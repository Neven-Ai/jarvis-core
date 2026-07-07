<!-- agents-memory v1 | project: jarvis | updated: 2026-07-07 -->

# PROJECT_STATE — jarvis

> Stato generale del progetto. Aggiornare solo su cambi architetturali, DB, servizi o procedure di avvio.

## Cos'è

Questo repository contiene `homeassistant`, il core di Home Assistant: una piattaforma open source di home automation orientata a controllo locale e privacy. Il codice principale vive nel package `homeassistant/`, con test in `tests/`, script di sviluppo in `script/` e una configurazione locale di esempio in `config/`.

## Stack e struttura

| Servizio | Tecnologia | Porta | Percorso |
|----------|-----------|-------|----------|
| Core applicativo | Python 3.14 / Home Assistant Core | variabile | `homeassistant/` |
| Test suite | `pytest` | n/a | `tests/` |
| Tooling sviluppo | `uv`, `prek`, `pylint`, `ruff` | n/a | `script/`, `.pre-commit-config.yaml` |
| Config locale di avvio | Home Assistant config dir | runtime locale | `config/` |

## Come si avvia

```bash
script/setup
uv run python -m homeassistant -c ./config
```

Note:
- In VS Code esiste anche il task `Run Home Assistant Core`, che avvia `python -m homeassistant -c ./config`.
- Quando si entra in un nuovo environment o worktree, `script/setup` e il passaggio richiesto prima di lavorare o committare.

## Database

Nessun database esterno dedicato rilevato da questa memoria di progetto. Per sviluppo locale il runtime usa la configurazione standard di Home Assistant sotto `config/`; eventuali dettagli specifici di integrazione o storage vanno documentati qui solo se diventano rilevanti per il lavoro corrente.

## Test

```bash
uv run pytest
uv run pytest tests/components/<integration_name>
uv run prek run --all-files
```

Comandi utili aggiuntivi:
- `python -m script.translations develop --all` per compilare le traduzioni inglesi durante test/lavoro su stringhe
- task VS Code disponibili per `Pytest`, `Ruff`, `Prek`, coverage e update snapshot Syrupy

## Git

- Branch principale: `dev`
- Vincolo: mai commit/push senza consenso esplicito
- Working tree attualmente sporco: presenti modifiche utente pregresse oltre ai file in `.agents/`

## Documentazione chiave

- `README.rst` — overview del progetto
- `AGENTS.md` — costituzione operativa del repo
- `.github/copilot-instructions.md` — istruzioni derivate per Copilot
- `.agents/memory/` — memoria agenti
- `.agents/skills/collaborative-project-memory/SKILL.md` — protocollo SYNC/CHECKPOINT/INIT
- `.agents/sessions/archive/` — checkpoint storici
