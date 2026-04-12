"""
tasks/registry.py - 定时任务执行逻辑

增强版：集成通用 AI 执行框架和技能系统
"""
from typing import Optional, Dict, Any
from core.config import AI_BACKENDS, DEFAULT_TASK_AI, PROMPT_LANG, AI_CLI_TIMEOUT, AI_PROGRESS_INTERVAL
from ai.providers import get_ai_provider
from utils.logger import log


def pick_task_ai(task_payload: Optional[dict] = None):
    """选择一个可用的 AI 后端（CLI 优先，然后 API）"""
    import os, shutil
    task_payload = task_payload or {}

    # 优先从环境变量获取，确保实时性
    env_default = os.environ.get("TASK_DEFAULT_AI") or DEFAULT_TASK_AI
    ai_name = task_payload.get("ai_name") or env_default

    log.info(f"[Tasks] pick_task_ai: ai_name={ai_name!r}, env_default={env_default!r}")

    if ai_name and ai_name in AI_BACKENDS:
        # 检查如果是 CLI 类型，命令是否可用
        backend = AI_BACKENDS[ai_name]
        if backend.get("type") == "cli":
            cmd = backend.get("cmd", "")
            if cmd and (shutil.which(cmd) or os.path.isfile(cmd)):
                log.info(f"[Tasks] ✓ 使用指定的 CLI AI: {ai_name}")
                return ai_name, backend
            else:
                log.warning(f"[Tasks] ✗ 指定的 CLI AI {ai_name} 不可用 (cmd={cmd!r})，回退到动态选择")
        else:
            # API 类型直接返回
            log.info(f"[Tasks] ✓ 使用指定的 API AI: {ai_name}")
            return ai_name, backend
    elif ai_name:
        log.warning(f"[Tasks] ✗ 指定的 AI {ai_name!r} 不在 AI_BACKENDS 中，回退到动态选择")

    # 动态选择：CLI 优先（过滤掉不可用的）
    cli_candidates = []
    api_candidates = []
    for name, b in AI_BACKENDS.items():
        if b.get("type") == "cli":
            cmd = b.get("cmd", "")
            if cmd and (shutil.which(cmd) or os.path.isfile(cmd)):
                cli_candidates.append(name)
        elif b.get("api_key"):
            api_candidates.append(name)

    # 优先级：1. 原本指定的（如果可用） 2. 其他 CLI 3. API
    candidates = cli_candidates + api_candidates
    if not candidates:
        selected = list(AI_BACKENDS.keys())[0]
        log.warning(f"[Tasks] ⚠ 没有可用的 AI 后端，使用默认: {selected}")
    else:
        # 优先使用环境变量指定的 AI，否则使用第一个可用的候选
        if env_default in candidates:
            selected = env_default
            log.info(f"[Tasks] ✓ 使用环境变量指定的 AI: {selected}")
        else:
            selected = candidates[0]
            log.info(f"[Tasks] ⚠ 环境变量指定的 AI {env_default!r} 不可用，使用第一个候选: {selected}")

    log.info(f"[Tasks] 动态选择 AI 后端: {selected} (CLI: {cli_candidates}, API: {api_candidates})")
    return selected, AI_BACKENDS.get(selected)


