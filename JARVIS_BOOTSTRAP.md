# JARVIS\_BOOTSTRAP — Setup nuovo repository `jarvis-monitor`

**Scopo di questo documento**: istruzioni operative per un agente AI (Cursor) per creare da zero il repository `jarvis-monitor` come **custom integration** di Home Assistant, migrando il lavoro esistente dal fork di `home-assistant/core`. Questo documento va letto INSIEME a `MONITORING_PLAN.md`, che resta la fonte di verità per requisiti, architettura, schema dati e roadmap. In caso di conflitto vince `MONITORING_PLAN.md`, salvo dove questo documento traduce esplicitamente percorsi "fork" in percorsi "custom integration" (vedi §6 — Mappa di traduzione).

---

## 1\. Decisione architetturale (contesto per l'agente)

Il progetto jarvis nasceva come fork di Home Assistant Core. È stato deciso (ADR da registrare come ADR-005 in `DECISIONS.md`) di riconvertirlo in **custom integration** perché:

1. Nulla nel piano richiede modifiche al core: entity bridge (`state_changed`), store SQLite proprio, REST/WS API custom, `StaticPathConfig` \+ `panel_custom` sono tutti disponibili alle custom integration.  
2. L'accesso al bus KNX per la presenza avviene tramite l'oggetto `xknx` dell'integrazione KNX ufficiale, raggiungibile via `hass.data` — senza patchare `homeassistant/components/knx/`.  
3. Il fork impone rebase mensili su `dev` e accoppia gli aggiornamenti jarvis agli aggiornamenti HA; la custom integration si aggiorna in modo indipendente su HA stock.

**Regola permanente**: se durante lo sviluppo emerge un requisito che sembra richiedere una modifica al core, NON tornare al fork. Fermarsi, documentare il caso in `DECISIONS.md` come proposta di ADR e valutare una PR upstream a `home-assistant/core`.

---

## 2\. Struttura target del repository

Creare la seguente struttura (pattern `integration_blueprint` di ludeeus, adattato):

```
jarvis-monitor/
├── .devcontainer/
│   └── devcontainer.json          # vedi §3
├── .github/
│   └── workflows/
│       ├── lint.yml               # ruff + hassfest validation
│       └── test.yml               # pytest su push/PR
├── .agents/
│   ├── memory/
│   │   ├── MONITORING_PLAN.md     # COPIARE dal fork (invariato salvo §6)
│   │   ├── PROJECT_STATE.md       # riscrivere per il nuovo repo (vedi §7)
│   │   ├── DECISIONS.md           # COPIARE dal fork + aggiungere ADR-005
│   │   ├── TODO.md                # COPIARE dal fork
│   │   ├── WORKLOG.md             # nuovo, vuoto
│   │   └── ACTIVE_WORK.md         # nuovo, vuoto
│   └── skills/
│       └── collaborative-project-memory/   # COPIARE dal fork
├── config/                        # config dir HA per sviluppo locale (gitignored salvo configuration.yaml di esempio)
│   └── configuration.yaml
├── custom_components/
│   ├── jarvis_monitor/
│   │   ├── __init__.py
│   │   ├── manifest.json          # domain: jarvis_monitor, version, requirements, iot_class: calculated
│   │   ├── const.py
│   │   ├── config_flow.py
│   │   ├── strings.json
│   │   ├── translations/
│   │   │   ├── en.json
│   │   │   └── it.json
│   │   ├── store/
│   │   │   ├── __init__.py
│   │   │   ├── schema.py          # DDL + migrazioni (MONITORING_PLAN §5)
│   │   │   ├── usage_store.py     # CRUD + query
│   │   │   └── retention.py       # rollup + eviction
│   │   ├── ingestion/
│   │   │   ├── __init__.py
│   │   │   ├── models.py          # NormalizedUsageEvent
│   │   │   └── pipeline.py        # validazione → store → eventi HA
│   │   ├── collectors/
│   │   │   ├── __init__.py
│   │   │   ├── entity_bridge.py   # state_changed (DEFAULT, Phase 0b)
│   │   │   ├── knx_presence.py    # porting di knx/monitoring.py (Phase 1) — vedi §6
│   │   │   └── knx_telegram.py    # opzionale (Phase 1)
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── rest.py
│   │   │   └── websocket.py
│   │   ├── alerts/
│   │   │   ├── __init__.py
│   │   │   ├── engine.py
│   │   │   └── notify_adapters.py
│   │   ├── frontend/              # sorgente TS/React — NON incluso nel pacchetto distribuito
│   │   │   ├── package.json
│   │   │   └── src/
│   │   └── www/                   # output npm run build (servito da HA via StaticPathConfig)
│   └── lutron_leap_custom/        # COPIARE dal fork (homeassistant/components/lutron_leap_custom/)
├── tests/
│   ├── conftest.py                # fixture pytest-homeassistant-custom-component
│   └── jarvis_monitor/
│       ├── test_store.py
│       ├── test_ingestion.py
│       ├── test_entity_bridge.py
│       ├── test_interval_engine.py
│       └── test_retention.py
├── scripts/
│   ├── setup                      # uv sync / pip install -r requirements
│   ├── develop                    # avvia HA con config/ e custom_components/ montati
│   └── lint                       # ruff check + ruff format
├── requirements.txt               # homeassistant==<pin ultima stable>, xknx, ecc.
├── requirements-dev.txt           # pytest, pytest-homeassistant-custom-component, ruff, pre-commit
├── pyproject.toml                 # ruff config, pytest config
├── .pre-commit-config.yaml
├── .gitignore                     # config/* (salvo configuration.yaml), www/ generato, .venv, __pycache__
├── hacs.json                      # predisposizione HACS (anche se distribuzione privata)
├── AGENTS.md                      # costituzione operativa: COPIARE dal fork e adattare percorsi
└── README.md
```

