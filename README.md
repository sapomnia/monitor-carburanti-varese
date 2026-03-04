# ⛽ Monitor Carburanti Varese

Calcolatore web che ogni mattina scarica i prezzi dei carburanti comunicati al MIMIT e permette di trovare il distributore più conveniente nei comuni della provincia di Varese.

## Come funziona

1. Ogni mattina alle 08:15 un GitHub Action scarica automaticamente il file prezzi dal MIMIT (`prezzo_alle_8.csv`)
2. I dati vengono elaborati e il sito viene aggiornato e pubblicato su GitHub Pages
3. Il file prezzi **non viene mai salvato nel repository**: viene generato al volo e deployato direttamente, senza accumulare storia

## Cosa mostra il calcolatore

- Seleziona un comune della provincia di Varese
- Seleziona il tipo di carburante
- Ottieni le stazioni più economiche con prezzo, nome, indirizzo e data/ora dell'ultima rilevazione

## Setup iniziale

### 1. Crea il repository su GitHub e fai push
```bash
git remote add origin https://github.com/TUO_USERNAME/NOME_REPO.git
git push -u origin main
```

### 2. Abilita GitHub Pages con Actions
Su GitHub: **Settings → Pages → Build and deployment → Source → GitHub Actions**

Il primo deploy parte automaticamente al push e impiega 1-2 minuti.

## File nel repository

| File | Descrizione |
|---|---|
| `index.html` | Il calcolatore web |
| `data/anagrafica.json` | Registro degli impianti nazionali (statico, ~23.500 stazioni) |
| `scripts/update_data.py` | Script che scarica e processa i prezzi giornalieri |
| `.github/workflows/update-data.yml` | GitHub Action: cron alle 08:15 + trigger su push |

> `data/prezzi.json` è escluso dal repo (vedi `.gitignore`): viene generato ogni mattina dal workflow e deployato su Pages senza essere committato.

## Aggiornare l'anagrafica degli impianti

L'anagrafica cambia raramente. Per aggiornarla manualmente:

```bash
# Scarica il file aggiornato dal MIMIT
curl -o anagrafica_impianti_attivi.csv \
  https://www.mimit.gov.it/images/exportCSV/anagrafica_impianti_attivi.csv

# Rigenera il JSON
python3 - << 'EOF'
import csv, json
anagrafica = {}
with open("anagrafica_impianti_attivi.csv", encoding="utf-8") as f:
    next(f)
    for row in csv.DictReader(f, delimiter="|"):
        anagrafica[row["idImpianto"].strip()] = {
            "n": row["Nome Impianto"].strip(),
            "i": row["Indirizzo"].strip(),
            "c": row["Comune"].strip(),
            "g": row["Gestore"].strip(),
            "prov": row["Provincia"].strip(),
        }
with open("data/anagrafica.json", "w", encoding="utf-8") as f:
    json.dump(anagrafica, f, ensure_ascii=False, separators=(",",":"))
print(f"Impianti: {len(anagrafica)}")
EOF

# Committa il nuovo file
git add data/anagrafica.json
git commit -m "chore: aggiorna anagrafica impianti"
git push
```

## Fonte dati

Ministero delle Imprese e del Made in Italy (MIMIT) — [Prezzi carburanti](https://www.mimit.gov.it/it/mercato-e-consumatori/carburanti-prezzi-e-contratti/osservatorio-prezzi-carburanti)