def _handle_task_manage(payload: Optional[dict], subject: str, lang: str = "zh") -> str:
    """处理任务管理请求（查看/取消/暂停/恢复/删除）"""
    from tasks.scheduler import scheduler

    payload = payload or {}
    action = payload.get("action", "list")
    task_id = payload.get("task_id")
    filt = payload.get("filter", {})

    def _t(zh: str, ja: str, en: str, ko: str) -> str:
        return {"zh": zh, "ja": ja, "en": en, "ko": ko}.get(lang, zh)

    if action == "list":
        tasks = scheduler.list_tasks(
            status_filter=filt.get("status"),
            type_filter=filt.get("type"),
            subject_filter=filt.get("subject"),
        )
        if not tasks:
            return _t("当前没有活跃的定时任务。", "アクティブな定期タスクはありません。", "No active scheduled tasks.", "현재 활성화된 정기 작업이 없습니다.")

        header = _t(f"当前有 {len(tasks)} 个任务：", f"アクティブなタスク：{len(tasks)} 件", f"Active tasks: {len(tasks)}", f"활성 작업: {len(tasks)}개")
        rows = []
        for t in tasks:
            status_icon = {"pending": "⏳", "paused": "⏸️", "cancelled": "❌", "completed": "✅", "failed": "⚠️", "processing": "🔄"}.get(t.get("status", ""), "❓")
            next_run = ""
            if t.get("trigger_time"):
                from datetime import datetime
                try:
                    next_run = datetime.fromtimestamp(t["trigger_time"]).strftime("%Y-%m-%d %H:%M")
                except Exception:
                    pass
            repeat = ""
            if t.get("cron_expr"):
                repeat = f"cron:{t['cron_expr']}"
            elif t.get("interval_seconds"):
                secs = t["interval_seconds"]
                if secs >= 86400: repeat = f"每{secs//86400}天"
                elif secs >= 3600: repeat = f"每{secs//3600}时"
                elif secs >= 60: repeat = f"每{secs//60}分"
                else: repeat = f"每{secs}秒"
            rows.append(f"[ID:{t['id']}] {status_icon} {t.get('subject','')[:40]}\n  下次:{next_run or '-'}  {repeat}")

        hint = _t(
            "\n\n回复「取消任务 ID:N」「暂停任务 ID:N」「恢复任务 ID:N」「删除任务 ID:N」进行管理。",
            "\n\n「タスクキャンセル ID:N」「一時停止 ID:N」「再開 ID:N」「削除 ID:N」と返信して管理できます。",
            "\n\nReply 'cancel task ID:N', 'pause task ID:N', 'resume task ID:N', or 'delete task ID:N' to manage.",
            "\n\n'작업 취소 ID:N', '작업 일시정지 ID:N', '작업 재개 ID:N', '작업 삭제 ID:N'으로 관리할 수 있습니다."
        )
        return header + "\n\n" + "\n\n".join(rows) + hint

    if action in ("cancel", "pause", "resume", "delete"):
        if task_id:
            task_id = int(task_id)
            ok = {
                "cancel": scheduler.cancel_task,
                "pause":  scheduler.pause_task,
                "resume": scheduler.resume_task,
                "delete": scheduler.delete_task,
            }[action](task_id)
            verb = {
                "cancel": ("取消", "キャンセル", "cancelled", "취소됨"),
                "pause":  ("暂停", "一時停止", "paused", "일시정지됨"),
                "resume": ("恢复", "再開", "resumed", "재개됨"),
                "delete": ("删除", "削除", "deleted", "삭제됨"),
            }[action]
            if ok:
                return _t(f"✅ 已{verb[0]}任务 ID:{task_id}。", f"✅ タスク ID:{task_id} を{verb[1]}しました。", f"✅ Task ID:{task_id} {verb[2]}.", f"✅ 작업 ID:{task_id} {verb[3]}.")
            else:
                return _t(f"⚠️ 未找到可{verb[0]}的任务 ID:{task_id}。", f"⚠️ タスク ID:{task_id} は{verb[1]}できませんでした。", f"⚠️ Task ID:{task_id} could not be {verb[2]}.", f"⚠️ 작업 ID:{task_id} {verb[3]}할 수 없습니다.")
        else:
            if action == "cancel":
                count = scheduler.cancel_tasks_by_filter(filt.get("type"), filt.get("subject"))
                return _t(f"✅ 已取消 {count} 个匹配的任务。", f"✅ {count} 件のタスクをキャンセルしました。", f"✅ Cancelled {count} matching tasks.", f"✅ 일치하는 작업 {count}개를 취소했습니다.")
            return _t("⚠️ 批量操作仅支持取消。", "⚠️ 一括操作はキャンセルのみ対応です。", "⚠️ Batch operation only supports cancel.", "⚠️ 일괄 작업은 취소만 지원합니다.")

    return _t(f"⚠️ 未知操作：{action}", f"⚠️ 不明な操作：{action}", f"⚠️ Unknown action: {action}", f"⚠️ 알 수 없는 작업: {action}")


