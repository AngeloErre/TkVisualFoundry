# IntelliSense Python, Tkinter e librerie installate

## Il completamento dopo il punto

Nell’editor di un evento, digita:

```python
messagebox.
```

Il menu mostra i membri pubblici, fra cui `showinfo`, `showwarning`, `showerror`, `askyesno`, `askyesnocancel`, `askokcancel`, `askretrycancel`, classi e costanti. Continuando con `sh`, l’elenco si filtra. Accettare `showinfo` inserisce solo il nome del metodo: non duplica `messagebox.`.

Aprendo la chiamata:

```python
messagebox.showinfo(
```

compare la firma con parametri e argomento attivo. Per esempio, dopo il titolo il suggerimento indica `message`. I valori predefiniti e i tipi visualizzati dipendono dalla versione Python e dalle informazioni disponibili per la libreria.

## Altri esempi

| Digita | Suggerimenti |
|---|---|
| `tk.` oppure `tkinter.` | Classi, funzioni e costanti Tkinter |
| `ttk.` | Widget tematici e altri membri ttk |
| `filedialog.` | Finestre di apertura/salvataggio |
| `self.Button1.` | Metodi di Button, inclusi quelli ereditati |
| `self.Button1.configure(te` | Proprietà come `text=` |
| `value = "ciao"`, poi `value.` | Metodi delle stringhe |
| `values = []`, poi `values.` | Metodi delle liste |
| `from pathlib import Path`, poi `Path(".").` | Metodi del percorso risultante |
| `import numpy as np`, poi `np.` | Membri di NumPy installato nell’ambiente configurato |

Gli import possono stare nell’evento, nell’editor **Progetto → Import e funzioni globali** o, per i componenti della palette, nel descrittore della classe. Jedi riceve una descrizione delle finestre e dei controlli per riconoscere `self.NomeControllo`.

Una libreria esterna deve essere **installata e importata**. Installarla tramite PIP non crea da solo un nome come `np` o `requests` nel codice. Dopo l’import viene analizzata nell’ambiente corretto. Puoi usare Ctrl+Spazio anche mentre scrivi istruzioni import.

## Comandi

- **Punto**: suggerimenti automatici, con una breve attesa; le librerie grandi possono richiedere più tempo alla prima analisi.
- **Ctrl+Spazio**: completamento esplicito.
- **↑ / ↓**: seleziona un simbolo; la sua descrizione/firma appare nel pannello di aiuto.
- **Invio o Tab**: accetta il simbolo; non aggiunge parentesi automaticamente.
- **Esc**: chiude l’elenco e scarta i risultati in arrivo della richiesta corrente.
- **Motore…**: prepara o verifica Jedi nell’interprete configurato e ricarica l’analisi.

L’elenco è scorrevole. I nomi privati che iniziano con `_` sono nascosti finché non si digita `_`. Il popup viene soppresso nei commenti e mentre si scrive testo dentro una stringa; l’aiuto sulla firma può restare disponibile durante l’inserimento degli argomenti.

## Ambiente e dipendenze

Il motore usa il **Python scelto in Progetto → Configurazione**. Le librerie presenti in un altro Python non vengono considerate installate nell’ambiente del progetto. Jedi è incluso nei requisiti dell’IDE; per un interprete diverso puoi predisporlo con **Motore…**, tramite lo stesso wizard PIP.

L’analisi semantica funziona in un processo separato con cache temporanea scrivibile. Non avvia il progetto e non esegue i corpi degli eventi. Le informazioni dei tipi vengono ricavate da sorgenti, stub e supporto di Jedi. Il worker viene chiuso con l’IDE e riavviato dopo cambi di interprete o installazioni PIP, evitando suggerimenti basati su un ambiente precedente.

Se Jedi manca, rimangono i suggerimenti locali per Python/Tkinter standard e le proprietà dei componenti; il pannello segnala come attivare il motore completo. Gli errori di analisi sono visibili nel pannello e non aprono finestre modali durante la digitazione.

## Limiti

Il completamento è un’analisi di codice, non l’esecuzione del programma. Attributi creati dinamicamente, API ottenute a runtime, alcuni moduli nativi e codice senza sorgenti/stub sufficienti possono avere risultati parziali. Non è garantita la deduzione di ogni tipo di qualsiasi pacchetto. L’elenco restituito da una singola analisi è limitato a 1.200 simboli; un prefisso più specifico restringe la ricerca.

Il motore non modifica automaticamente gli import e non converte l’installazione di un pacchetto in un controllo visuale. Per riprovare dopo una modifica esterna all’ambiente, usa Motore.

Riferimenti: [API Jedi](https://jedi.readthedocs.io/en/latest/docs/api.html), [completamenti e firme](https://jedi.readthedocs.io/en/latest/docs/api-classes.html).

## Valori guidati, documentazione e controlli iniziali (1.14)

Digitando `self.Button1.configure(text=` l’editor inserisce `''` con il cursore tra le virgolette. Funziona anche accettando `text=` dalla lista. Scrivi il testo e premi `'` per oltrepassare la chiusura già inserita; Backspace tra due virgolette vuote elimina la coppia. La funzione è disattivabile nella Configurazione.

Il tipo viene ricavato dalle proprietà del componente e dai valori del designer/descrittore: testi, numeri, booleani e scelte note (`state`, `orient`, `anchor`, ecc.). I valori già presenti, i commenti e le stringhe non vengono riscritti. Per tipi sconosciuti e chiamate generiche resta l’analisi Jedi; non si inventano tipi o valori obbligatori. I descrittori esterni possono fornire valori iniziali tipizzati in `defaults`.

Nell’ispettore, **Documentazione** offre un riferimento locale con metodi, esempi, proprietà e dipendenze, il sito ufficiale e **API installata (pydoc)**. Quest’ultimo pulsante importa il modulo del componente in un processo separato, con timeout; non esegue gli eventi del progetto. Le docstring dipendono dalla libreria installata e possono essere in inglese. Non viene incorporato un browser remoto nell’IDE. Per un componente esterno aggiungere al descrittore:

```json
"documentation": "https://example.org/documentation"
```

All’avvio un controllo in background verifica i metadati dei pacchetti nel Python configurato, i requisiti del progetto e i pacchetti dell’IDE, PIP compreso. Interroga PyPI per le versioni stabili compatibili con Python e con i vincoli dichiarati: esclude prerelease, release di sviluppo e file ritirati. Esegue anche `pip check`. Le librerie opzionali non utilizzate non vengono installate. Le dipendenze transitive già installate vengono elencate, ma il pulsante di aggiornamento propone solo i requisiti dichiarati, lasciando a PIP la risoluzione delle dipendenze e la verifica delle wheel.

Apri **PIP → Controlli iniziali** oppure il pulsante sotto l’ispettore. **Ricontrolla** usa il progetto e l’interprete correnti. **Aggiorna con wizard PIP…** prepara una procedura revisionabile, senza installazione automatica. Questo controllo non certifica import nativi, driver, funzionamento hardware o API remote: usa anche il wizard dei componenti e la diagnostica.

I link documentali vengono verificati a ogni avvio. Redirect consentiti; 404/410 indicano link non validi. Errori di rete, certificati, blocchi 403, 429 e problemi temporanei sono indicati come non verificati, senza rimuovere o modificare i link. La guida locale resta disponibile offline. I controlli non bloccano l’editor e sono disattivabili nella Configurazione. Richiedono accesso HTTPS ai siti documentali e a PyPI; nessun codice, credenziale o file del progetto viene inviato.
