# Best Practices — Collaborative Project Memory

## Frequenza

| Scenario | Azione |
|----------|--------|
| Ogni sessione | SYNC: leggi memoria + ACTIVE_WORK |
| Dopo ogni task completato | SYNC: aggiorna WORKLOG/TODO/BUGS |
| Sessione > 1 ora o fine giornata | CHECKPOINT |
| Task > 30 min | Claim in ACTIVE_WORK |
| Cambio contesto | CHECKPOINT + aggiorna claim |

## Claim efficaci

- OK: `[2026-07-07 10:00] **neven** — perf pianificazione drag — branch main — scade 2026-07-07 18:00`
- NO: `sto lavorando sul backend`

## Checkpoint efficaci

- OK: "Fix `TabPianificazione.tsx`: `refresh-incassi` in background dopo `GET /calendario`"
- NO: "Migliorata performance"

## ADR vs WORKLOG

- **WORKLOG**: cosa è stato fatto, quando, da chi
- **DECISIONS**: perché una scelta resta valida nel tempo (non riscrivere ADR passati)

## Multi-utente

1. Leggi ACTIVE_WORK prima di iniziare
2. Registra claim su task lunghi
3. Non toccare claim altrui
4. Preferisci branch separati per lavoro parallelo
5. In caso di conflitto git su WORKLOG: unisci manualmente preservando entrambe le voci

## Metriche di qualità

Un nuovo agente deve poter:
- Riprendere in < 5 minuti
- Avviare i servizi con comandi da PROJECT_STATE
- Capire WIP da SESSION_SUMMARY + ACTIVE_WORK
- Evitare di duplicare lavoro già in corso
