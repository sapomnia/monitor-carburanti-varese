"""
Scarica i prezzi carburanti dal MIMIT e genera data/prezzi.json.
Eseguito ogni mattina dal GitHub Action.
"""
import csv
import json
import io
import sys
from datetime import date

try:
    import requests
except ImportError:
    print("requests non trovato. Installa con: pip install requests")
    sys.exit(1)

PREZZI_URL = "https://www.mimit.gov.it/images/exportCSV/prezzo_alle_8.csv"
ANAGRAFICA_PATH = "data/anagrafica.json"
OUTPUT_PATH = "data/prezzi.json"
TOP_N = 5  # stazioni più convenienti per ogni combinazione comune/carburante

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; carburanti-bot/1.0)",
    "Accept-Encoding": "gzip, deflate",
}


def download_prezzi() -> str:
    print(f"Download prezzi da {PREZZI_URL}...")
    resp = requests.get(PREZZI_URL, headers=HEADERS, timeout=60)
    resp.raise_for_status()
    # Il file è ISO-8859-1 o UTF-8: proviamo entrambi
    for enc in ("utf-8", "latin-1"):
        try:
            return resp.content.decode(enc)
        except UnicodeDecodeError:
            continue
    return resp.text


def parse_prezzi(content: str, anagrafica: dict) -> dict:
    lines = content.splitlines()
    estrazione = ""
    # Prima riga: "Estrazione del YYYY-MM-DD"
    if lines and lines[0].startswith("Estrazione"):
        estrazione = lines[0].replace("Estrazione del ", "").strip()
        lines = lines[1:]

    reader = csv.DictReader(lines, delimiter="|")
    data: dict = {}
    skipped = 0

    for row in reader:
        imp_id = row.get("idImpianto", "").strip()
        if imp_id not in anagrafica:
            skipped += 1
            continue
        carb = row.get("descCarburante", "").strip()
        prezzo_str = row.get("prezzo", "").strip()
        try:
            prezzo = float(prezzo_str)
        except ValueError:
            continue
        is_self = 1 if row.get("isSelf", "").strip() == "1" else 0

        imp = anagrafica[imp_id]
        comune = imp["c"]

        if comune not in data:
            data[comune] = {}
        if carb not in data[comune]:
            data[comune][carb] = []

        data[comune][carb].append({
            "p": prezzo,
            "s": is_self,
            "n": imp["n"],
            "i": imp["i"],
            "g": imp["g"],
        })

    print(f"  Impianti senza anagrafica saltati: {skipped}")
    return data, estrazione


def main():
    # Carica anagrafica statica
    print(f"Carico anagrafica da {ANAGRAFICA_PATH}...")
    with open(ANAGRAFICA_PATH, encoding="utf-8") as f:
        anagrafica = json.load(f)
    print(f"  Impianti in anagrafica: {len(anagrafica)}")

    # Scarica prezzi
    content = download_prezzi()

    # Parsa e indicizza
    data, estrazione = parse_prezzi(content, anagrafica)

    # Ordina per prezzo e tieni i top N
    all_carburanti = set()
    for comune in data:
        for carb in data[comune]:
            data[comune][carb].sort(key=lambda x: x["p"])
            data[comune][carb] = data[comune][carb][:TOP_N]
            all_carburanti.add(carb)

    # Comuni della provincia di Varese presenti nei dati
    comuni_va = sorted(
        imp["c"] for imp in anagrafica.values()
        if imp.get("prov") == "VA" and imp["c"] in data
    )
    # Deduplicazione mantenendo l'ordine
    seen = set()
    comuni_va = [c for c in comuni_va if not (c in seen or seen.add(c))]

    output = {
        "aggiornato": estrazione or str(date.today()),
        "carburanti": sorted(all_carburanti),
        "comuni_va": comuni_va,
        "dati": data,
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, separators=(",", ":"))

    size_mb = len(json.dumps(output).encode()) / 1024 / 1024
    print(f"Scritto {OUTPUT_PATH}: {len(data)} comuni, {len(all_carburanti)} carburanti, {size_mb:.2f} MB")


if __name__ == "__main__":
    main()
