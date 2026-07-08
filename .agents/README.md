# Agent memory — jarvis-core (ARCHIVED)

> **Repo archiviato (2026-07-08).** Sviluppo attivo in **`jarvis-monitor`** (`/home/neven/dev/jarvis-monitor`).
> Questa memoria resta per riferimento storico e migrazione. Per lavoro corrente: `jarvis-monitor/.agents/`.

Collaborative multi-agent memory for this project.

## Avvio rapido per agenti

1. **Se il task è sviluppo jarvis**: vai a `jarvis-monitor/.agents/` e segui il SYNC lì.
2. Se consulti questo repo (riferimento fork): leggi `AGENTS.md` e `skills/collaborative-project-memory/SKILL.md`
3. Leggi `memory/PROJECT_STATE.md` — conferma stato ARCHIVED prima di modificare codice qui
4. Per contesto monitoring: `memory/MONITORING_PLAN.md` + `memory/DECISIONS.md` (ADR-005)

## Fonti di verità

| Domanda | File |
|---------|------|
| Come implementare il monitoring? | **`memory/MONITORING_PLAN.md`** |
| Come si configura l'ambiente di sviluppo? | **`memory/DEV_ENVIRONMENT.md`** |
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
