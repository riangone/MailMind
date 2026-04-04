import imaplib
import email
import os
import re
import time
import base64
from email.header import decode_header as _decode_header, Header
from email.utils import parseaddr, formatdate
from email.mime.text import MIMEText
from core.config import MAILBOXES, ATTACHMENT_MAX_SIZE_MB, CONTEXT_MAX_DEPTH
from core.prompts import TEMPLATES, FOLDER_NAMES
from utils.logger import log

# ────────────────────────────────────────────────────────────────
# 核心 IMAP 工具函数
# ────────────────────────────────────────────────────────────────

def decode_str(s: str) -> str:
    if not s: return ""
    result = []
    for part, charset in _decode_header(s):
        if isinstance(part, bytes):
            result.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            result.append(str(part))
    return "".join(result)

def get_body_and_attachments(msg) -> tuple:
    max_bytes = ATTACHMENT_MAX_SIZE_MB * 1024 * 1024
    body, attachments = "", []
    if msg.is_multipart():
        for part in msg.walk():
            disposition = str(part.get_content_disposition() or "")
            if "attachment" in disposition:
                payload = part.get_payload(decode=True)
                if payload:
                    if len(payload) > max_bytes:
                        filename = decode_str(part.get_filename() or "untitled")
                        log.warning(f"附件 '{filename}' 超出大小限制")
                        continue
                    is_text = part.get_content_type().startswith("text/")
                    content = payload.decode(part.get_content_charset() or "utf-8", errors="replace") if is_text else payload
                    attachments.append({"filename": decode_str(part.get_filename() or "untitled"), "content": content, "is_text": is_text})
            elif part.get_content_type() == "text/plain" and not body and "attachment" not in disposition:
                payload = part.get_payload(decode=True)
                if payload:
                    body = payload.decode(msg.get_content_charset() or "utf-8", errors="replace").strip()
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            body = payload.decode(msg.get_content_charset() or "utf-8", errors="replace").strip()
    return body, attachments

def imap_login(mailbox: dict):
    mail = imaplib.IMAP4_SSL(mailbox["imap_server"], mailbox["imap_port"], timeout=15)
    if mailbox.get("imap_id"):
        try:
            mail.xatom("ID", '("name" "mailmind" "version" "1.0")')
        except Exception:
            pass
    auth = mailbox.get("auth", "password")
    if auth == "password":
        mail.login(mailbox["address"], mailbox["password"])
    else:
        from core.mail_client_oauth import get_oauth_token # 假设拆分了 OAuth
        token = get_oauth_token(mailbox)
        mail.authenticate("XOAUTH2", lambda x: base64.b64encode(f"user={mailbox['address']}\x01auth=Bearer {token}\x01\x01".encode()).decode())
    return mail

def get_archive_folder(mailbox: dict) -> str:
    imap_server = mailbox.get("imap_server", "").lower()
    if "gmail" in imap_server:
        return mailbox.get("archive_folder") or "[Gmail]/All Mail"
    return mailbox.get("archive_folder") or "Archive"

def imap_move_messages(mail, uid_list: list, target_folder: str) -> int:
    if not uid_list: return 0
    success = 0
    try: mail.create(target_folder)
    except Exception: pass
    for uid in uid_list:
        try:
            rv, _ = mail.uid("copy", uid, target_folder)
            if rv == "OK":
                mail.uid("store", uid, "+FLAGS", "\\Deleted")
                success += 1
        except Exception as e:
            log.warning(f"移动 uid={uid} 失败: {e}")
    mail.expunge()
    return success

def imap_archive_messages(mail, uid_list: list, mailbox: dict) -> int:
    return imap_move_messages(mail, uid_list, get_archive_folder(mailbox))

def push_templates_to_mailbox(mailbox: dict, lang: str = "zh") -> int:
    templates = TEMPLATES.get(lang, TEMPLATES["zh"])
    folder = FOLDER_NAMES.get(lang, "MailMindHub_Templates")
    mail = imap_login(mailbox)
    try:
        mail.create(folder)
        status, _ = mail.select(folder)
        if status == "OK":
            _, ids = mail.search(None, "ALL")
            for mid in ids[0].split():
                mail.store(mid, "+FLAGS", "\\Deleted")
            mail.expunge()
        count = 0
        for subject, body in templates:
            msg = MIMEText(body, "plain", "utf-8")
            msg["From"] = mailbox["address"]
            msg["To"] = mailbox["address"]
            msg["Subject"] = Header(subject, "utf-8")
            msg["Date"] = formatdate(localtime=True)
            if mail.append(folder, "(\\Seen)", imaplib.Time2Internaldate(time.time()), msg.as_bytes())[0] == "OK":
                count += 1
        return count
    finally:
        mail.logout()

def fetch_unread_emails(mailbox: dict, processed_ids: set):
    mail = imap_login(mailbox)
    emails = []
    try:
        status, _ = mail.select("INBOX")
        if status != "OK": return []
        _, ids = mail.uid("search", None, "UNSEEN")
        for uid in ids[0].split():
            eid = uid.decode()
            if eid in processed_ids: continue
            _, data = mail.uid("fetch", uid, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])
            body, atts = get_body_and_attachments(msg)
            emails.append({
                "id": eid, 
                "from": decode_str(msg.get("From", "")),
                "subject": decode_str(msg.get("Subject", "(无主题)")),
                "message_id": msg.get("Message-ID", ""),
                "body": body, 
                "attachments": atts
            })
    finally:
        mail.logout()
    return emails

def fetch_thread_context(mailbox: dict, references: str, in_reply_to: str = "", max_depth: int = 5) -> str:
    # 简化后的上下文获取逻辑
    ref_ids = [mid.strip() for mid in (references or "").split() if mid.strip()]
    if in_reply_to: ref_ids.append(in_reply_to.strip())
    if not ref_ids: return ""
    
    mail = imap_login(mailbox)
    results = []
    try:
        for folder in ["INBOX", "Sent", '"[Gmail]/Sent Mail"']:
            mail.select(folder, readonly=True)
            for mid in ref_ids[-max_depth:]:
                _, data = mail.search(None, f'HEADER Message-ID "{mid}"')
                for msg_id in data[0].split():
                    _, msg_data = mail.fetch(msg_id, "(RFC822)")
                    body, _ = get_body_and_attachments(email.message_from_bytes(msg_data[0][1]))
                    if body: results.append(body)
    finally:
        mail.logout()
    return "\n\n---\n\n".join(results)
