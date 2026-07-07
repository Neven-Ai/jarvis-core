#!/usr/bin/env python3
"""Validate .agents/ memory layout and basic hygiene."""

from datetime import datetime, timedelta
from pathlib import Path
import re
import sys

MEMORY_FILES = (
    "PROJECT_STATE.md",
    "WORKLOG.md",
    "BUGS.md",
    "TODO.md",
    "ACTIVE_WORK.md",
    "DECISIONS.md",
)

AUTO_DISCOVERY_FILES = (
    "AGENTS.md",
    ".github/copilot-instructions.md",
    "CLAUDE.md",
    ".agents/AGENTS.md",
)

AUTONOMY_MARKERS = (
    "autonomo",
    "automaticamente",
    "senza che l'utente",
    "primo turno",
    "stesso turno",
)

INIT_WORKLOG_RE = re.compile(
    r"^## \[\d{4}-\d{2}-\d{2}\] Init memoria progetto \(script: init_project_memory\.sh\)",
    re.MULTILINE,
)

CLAIM_RE = re.compile(
    r"^- \[\d{4}-\d{2}-\d{2} \d{2}:\d{2}\] \*\*.+\*\* — .+ — branch `.+` — scade \d{4}-\d{2}-\d{2} \d{2}:\d{2}\s*$"
)
UPDATED_RE = re.compile(r"Ultimo aggiornamento[:\s*]+(\d{4}-\d{2}-\d{2})", re.IGNORECASE)
SESSION_HEADER_RE = re.compile(r"^## \[\d{4}-\d{2}-\d{2}\]", re.MULTILINE)


def has_autonomy_markers(text: str) -> bool:
    """Return whether text contains the expected autonomy guidance markers."""
    lower = text.lower()
    return any(m in lower for m in AUTONOMY_MARKERS)


def is_fresh_install(worklog_text: str, has_session_summary: bool) -> bool:
    """Return whether the memory looks like a fresh initialization."""
    entries = SESSION_HEADER_RE.findall(worklog_text)
    if not entries:
        return True
    if len(entries) == 1 and INIT_WORKLOG_RE.search(worklog_text):
        return True
    return not has_session_summary and len(entries) <= 1


def main() -> int:
    """Run validation checks and return a process exit code."""
    root = Path(__file__).resolve().parents[2]
    agents = root / ".agents"
    memory = agents / "memory"
    errors: list[str] = []
    warnings: list[str] = []
    notes: list[str] = []

    if not agents.is_dir():
        errors.append("Missing .agents/ directory")
        _report(errors, warnings, notes)
        return 1

    for name in MEMORY_FILES:
        path = memory / name
        if not path.is_file():
            errors.append(f"Missing {path.relative_to(root)}")

    sessions = agents / "sessions" / "SESSION_SUMMARY.md"
    has_session_summary = sessions.is_file()
    if not has_session_summary:
        notes.append("Nessun checkpoint ancora (.agents/sessions/SESSION_SUMMARY.md) — atteso su progetto nuovo")

    skill = agents / "skills" / "collaborative-project-memory" / "SKILL.md"
    if not skill.is_file():
        errors.append("Missing unified skill at .agents/skills/collaborative-project-memory/SKILL.md")
    else:
        skill_text = skill.read_text(encoding="utf-8")
        if not has_autonomy_markers(skill_text):
            warnings.append("SKILL.md senza istruzioni di comportamento autonomo esplicite")

    agents_md = root / "AGENTS.md"
    if not agents_md.is_file():
        errors.append("Missing AGENTS.md in repo root (required for auto-discovery)")
    else:
        agents_text = agents_md.read_text(encoding="utf-8")
        if not has_autonomy_markers(agents_text):
            warnings.append(
                "AGENTS.md senza sezione comportamento autonomo — "
                "esegui: .agents/scripts/init_project_memory.sh --merge-agents"
            )

    discovery_present = [p for p in AUTO_DISCOVERY_FILES if (root / p).is_file()]
    if len(discovery_present) < 2:
        warnings.append(
            "Pochi file auto-discovery presenti "
            f"({len(discovery_present)}/{len(AUTO_DISCOVERY_FILES)}): "
            + ", ".join(discovery_present or ["nessuno"])
            + " — esegui init_project_memory.sh"
        )

    active = memory / "ACTIVE_WORK.md"
    if active.is_file():
        now = datetime.now()
        for line in active.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line.startswith("- ["):
                continue
            if line.startswith("- [*]") or "Nessun lavoro" in line:
                continue
            if not CLAIM_RE.match(line):
                warnings.append(f"ACTIVE_WORK formato non standard: {line[:80]}")
            else:
                m = re.search(r"scade (\d{4}-\d{2}-\d{2} \d{2}:\d{2})", line)
                if m:
                    expiry = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M")
                    if expiry < now:
                        warnings.append(f"Claim scaduto: {line[:80]}")

    state = memory / "PROJECT_STATE.md"
    worklog = memory / "WORKLOG.md"
    worklog_text = worklog.read_text(encoding="utf-8") if worklog.is_file() else ""
    fresh = is_fresh_install(worklog_text, has_session_summary)

    if state.is_file() and worklog.is_file():
        state_text = state.read_text(encoding="utf-8")
        m = UPDATED_RE.search(state_text)
        if m:
            state_date = datetime.strptime(m.group(1), "%Y-%m-%d")
            if datetime.now() - state_date > timedelta(days=14):
                warnings.append(
                    f"PROJECT_STATE.md potrebbe essere obsoleto (ultimo aggiornamento {m.group(1)})"
                )

    if worklog.is_file() and "## [" not in worklog_text:
        if fresh:
            notes.append("WORKLOG.md vuoto — verrà popolato alla prima sessione agente")
        else:
            warnings.append("WORKLOG.md senza voci sessione")

    _report(errors, warnings, notes, discovery_present)
    return 1 if errors else 0


def _report(
    errors: list[str],
    warnings: list[str],
    notes: list[str] | None = None,
    discovery: list[str] | None = None,
) -> None:
    """Print a human-readable validation report."""
    if errors:
        _write_line("ERRORS:")
        for e in errors:
            _write_line(f"  - {e}")
    if warnings:
        _write_line("WARNINGS:")
        for w in warnings:
            _write_line(f"  - {w}")
    if notes:
        _write_line("NOTES:")
        for n in notes:
            _write_line(f"  - {n}")
    if not errors and not warnings:
        _write_line("OK: .agents/ memory layout valid")
        if discovery:
            _write_line(f"  Auto-discovery files: {', '.join(discovery)}")
        if notes:
            for n in notes:
                _write_line(f"  Note: {n}")


def _write_line(message: str) -> None:
    """Write a single report line to stdout without using print()."""
    sys.stdout.write(f"{message}\n")


if __name__ == "__main__":
    raise SystemExit(main())
