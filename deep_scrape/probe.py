# -*- coding: utf-8 -*-
"""Lightweight upstream command probing.

Distinguishes the three failure modes that look identical to shutil.which():
  - missing: command not on PATH
  - broken: command exists but cannot execute — most commonly a stale venv
    shebang after a system Python upgrade (pipx/uv tool installs break this
    way: which() finds the shim, but exec fails with FileNotFoundError
    pointing at the shim itself)
  - timeout/error: command runs but misbehaves

Channels use probe_command() inside check() so doctor reports real health,
not just file existence.
"""

import shutil
import subprocess
from dataclasses import dataclass
from typing import Mapping, Optional, Sequence

from deep_scrape.utils.process import utf8_subprocess_env

#: Exit codes shells use for "found but not executable" / "not found".
_BROKEN_EXIT_CODES = (126, 127)


@dataclass
class ProbeResult:
    status: str  # "ok" | "missing" | "broken" | "timeout" | "error"
    output: str = ""
    hint: str = ""

    @property
    def ok(self) -> bool:
        return self.status == "ok"


def reinstall_hint(package: str) -> str:
    """Prescription for a broken (stale-venv) CLI install."""
    return (
        f"Command exists but failed to execute — typically due to missing venv interpreter after a Python upgrade. Reinstall to resolve:\n"
        f"  uv tool install --force {package}\n"
        f"or: pipx reinstall {package}"
    )


def probe_command(
    cmd: str,
    args: Sequence[str] = ("--version",),
    timeout: int = 10,
    retries: int = 0,
    package: Optional[str] = None,
    env: Optional[Mapping[str, str]] = None,
    remove_env: Sequence[str] = (),
) -> ProbeResult:
    """Actually execute `cmd *args` and classify the result.

    Intended for SIDE-EFFECT-FREE health probes only (version/status
    commands): retries re-run the command verbatim with no backoff, so a
    non-idempotent command would repeat its effect.

    package: pip/pipx package name used in the broken-install hint
             (defaults to cmd).
    env: values added only to the probed child process.
    remove_env: inherited variables removed only from the child process.
    """
    path = shutil.which(cmd)
    if not path:
        return ProbeResult("missing")

    last: Optional[ProbeResult] = None
    for _ in range(retries + 1):
        last = _run_once(path, args, timeout, package or cmd, env, remove_env)
        if last.ok:
            return last
        # missing/broken won't heal between retries — only transient
        # failures (timeout/error) are worth a second attempt
        if last.status in ("missing", "broken"):
            return last
    assert last is not None  # retries + 1 always executes at least once
    return last


def _run_once(
    path: str,
    args: Sequence[str],
    timeout: int,
    package: str,
    env: Optional[Mapping[str, str]] = None,
    remove_env: Sequence[str] = (),
) -> ProbeResult:
    try:
        subprocess_env = utf8_subprocess_env()
        for key in remove_env:
            subprocess_env.pop(key, None)
        if env:
            subprocess_env.update(env)
        r = subprocess.run(
            [path, *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            env=subprocess_env,
        )
        if r.returncode == 0:
            return ProbeResult("ok", output=r.stdout.strip())
        if r.returncode in _BROKEN_EXIT_CODES:
            return ProbeResult("broken", output=r.stderr.strip(), hint=reinstall_hint(package))
        return ProbeResult("error", output=(r.stderr or r.stdout).strip())
    except FileNotFoundError:
        # On Windows/POSIX when the shebang interpreter is missing, exec
        # raises FileNotFoundError even though which() found `path`.
        return ProbeResult("broken", hint=reinstall_hint(package))
    except subprocess.TimeoutExpired:
        return ProbeResult("timeout")
    except OSError as e:
        return ProbeResult("broken", output=str(e), hint=reinstall_hint(package))
