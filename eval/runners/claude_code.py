"""Claude Code runner -- invokes skills via `claude --print`."""

import json
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Callable, Optional

from .base import EvalRunner, RunResult

# Shared lock for printing — prevents interleaved output across threads
_print_lock = threading.Lock()


class ClaudeCodeRunner(EvalRunner):
    """Runs skills using the Claude Code CLI in non-interactive mode."""

    @property
    def name(self) -> str:
        return "claude-code"

    def run_skill(
        self,
        skill_name: str,
        args: str,
        workspace: Path,
        model: str,
        settings_path: Optional[Path] = None,
        system_prompt: Optional[str] = None,
        max_budget_usd: float = 5.0,
        timeout_s: int = 600,
        log_prefix: Optional[str] = None,
    ) -> RunResult:
        cmd = [
            "claude",
            "--print",
            "--model", model,
            "--output-format", "stream-json" if log_prefix else "json",
            "--max-budget-usd", str(max_budget_usd),
            "--no-session-persistence",
        ]
        if log_prefix:
            cmd.append("--verbose")

        if settings_path:
            cmd.extend(["--settings", str(settings_path)])

        if system_prompt:
            cmd.extend(["--append-system-prompt", system_prompt])

        # Block all Jira/MCP write tools
        cmd.extend(["--disallowed-tools", "mcp__atlassian__*"])

        # Build the skill invocation prompt (passed via stdin)
        prompt = f"/{skill_name}"
        if args:
            prompt += f" {args}"

        start = time.monotonic()
        stdout_lines = []

        try:
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(workspace),
                text=True,
                env=_clean_env(),
            )

            # Send prompt via stdin and close it
            proc.stdin.write(prompt)
            proc.stdin.close()

            # Read stdout line by line — stream-json gives us JSONL
            # Print progress events if log_prefix is set
            result_obj = None
            for line in proc.stdout:
                line = line.rstrip("\n")
                stdout_lines.append(line)
                if not line.strip():
                    continue
                if log_prefix:
                    try:
                        obj = json.loads(line)
                        msg = _extract_progress(obj)
                        if msg:
                            with _print_lock:
                                print(f"  {log_prefix} | {msg}", flush=True)
                        # Keep the last result object
                        if obj.get("type") == "result":
                            result_obj = obj
                    except json.JSONDecodeError:
                        pass

            stderr = proc.stderr.read()
            proc.wait(timeout=30)

        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
            duration = time.monotonic() - start
            return RunResult(
                exit_code=-1,
                stdout="\n".join(stdout_lines),
                stderr=f"Timed out after {timeout_s}s",
                duration_s=duration,
            )
        except Exception as e:
            duration = time.monotonic() - start
            return RunResult(
                exit_code=-1,
                stdout="",
                stderr=str(e),
                duration_s=duration,
            )

        duration = time.monotonic() - start
        stdout_text = "\n".join(stdout_lines)

        # Extract usage from result object or parse stdout
        token_usage = None
        cost_usd = None
        raw_output = result_obj

        if not result_obj and stdout_text.strip():
            # Fallback: try parsing as single JSON (non-stream mode)
            try:
                result_obj = json.loads(stdout_text)
                raw_output = result_obj
            except json.JSONDecodeError:
                pass

        if isinstance(result_obj, dict):
            usage = result_obj.get("usage", {})
            if usage:
                token_usage = {
                    "input": usage.get("input_tokens", 0),
                    "output": usage.get("output_tokens", 0),
                }
            cost_usd = result_obj.get("total_cost_usd")

        return RunResult(
            exit_code=proc.returncode,
            stdout=stdout_text,
            stderr=stderr or "",
            duration_s=duration,
            token_usage=token_usage,
            cost_usd=cost_usd,
            raw_output=raw_output,
        )


def _extract_progress(obj: dict) -> str:
    """Extract a human-readable progress message from a stream-json event."""
    t = obj.get("type")

    if t == "assistant":
        # Tool use events show what the agent is doing
        msg = obj.get("message", {})
        for block in msg.get("content", []):
            if block.get("type") == "tool_use":
                tool = block.get("name", "")
                # Summarize the tool call
                inp = block.get("input", {})
                if tool == "Skill":
                    return f"Invoking /{inp.get('skill', '?')}"
                elif tool == "Bash":
                    cmd = inp.get("command", "")[:60]
                    return f"Running: {cmd}"
                elif tool in ("Write", "Edit"):
                    path = inp.get("file_path", "")
                    return f"{tool}: {path.split('/')[-1] if path else '?'}"
                elif tool == "Read":
                    path = inp.get("file_path", "")
                    return f"Reading: {path.split('/')[-1] if path else '?'}"
                else:
                    return f"Tool: {tool}"
            elif block.get("type") == "text":
                text = block.get("text", "").strip()
                if text and len(text) < 100:
                    return text
    elif t == "result":
        cost = obj.get("total_cost_usd", 0)
        turns = obj.get("num_turns", 0)
        return f"Done ({turns} turns, ${cost:.2f})"

    return ""


def _clean_env():
    """Return env dict without Jira credentials to prevent accidental writes."""
    import os
    env = os.environ.copy()
    for key in ("JIRA_SERVER", "JIRA_USER", "JIRA_TOKEN"):
        env.pop(key, None)
    return env
