import os
import subprocess
import threading
import time as _time
from ai.base import AIBase
from utils.logger import log
from core.config import WORKSPACE_DIR

class CLIProvider(AIBase):
    def __init__(self, name: str, backend: dict):
        self.name = name
        self.backend = backend

    def _build_env(self):
        env = os.environ.copy()
        extra_paths = [
            os.path.expanduser("~/.local/bin"),
            os.path.expanduser("~/bin"),
            "/usr/local/bin",
        ]
        nvm_dir = os.path.expanduser("~/.nvm/versions/node")
        if os.path.isdir(nvm_dir):
            for ver in sorted(os.listdir(nvm_dir), reverse=True):
                extra_paths.append(os.path.join(nvm_dir, ver, "bin"))
                break
        current_path = env.get("PATH", "")
        for p in extra_paths:
            if p not in current_path:
                current_path = p + os.pathsep + current_path
        env["PATH"] = current_path
        return env

    def call(self, prompt: str, progress_cb=None, timeout=None, progress_interval=120, **kwargs) -> str:
        try:
            env = self._build_env()
            cmd = [self.backend["cmd"]] + self.backend.get("args", []) + [prompt]
            cwd = WORKSPACE_DIR if WORKSPACE_DIR and os.path.isdir(WORKSPACE_DIR) else None
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                cwd=cwd,
            )

            stdout_lines, stderr_lines = [], []
            def _read(pipe, l):
                for line in pipe: l.append(line)

            t_out = threading.Thread(target=_read, args=(proc.stdout, stdout_lines), daemon=True)
            t_err = threading.Thread(target=_read, args=(proc.stderr, stderr_lines), daemon=True)
            t_out.start(); t_err.start()

            start = _time.time()
            last_progress = start
            while proc.poll() is None:
                _time.sleep(1)
                elapsed = _time.time() - start
                if timeout and elapsed > timeout:
                    proc.kill()
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        pass
                    # 关闭管道防止读线程永久阻塞
                    try:
                        if proc.stdout:
                            proc.stdout.close()
                        if proc.stderr:
                            proc.stderr.close()
                    except Exception:
                        pass
                    return f"AI 出错：执行超时（{int(timeout)} 秒）"
                if progress_cb and progress_interval > 0 and (elapsed - last_progress) >= progress_interval:
                    progress_cb(int(elapsed))
                    last_progress = _time.time()

            t_out.join(); t_err.join()
            return "".join(stdout_lines).strip() or f"Error: {''.join(stderr_lines[:5])}"
        except Exception as e:
            return f"AI 出错：{e}"
