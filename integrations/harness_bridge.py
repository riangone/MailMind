"""
integrations/harness_bridge.py — MailMind ↔ Harness 桥接

将 MailMind 的邮件指令转发到 Harness 的多 AI 管道执行，
并将结果返回给 MailMind 的邮件回复系统。
"""

import os
import sys
import subprocess
from typing import Optional, Dict, Any

from utils.logger import log


def _find_harness_webui() -> Optional[str]:
    """查找 Harness webui 目录路径"""
    candidates = []

    # 1. 环境变量优先
    env_path = os.environ.get("HARNESS_WEBUI_DIR") or os.environ.get("HARNESS_DIR")
    if env_path:
        candidates.append(env_path)

    # 2. 常见相对路径（MailMind 同级目录）
    mailmind_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    parent_dir = os.path.dirname(mailmind_dir)
    candidates.extend([
        os.path.join(parent_dir, "harness-new", "webui"),
        os.path.join(parent_dir, "harness", "webui"),
        os.path.join(mailmind_dir, "..", "harness-new", "webui"),
    ])

    # 3. 绝对路径 fallback
    candidates.extend([
        "/home/ubuntu/ws/harness-new/webui",
        "/opt/harness/webui",
    ])

    for path in candidates:
        real_path = os.path.realpath(path)
        if os.path.isdir(real_path) and os.path.isfile(os.path.join(real_path, "app", "pipeline_executor.py")):
            return real_path

    return None


def _get_harness_venv_python() -> str:
    """获取 Harness 虚拟环境的 Python 路径"""
    env_python = os.environ.get("HARNESS_VENV_PYTHON")
    if env_python and os.path.isfile(env_python):
        return env_python

    harness_dir = _find_harness_webui()
    if harness_dir:
        venv_python = os.path.join(harness_dir, "venv", "bin", "python3")
        if os.path.isfile(venv_python):
            return venv_python
        venv_python = os.path.join(harness_dir, "venv", "bin", "python")
        if os.path.isfile(venv_python):
            return venv_python

    # Fallback: 使用当前 Python
    return sys.executable


def run_harness_pipeline(
    prompt: str,
    work_dir: Optional[str] = None,
    pipeline_mode: str = "full",
    project_name: Optional[str] = None,
    timeout: Optional[int] = None,
) -> Dict[str, Any]:
    """
    调用 Harness 多 AI 管道。

    参数:
        prompt: 任务描述（自然语言）
        work_dir: 工作目录（可选）
        pipeline_mode: "full" (planner→generator→evaluator) 或 "single" (单 AI)
        project_name: 项目名称（可选）
        timeout: 超时秒数（可选）

    返回:
        {"status": "completed"|"failed", "output": "日志", "work_dir": "路径"}
    """
    harness_webui = _find_harness_webui()

    if not harness_webui:
        log.error("[Harness] ✗ 未找到 Harness webui 目录，请设置 HARNESS_WEBUI_DIR 环境变量")
        return {
            "status": "failed",
            "output": "⚠️ Harness 未配置。请设置 HARNESS_WEBUI_DIR 环境变量指向 Harness webui 目录。\n\n配置示例:\nHARNESS_WEBUI_DIR=/home/ubuntu/ws/harness-new/webui",
            "work_dir": work_dir or "",
        }

    log.info(f"[Harness] ✓ 找到 Harness: {harness_webui}")
    log.info(f"[Harness] 🚀 执行管道: mode={pipeline_mode}, prompt={prompt[:50]}...")

    try:
        venv_python = _get_harness_venv_python()
        log.info(f"[Harness] 使用 Python: {venv_python}")

        # 构建调用脚本
        script = f"""
import sys
sys.path.insert(0, '{harness_webui}')
from app.pipeline_executor import run_pipeline
import json

result = run_pipeline(
    prompt={repr(prompt)},
    work_dir={repr(work_dir)},
    pipeline_mode={repr(pipeline_mode)},
    project_name={repr(project_name)},
    timeout={repr(timeout)},
)
print(json.dumps(result, ensure_ascii=False))
"""

        proc = subprocess.run(
            [venv_python, "-c", script],
            capture_output=True,
            text=True,
            timeout=600,  # 脚本总超时 10 分钟
            cwd=harness_webui,
        )

        if proc.returncode != 0:
            log.error(f"[Harness] ✗ 执行失败 (exit {proc.returncode}): {proc.stderr[:500]}")
            return {
                "status": "failed",
                "output": f"⚠️ Harness 执行错误:\n\n{proc.stderr[:1000]}",
                "work_dir": work_dir or "",
            }

        # 解析 JSON 结果
        output = proc.stdout.strip()
        # 查找 JSON 块（可能前面有日志输出）
        json_start = output.rfind("{")
        if json_start == -1:
            return {
                "status": "failed",
                "output": f"⚠️ 无法解析 Harness 输出:\n\n{output[:1000]}",
                "work_dir": work_dir or "",
            }

        import json
        result = json.loads(output[json_start:])

        log.info(f"[Harness] ✓ 管道完成: status={result.get('status')}, work_dir={result.get('work_dir')}")
        return {
            "status": result.get("status", "failed"),
            "output": result.get("output", ""),
            "work_dir": result.get("work_dir", work_dir or ""),
        }

    except subprocess.TimeoutExpired:
        log.error("[Harness] ✗ 执行超时（10分钟）")
        return {
            "status": "failed",
            "output": "⚠️ Harness 执行超时（超过 10 分钟），任务已终止。",
            "work_dir": work_dir or "",
        }
    except Exception as e:
        log.error(f"[Harness] ✗ 桥接异常: {e}")
        return {
            "status": "failed",
            "output": f"⚠️ Harness 桥接错误:\n\n{str(e)}",
            "work_dir": work_dir or "",
        }