**Differenza chiave rispetto al fork**: il codice vive in `custom_components/jarvis_monitor/`, non in `homeassistant/components/jarvis_monitor/`. Home Assistant è una **dipendenza pip** (pinnata in `requirements.txt`), non il repository ospitante.

---

## 3\. Devcontainer

`.devcontainer/devcontainer.json` di riferimento:

```json
{
  "name": "jarvis-monitor dev",
  "image": "mcr.microsoft.com/devcontainers/python:3.13",
  "postCreateCommand": "scripts/setup",
  "forwardPorts": [8123],
  "portsAttributes": {
    "8123": { "label": "Home Assistant", "onAutoForward": "notify" }
  },
  "features": {
    "ghcr.io/devcontainers/features/node:1": { "version": "lts" }
  },
  "mounts": [
    "source=${localEnv:HOME}/.ssh,target=/home/vscode/.ssh,type=bind,readonly"
  ],
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "charliermarsh.ruff",
        "esbenp.prettier-vscode"
      ]
    }
  }
}
```

Note per l'agente:

- **Verificare la versione Python richiesta** dall'ultima release stabile di Home Assistant prima di fissare l'immagine (allineare immagine devcontainer e `requires-python` in `pyproject.toml`).  
- Il mount `~/.ssh` replica il comportamento del vecchio devcontainer per `git push` verso GitHub.  
- `scripts/develop` deve avviare HA puntando a `config/` con `custom_components/` raggiungibile (symlink `config/custom_components → ../custom_components` oppure avvio con working dir adeguata).

---

## 4\. Migrazione dal fork — checklist operativa

Il fork GitHub esistente (fork di `home-assistant/core`, branch `neven/jarvis`) NON va convertito: si crea un repo nuovo e si copiano solo i file di valore. Il fork resta come riferimento in sola lettura finché la migrazione non è completa, poi si archivia.

Copiare dal fork (branch `neven/jarvis`):

| Sorgente (fork) | Destinazione (nuovo repo) | Azione |
| :---- | :---- | :---- |
| `.agents/memory/MONITORING_PLAN.md` | `.agents/memory/MONITORING_PLAN.md` | Copia invariata |
| `.agents/memory/DECISIONS.md` | `.agents/memory/DECISIONS.md` | Copia \+ aggiungere ADR-005 (custom integration) |
| `.agents/memory/TODO.md` | `.agents/memory/TODO.md` | Copia |
| `.agents/skills/` | `.agents/skills/` | Copia |
| `AGENTS.md` | `AGENTS.md` | Copia \+ adattare percorsi (§6) |
| `homeassistant/components/knx/monitoring.py` | `custom_components/jarvis_monitor/collectors/knx_presence.py` | **Porting con refactor** (Phase 1, vedi §6) — per ora copiare in `collectors/_legacy_knx_monitoring.py` come riferimento |
| `homeassistant/components/lutron_leap_custom/` | `custom_components/lutron_leap_custom/` | Copia; adattare import relativi se presenti |

NON copiare: tutto il resto del monorepo core (incluso `homeassistant/components/knx/telegrams.py` e `websocket.py` — restano nel core stock e si riusano come API, MONITORING\_PLAN §9).

---

## 5\. Vincoli tecnici specifici della custom integration

