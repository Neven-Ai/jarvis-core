#!/usr/bin/env bash
# Bootstrap .agents/ memory layout for a new project.
# Usage: .agents/scripts/init_project_memory.sh [project-name]
#        .agents/scripts/init_project_memory.sh --merge-agents   # patch existing AGENTS.md

set -euo pipefail

PROJECT_NAME=""
MERGE_AGENTS=false

for arg in "$@"; do
  case "$arg" in
    --merge-agents) MERGE_AGENTS=true ;;
    -h|--help)
      echo "Usage: init_project_memory.sh [--merge-agents] [project-name]"
      exit 0
      ;;
    *)
      if [[ -z "$PROJECT_NAME" ]]; then
        PROJECT_NAME="$arg"
      fi
      ;;
  esac
done

PROJECT_NAME="${PROJECT_NAME:-$(basename "$(pwd)")}"
DATE="$(date +%Y-%m-%d)"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SKILL_ASSETS="$ROOT/.agents/skills/collaborative-project-memory/assets"
AUTONOMY_MARKERS=("autonomo" "senza che l'utente" "primo turno" "stesso turno")

mkdir -p "$ROOT/.agents/memory" "$ROOT/.agents/sessions/archive" "$ROOT/.github"

substitute() {
  sed "s/{{PROJECT_NAME}}/$PROJECT_NAME/g; s/{{DATE}}/$DATE/g"
}

write_if_missing() {
  local dest="$1"
  local src="$2"
  if [[ ! -f "$dest" ]] && [[ -f "$src" ]]; then
    substitute < "$src" > "$dest"
    echo "  Created $(realpath --relative-to="$ROOT" "$dest")"
  fi
}

has_autonomy_markers() {
  local file="$1"
  [[ -f "$file" ]] || return 1
  local text lower
  text="$(tr '[:upper:]' '[:lower:]' < "$file")"
  for marker in "${AUTONOMY_MARKERS[@]}"; do
    if [[ "$text" == *"$marker"* ]]; then
      return 0
    fi
  done
  return 1
}

ensure_autonomy_section() {
  local dest="$1"
  local label="$2"
  [[ -f "$dest" ]] || return 0
  if has_autonomy_markers "$dest"; then
    return 0
  fi
  if [[ ! -f "$SKILL_ASSETS/autonomy-section.md.snippet" ]]; then
    echo "  WARN: missing autonomy snippet; cannot patch $label"
    return 0
  fi
  {
    echo ""
    cat "$SKILL_ASSETS/autonomy-section.md.snippet"
  } >> "$dest"
  echo "  Patched $label — aggiunta sezione comportamento autonomo"
}

WORKLOG_NEW=false
if [[ ! -f "$ROOT/.agents/memory/WORKLOG.md" ]]; then
  WORKLOG_NEW=true
  cat > "$ROOT/.agents/memory/WORKLOG.md" <<EOF
# WORKLOG — $PROJECT_NAME

> Storico conversazioni e modifiche, voce più recente in alto. Append-only.
> **Agenti**: aggiorna dopo ogni operazione completata — vedi \`AGENTS.md\` e \`.agents/skills/collaborative-project-memory/SKILL.md\`.

---

EOF
fi

if ! grep -q '^## \[' "$ROOT/.agents/memory/WORKLOG.md" 2>/dev/null; then
  cat >> "$ROOT/.agents/memory/WORKLOG.md" <<EOF
## [$DATE] Init memoria progetto (script: init_project_memory.sh)
**Richieste**: bootstrap collaborative project memory
**Modifiche**:
- \`.agents/\` — layout memoria inizializzato
**Esito**: completato

EOF
  if [[ "$WORKLOG_NEW" == false ]]; then
    echo "  Added init entry to WORKLOG.md"
  fi
fi

for f in BUGS ACTIVE_WORK DECISIONS; do
  if [[ ! -f "$ROOT/.agents/memory/$f.md" ]]; then
    case "$f" in
      BUGS)
        cat > "$ROOT/.agents/memory/BUGS.md" <<EOF
# BUGS — $PROJECT_NAME

> Bug aperti e risolti. Aggiornare lo stato, non cancellare i risolti.

---

*Nessun bug registrato.*

EOF
        ;;
      ACTIVE_WORK)
        cat > "$ROOT/.agents/memory/ACTIVE_WORK.md" <<EOF
# ACTIVE WORK — $PROJECT_NAME

> Claim per coordinamento multi-utente. Rimuovere a task completato o scaduto.

---

*Nessun lavoro in corso.*

EOF
        ;;
      DECISIONS)
        cat > "$ROOT/.agents/memory/DECISIONS.md" <<EOF
# DECISIONS — $PROJECT_NAME

> Architecture Decision Records (ADR). Non riscrivere decisioni passate.

---

EOF
        ;;
    esac
  fi
done

write_if_missing "$ROOT/.agents/memory/PROJECT_STATE.md" "$SKILL_ASSETS/PROJECT_STATE.md.template"
write_if_missing "$ROOT/.agents/memory/TODO.md" "$SKILL_ASSETS/TODO.md.template"
write_if_missing "$ROOT/AGENTS.md" "$SKILL_ASSETS/AGENTS.md.template"
write_if_missing "$ROOT/.github/copilot-instructions.md" "$SKILL_ASSETS/copilot-instructions.md.template"
write_if_missing "$ROOT/CLAUDE.md" "$SKILL_ASSETS/CLAUDE.md.template"
write_if_missing "$ROOT/.agents/AGENTS.md" "$SKILL_ASSETS/agents-dir-AGENTS.md.template"

if [[ "$MERGE_AGENTS" == true ]] || [[ -f "$ROOT/AGENTS.md" ]]; then
  ensure_autonomy_section "$ROOT/AGENTS.md" "AGENTS.md"
  ensure_autonomy_section "$ROOT/.github/copilot-instructions.md" ".github/copilot-instructions.md"
  ensure_autonomy_section "$ROOT/CLAUDE.md" "CLAUDE.md"
fi

if [[ ! -f "$ROOT/.agents/README.md" ]]; then
  cat > "$ROOT/.agents/README.md" <<'EOF'
# Agent memory

Collaborative multi-agent memory for this project.

- **Agenti**: leggi subito `AGENTS.md` (questa cartella) e `../AGENTS.md` (root)
- **Protocollo**: `skills/collaborative-project-memory/SKILL.md`
- **Installazione**: `skills/collaborative-project-memory/references/INSTALL.md`
EOF
fi

echo "Initialized .agents/ memory for: $PROJECT_NAME"
echo "  Edit .agents/memory/PROJECT_STATE.md next."
echo "  Auto-discovery: AGENTS.md, .github/copilot-instructions.md, CLAUDE.md, .agents/AGENTS.md"
echo "  Validate: python3 .agents/scripts/validate_memory.py"
