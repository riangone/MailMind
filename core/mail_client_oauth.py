import os
import stat
import base64
from utils.logger import log

def _secure_write_token(token_file: str, content: str):
    """Write token file with restrictive permissions (owner read/write only)."""
    fd = os.open(token_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, stat.S_IRUSR | stat.S_IWUSR)
    try:
        os.write(fd, content.encode("utf-8"))
    finally:
        os.close(fd)

def _oauth_google(mailbox: dict) -> str:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    SCOPES = ["https://www.googleapis.com/auth/gmail.imap", "https://mail.google.com/"]
    token_file, creds_file = mailbox["oauth_token_file"], mailbox["oauth_creds_file"]
    creds = Credentials.from_authorized_user_file(token_file, SCOPES) if os.path.exists(token_file) else None
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
            auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
            print(f"\nGmail OAuth 授权链接：\n{auth_url}\n请输入 code:")
            flow.fetch_token(code=input(">>> ").strip())
            creds = flow.credentials
        _secure_write_token(token_file, creds.to_json())
    return creds.token

def _oauth_microsoft(mailbox: dict) -> str:
    import msal
    client_id, token_file = mailbox.get("oauth_client_id"), mailbox["oauth_token_file"]
    SCOPES = ["https://outlook.office.com/IMAP.AccessAsUser.All", "https://outlook.office.com/SMTP.Send", "offline_access"]
    cache = msal.SerializableTokenCache()
    if os.path.exists(token_file):
        cache.deserialize(open(token_file).read())
    app = msal.PublicClientApplication(client_id, authority="https://login.microsoftonline.com/common", token_cache=cache)
    accounts = app.get_accounts()
    result = app.acquire_token_silent(SCOPES, account=accounts[0]) if accounts else None
    if not result:
        flow = app.initiate_device_flow(scopes=SCOPES)
        print(f"\nOutlook OAuth 授权：{flow['verification_uri']} 代码：{flow['user_code']}")
        result = app.acquire_token_by_device_flow(flow)
    if cache.has_state_changed:
        _secure_write_token(token_file, cache.serialize())
    return result["access_token"]

def get_oauth_token(mailbox: dict) -> str:
    auth = mailbox.get("auth", "password")
    if auth == "oauth_google":
        return _oauth_google(mailbox)
    if auth == "oauth_microsoft":
        return _oauth_microsoft(mailbox)
    return ""