1. **Accesso a xknx senza fork**: il collector `knx_presence` ottiene l'istanza xknx dall'integrazione KNX ufficiale caricata, via `hass.data`. Verificare nella versione HA pinnata la chiave esatta e la struttura dati (negli ultimi anni è cambiata più volte: controllare `homeassistant/components/knx/__init__.py` della release pinnata, non andare a memoria). Dichiarare `"dependencies": ["knx"]` oppure `"after_dependencies": ["knx"]` nel `manifest.json` a seconda che KNX sia richiesto o opzionale (deciderlo: jarvis\_monitor deve caricarsi anche su impianti senza KNX → `after_dependencies`).  
2. **`nm_individual_address_check`**: è una funzione di xknx, utilizzabile direttamente dall'istanza ottenuta al punto 1\. Nessuna modifica al componente knx necessaria.  
3. **Storage path**: usare `hass.config.path(".storage/jarvis_monitor/usage.db")` come da MONITORING\_PLAN §5, creando la directory al primo avvio.  
4. **SQLite e event loop**: tutte le operazioni DB in executor (`hass.async_add_executor_job`) o thread dedicato; mai I/O bloccante nel loop.  
5. **Frontend**: registrare `www/` con `StaticPathConfig` e `panel_custom` solo se `advanced_panel_enabled` (MONITORING\_PLAN §1). Il pattern di riferimento è `knx/websocket.py` nel core — consultarlo nella dipendenza pip installata.  
6. **Test**: usare `pytest-homeassistant-custom-component` (fixture `hass` per custom integration, equivalente a quelle interne del core).  
7. **Nessuna dipendenza da percorsi del core**: vietato importare da `homeassistant.components.knx` API private/non documentate senza annotarlo in `DECISIONS.md` (rischio breaking change mensile).

---

## 6\. Mappa di traduzione fork → custom integration

Ovunque `MONITORING_PLAN.md` o `AGENTS.md` citino percorsi del fork, leggere così:

| Nel piano (fork) | Nel nuovo repo |
| :---- | :---- |
| `homeassistant/components/jarvis_monitor/` | `custom_components/jarvis_monitor/` |
| `homeassistant/components/knx/monitoring.py` (refactor Phase 1\) | `custom_components/jarvis_monitor/collectors/knx_presence.py` |
| `homeassistant/components/lutron_leap_custom/` | `custom_components/lutron_leap_custom/` |
| `tests/components/jarvis_monitor/` | `tests/jarvis_monitor/` |
| `script/setup`, avvio `uv run python -m homeassistant -c ./config` | `scripts/setup`, `scripts/develop` |
| "Rebuild Container dopo modifica devcontainer" | invariato |
| Branch `dev` / `neven/jarvis` | `main` / feature branch `feat/<phase>-<slug>` |

La roadmap (Phase 0a → 5), lo schema SQLite (§5), le API (§9), i criteri di accettazione (§10) e le regole per gli agenti (§11) di `MONITORING_PLAN.md` restano validi senza modifiche.

---

## 7\. Sequenza operativa per l'agente (prima sessione)

Eseguire in ordine, chiedendo conferma all'utente nei punti marcati ⚠:

1. Scaffold della struttura §2 (file vuoti/minimi ma repo avviabile).  
2. `requirements.txt`: pinnare l'ultima release **stabile** di Home Assistant (verificarla, non inventarla) \+ `xknx` alla versione compatibile.  
3. Devcontainer §3; verificare che `scripts/setup` e `scripts/develop` funzionino (HA parte, risponde su :8123, carica `jarvis_monitor` come dominio vuoto).  
4. Migrazione file §4.  
5. Riscrivere `.agents/memory/PROJECT_STATE.md` per il nuovo repo (stack, avvio, test, DB — stesso formato del fork).  
6. Aggiungere ADR-005 in `DECISIONS.md`: "jarvis\_monitor come custom integration, non fork" con motivazioni §1.  
7. ⚠ Mostrare all'utente lo stato e chiedere conferma prima di procedere.  
8. Iniziare **Phase 0a** come da MONITORING\_PLAN §10: scaffold integrazione caricabile → schema SQLite → UsageStore → NormalizedUsageEvent \+ pipeline → config globale. Test inclusi.

Regole permanenti (da MONITORING\_PLAN §11, valide anche qui):

- SYNC obbligatorio a inizio sessione: leggere `MONITORING_PLAN.md`, `DECISIONS.md`, `TODO.md`.  
- Rispettare l'ordine delle fasi; deviazioni solo con nuovo ADR.  
- Test obbligatori per ogni phase; preferire `@pytest.mark.parametrize`.  
- **Mai commit/push senza consenso esplicito dell'utente.**  
- Task \> 30 min → riga in `ACTIVE_WORK.md`; a fine sessione aggiornare `WORKLOG.md` e `TODO.md`.

---

*Creato: 2026-07-08 — Documento di bootstrap approvato dall'utente per l'avvio del repo `jarvis-monitor`.*  
