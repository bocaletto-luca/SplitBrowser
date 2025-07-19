# SplitBrowser

> Browser desktop multi-scheda con layout “split” dinamico e supporto full-screen per tab e per singoli pannelli.

SplitBrowser è un’applicazione Python basata su PyQt5 e PyQtWebEngine, che permette di navigare sul web con schede multiple, suddividere ogni scheda in 1–4 pannelli (orizzontale o verticale), andare in full-screen sull’intera finestra o sui singoli pannelli, e passare agilmente da un pannello o da una scheda all’altra.

Repository: https://github.com/bocaletto-luca/SplitBrowser  

---

## Caratteristiche Principali

- Gestione di più schede (New Tab / Close Tab)  
- Split di ciascuna scheda in 1, 2, 3 o 4 pannelli, con ripartizione automatica:  
  - 2 parti → 50% / 50%  
  - 3 parti → ~33% ciascuna  
  - 4 parti → 25% ciascuna  
- Pannello di navigazione per ogni mini-browser:  
  - Barra URL + pulsanti ◀ (Indietro), ▶ (Avanti), ⟳ (Ricarica), 🗑 (Pulisci cache), Go  
- Full-screen globale della finestra (F11 / Esc)  
- Full-screen di un singolo pannello (Shift+F11 / Esc), con menu sempre visibile  
- Scorciatoie per passare tra schede e pannelli in full-screen:  
  - Ctrl+PgUp / Ctrl+PgDown → cambia scheda (in modalità full-tab)  
  - Ctrl+Tab / Ctrl+Shift+Tab → cambia pannello (in modalità full-pane)  
- Barra menu sempre accessibile per richiamare tutte le azioni  

---

## Requisiti

- Python 3.7+  
- PyQt5  
- PyQtWebEngine  

---

## Installazione

```bash
# Clona il repository
git clone https://github.com/bocaletto-luca/SplitBrowser.git
cd SplitBrowser

# Crea e attiva il virtual environment
python3 -m venv venv
source venv/bin/activate      # Linux / macOS
# o
.\venv\Scripts\activate       # Windows PowerShell

# Installa le dipendenze
pip install --upgrade pip
pip install PyQt5 PyQtWebEngine
```

---

## Uso

```bash
# All’interno del venv
python main.py
```

- **Nuova scheda**: File → New Tab (Ctrl+T)  
- **Chiudi scheda**: File → Close Tab (Ctrl+W)  
- **Split**: menu Split → scegli “1 Panel” o “Horizontal”/“Vertical” → 2, 3 o 4 Panels  
- **Full-screen tab**: View → FullScreen Tab (F11 / Esc)  
- **Full-screen pane**: View → FullScreen Pane (Shift+F11 / Esc)  
- **Navigazione**:  
  - ◀ / ▶ / ⟳ / Go / 🗑 (per ogni pannello)  
  - Ctrl+PgUp / Ctrl+PgDown (cambio scheda in full-tab)  
  - Ctrl+Tab / Ctrl+Shift+Tab (cambio pannello in full-pane)  

---

## Struttura del Progetto

```
SplitBrowser/
├── main.py              # Entry point dell’applicazione
├── requirements.txt     # (opzionale) pip freeze > requirements.txt
└── README.md            # Questo file
```

---

## Contributi

1. Fork del repository  
2. Crea un branch feature: `git checkout -b feature/NOME`  
3. Aggiungi/modifica il codice e fai commit  
4. Invia una Pull Request  

---

## Licenza

Questo progetto è rilasciato sotto licenza MIT.  
© 2025 Luca Bocaletto.
