# Agent memory

Collaborative multi-agent memory for this project.

## Avvio rapido per agenti

1. Leggi `AGENTS.md` (questa cartella) e `../AGENTS.md` (root)
2. Esegui **SYNC** (skill): `skills/collaborative-project-memory/SKILL.md`
3. Se lavori sul **monitoring evoluto**, leggi obbligatoriamente:
   - **`.agents/memory/MONITORING_PLAN.md`** — piano implementazione completo
   - `.agents/memory/DECISIONS.md` — ADR vincolanti
   - `.agents/memory/TODO.md` — backlog by phase

## Fonti di verità

| Domanda | File |
|---------|------|
| Come implementare il monitoring? | **`memory/MONITORING_PLAN.md`** |
| Perché abbiamo scelto X? | `memory/DECISIONS.md` |
| Cosa fare dopo? | `memory/TODO.md` |
| Stack, DB, avvio? | `memory/PROJECT_STATE.md` |
| Cosa è successo di recente? | `memory/WORKLOG.md` |
| Chi sta lavorando su cosa? | `memory/ACTIVE_WORK.md` |
| Stato sessione / handover? | `sessions/SESSION_SUMMARY.md` |

## Protocollo

- **SYNC**: inizio sessione e dopo ogni operazione completata
- **CHECKPOINT**: fine sessione → `sessions/SESSION_SUMMARY.md`
- **Validazione**: `python3 .agents/scripts/validate_memory.py`

Installazione skill: `skills/collaborative-project-memory/references/INSTALL.md`