def execute_task_logic(task: Dict[str, Any], lang: str = "zh", progress_cb=None) -> tuple:
    """
    执行定时任务逻辑

    增强版：
    1. 集成通用 AI 执行框架
    2. 支持技能链式调用
    3. 自动执行模式（无需确认）
    """
    task_type = (task.get("type") or "email").lower()
    payload = task.get("payload") or {}
    subject = task.get("subject") or "定时任务结果"
    body = task.get("body") or ""

    def _t(zh: str, ja: str, en: str, ko: str) -> str:
        return {"zh": zh, "ja": ja, "en": en, "ko": ko}.get(lang, zh)

    # 1. 任务管理
    if task_type == "task_manage":
        body = _handle_task_manage(payload, subject, lang)
        subject = subject or _t("任务管理结果", "タスク管理結果", "Task management result", "작업 관리 결과")

    # 2. MCP 工具调用
    elif task_type == "mcp_call":
        from utils.mcp_client import call_mcp_tool, list_mcp_tools
        server = payload.get("server", "")
        tool = payload.get("tool", "")
        args = payload.get("args") or {}
        if tool == "__list__":
            body = list_mcp_tools(server)
        else:
            body = call_mcp_tool(server, tool, args)
        subject = subject or f"MCP: {server}/{tool}"

    # 3. email_manage 不支持定时执行
    elif task_type == "email_manage":
        body = _t("⚠️ email_manage 仅支持即时执行。", "⚠️ email_manage は即時実行のみ対応です。", "⚠️ email_manage only supports immediate execution.", "⚠️ email_manage 는 즉시 실행만 지원합니다.")

    # 4. ai_skill 类型：从 payload.skill 获取技能名
    elif task_type == "ai_skill":
        skill_name = payload.get("skill") or payload.get("query", "")
        if not skill_name:
            body = _t("⚠️ ai_skill 任务缺少 skill 参数。", "⚠️ ai_skill タスクに skill パラメータがありません。", "⚠️ ai_skill task missing skill parameter.", "⚠️ ai_skill 작업에 skill 매개변수가 없습니다.")
        else:
            from skills.loader import get_skill as load_skill

            # 获取嵌套的 payload 参数（payload.payload）
            skill_payload = payload.get("payload") or {}
            # 添加语言参数
            if "lang" not in skill_payload:
                skill_payload["lang"] = lang
            # 添加 query 参数（如果 payload 中有）
            if "query" in payload and "query" not in skill_payload:
                skill_payload["query"] = payload["query"]

            skill = load_skill(skill_name)
            if skill:
                log.info(f"🚀 执行技能 (ai_skill): {skill_name}")
                ai_name, backend = pick_task_ai(skill_payload)
                ai = get_ai_provider(ai_name, backend)
                body = skill.run(skill_payload, ai_caller=ai)
                subject = subject or f"Skill: {skill_name}"
            else:
                body = _t(f"⚠️ 未找到技能：{skill_name}", f"⚠️ スキックが見つかりません：{skill_name}", f"⚠️ Skill not found: {skill_name}", f"⚠️ 스킬을 찾을 수 없습니다: {skill_name}")
        return subject, body

    # 5. 尝试执行已注册的技能（直接通过 task_type 匹配技能名）
    from skills.loader import get_skill

    # 映射逻辑：将 news/stock 映射到对应技能以统一格式
    effective_task_type = task_type
    if task_type == "news":
        effective_task_type = "news_briefing"
    # stock 类型直接对应 stock 技能，不需要额外映射

    skill = get_skill(effective_task_type)
    if skill:
        log.info(f"🚀 执行技能: {effective_task_type}")

        # 准备技能参数：优先使用 payload 里的字段，如果 payload 缺少 query 但有 body，把 body 当 query
        skill_payload = payload.copy()
        if "query" not in skill_payload and body:
            skill_payload["query"] = body
        if "prompt" not in skill_payload and body:
            skill_payload["prompt"] = body
        
        # 重要：传递语言参数，确保技能使用正确的语言输出
        if "lang" not in skill_payload:
            skill_payload["lang"] = lang

        # 验证 payload
        is_valid, error_msg = skill.validate_payload(skill_payload)
        if not is_valid:
            body = f"⚠️ 参数验证失败: {error_msg}"
        else:
            ai_name, backend = pick_task_ai(skill_payload)
            ai = get_ai_provider(ai_name, backend)
            # skill.run 会渲染指令并调用 AI
            body = skill.run(skill_payload, ai_caller=ai)
        
        subject = subject or f"Skill: {effective_task_type}"
        return subject, body

    # 5. pipeline: 调用 Harness 多 AI 管道
    elif task_type == "pipeline":
        from integrations.harness_bridge import run_harness_pipeline
        harness_prompt = payload.get("prompt") or body or subject
        pipeline_mode = payload.get("mode", "full")  # "full" 或 "single"
        work_dir = payload.get("work_dir")  # 可选
        timeout = payload.get("timeout")  # 可选

        if not harness_prompt:
            body = _t("⚠️ pipeline 任务缺少 prompt 参数。", "⚠️ pipeline タスクに prompt パラメータがありません。", "⚠️ pipeline task missing prompt parameter.", "⚠️ pipeline 작업에 prompt 매개변수가 없습니다.")
        else:
            result = run_harness_pipeline(
                prompt=harness_prompt,
                work_dir=work_dir,
                pipeline_mode=pipeline_mode,
                timeout=timeout,
            )
            if result["status"] == "completed":
                body = result["output"]
                subject = subject or f"✅ Pipeline: {harness_prompt[:30]}"
            else:
                body = f"❌ Pipeline 执行失败:\n\n{result['output']}"
                subject = subject or f"❌ Pipeline Failed: {harness_prompt[:30]}"
        return subject, body

    # 6. 其他所有任务：使用增强版 AI 执行框架
    else:
        ai_name, backend = pick_task_ai(payload)
        ai = get_ai_provider(ai_name, backend)

        # 构建 prompt：包含原始指令和上下文
        prompt = body or subject
        if task_type and task_type not in ("email", "ai_job"):
            # 根据语言翻译前缀
            type_prefix = {
                "zh": f"请执行以下{task_type}任务：",
                "ja": f"以下の{task_type}タスクを実行してください：",
                "en": f"Please execute the following {task_type} task: ",
                "ko": f"다음 {task_type} 작업을 수행하십시오: ",
            }.get(lang, f"Please execute the following {task_type} task: ")
            prompt = f"{type_prefix}{prompt}"

        # 注入技能列表（让 AI 知道可用工具）
        from skills import get_all_skills_prompt
        skills_hint = get_all_skills_prompt(lang)
        if skills_hint:
            prompt = f"{prompt}\n\n{skills_hint}"

        # 添加强制执行指令
        exec_instruction = {
            "zh": """
【重要执行指令 — 自动任务模式】
这是一个自动执行任务，请严格遵守：
1. **禁止探索文件系统**：不要列出目录、不要搜索文件、不要查看项目结构
2. **禁止创建/修改定时任务或项目文件**：除非任务明确要求，否则不要新建/修改任务、脚本或配置
3. **直接执行任务**：根据任务要求搜索网页/获取数据/处理信息
4. **直接输出最终结果**：不要输出中间步骤、不要输出工具调用过程
5. **不要询问确认**：自动完成所有步骤
6. **只返回任务结果**：只返回用户需要的信息（如新闻摘要、天气信息、股票数据等）
7. **必须使用中文（简体）回复所有内容**
""",
            "ja": """
【重要実行指示 — 自動タスクモード】
これは自動実行タスクです。以下のルールを厳守してください：
1. **ファイルシステムの探索を禁止**：ディレクトリ一覧、ファイル検索、プロジェクト構造の確認は一切不要
2. **定時タスクやプロジェクトファイルの作成・変更を禁止**：タスクが明示的に要求しない限り、タスク/スクリプト/設定を作成・変更しない
3. **直接タスクを実行**：タスクに応じてウェブ検索/データ取得/情報処理を直接実行
4. **最終結果のみを出力**：中間ステップやツール呼び出しの過程は一切出力しない
5. **確認不要**：すべてのステップを自動完了
6. **タスク結果のみを返す**：ユーザーが必要とする情報（ニュース要約、天気情報、株式データなど）のみを返す
7. **すべての回答内容を日本語で行ってください**
""",
            "en": """
[IMPORTANT EXECUTION INSTRUCTION — AUTO TASK MODE]
This is an auto-execution task. Strictly follow these rules:
1. **DO NOT explore the filesystem**: No directory listing, no file search, no project structure check
2. **Do NOT create/modify scheduled tasks or project files**: Unless explicitly required by the task, do not create or change tasks, scripts, or configs
3. **Execute the task directly**: Search web/fetch data/process info as required by the task
4. **Output ONLY the final result**: No intermediate steps, no tool call process
5. **Do NOT ask for confirmation**: Complete all steps automatically
6. **Return ONLY the task result**: Only return information the user needs (news summary, weather info, stock data, etc.)
7. **YOU MUST RESPOND ENTIRELY IN ENGLISH**
""",
            "ko": """
[중요 실행 지침 — 자동 작업 모드]
이것은 자동 실행 작업입니다. 다음 규칙을 엄수하세요:
1. **파일 시스템 탐색 금지**: 디렉토리 목록, 파일 검색, 프로젝트 구조 확인 일절 불가
2. **예약 작업/프로젝트 파일 생성·수정 금지**: 작업이 명시적으로 요구하지 않는 한 태스크/스크립트/설정을 생성·수정하지 마십시오
3. **작업 직접 실행**: 작업에 따라 웹 검색/데이터 수집/정보 처리를 직접 실행
4. **최종 결과만 출력**: 중간 단계나 도구 호출 과정 일절 출력 금지
5. **확인 불요**: 모든 단계 자동 완료
6. **작업 결과만 반환**: 사용자에게 필요한 정보(뉴스 요약, 날씨 정보, 주식 데이터 등)만 반환
7. **모든 답변은 반드시 한국어로 작성하십시오**
""",
        }
        
        # 将语言指令放在最后，具有最高优先级
        prompt = f"{prompt}\n\n{exec_instruction.get(lang, exec_instruction['zh'])}"

        # 调用 AI（使用 execute_task 模式，而非普通 call）

        # 调用 AI（使用 execute_task 模式，而非普通 call）
        log.info(f"⚡ 定时任务调用 AI: {ai_name} | 类型：{task_type}")
        
        # 检查 AI 是否有 execute_task 方法（CLI Provider 没有，所以会走 else 分支）
        if hasattr(ai, 'execute_task'):
            # 使用任务执行模式（非交互式）
            is_cli = (backend or {}).get("type") == "cli"
            if is_cli and progress_cb and AI_PROGRESS_INTERVAL > 0:
                body = ai.execute_task(prompt, progress_cb=progress_cb, timeout=AI_CLI_TIMEOUT)
            else:
                body = ai.execute_task(prompt, timeout=AI_CLI_TIMEOUT)
        else:
            # CLI 和 API Provider 都使用 call()，必须传递 timeout
            if progress_cb and AI_PROGRESS_INTERVAL > 0:
                body = ai.call(prompt, progress_cb=progress_cb, timeout=AI_CLI_TIMEOUT, progress_interval=AI_PROGRESS_INTERVAL)
            else:
                body = ai.call(prompt, timeout=AI_CLI_TIMEOUT)
        
        body = body or _t("⚠️ AI 处理失败", "⚠️ AI 処理に失敗しました", "⚠️ AI processing failed", "⚠️ AI 처리 실패")
        subject = subject or f"AI: {task_type or 'task'}"

    return subject, body
