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

## Fonte dati

Ministero delle Imprese e del Made in Italy (MIMIT) — [Prezzi carburanti](https://www.mimit.gov.it/it/mercato-e-consumatori/carburanti-prezzi-e-contratti/osservatorio-prezzi-carburanti)

Il calcolatore è stato sviluppato con Claude Opus 4.6
