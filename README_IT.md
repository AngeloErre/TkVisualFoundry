# VisualTk Studio 1.10.1

Ambiente visuale per creare applicazioni Python/Tkinter, ispirato al flusso di lavoro di Visual Basic 6 e pensato principalmente per macOS. Disegna i form, modifica le proprietà, scrivi il codice degli eventi e avvia il progetto dall’IDE.

## Novità 1.9 — IntelliSense semantico

- Suggerimenti automatici dopo il punto per moduli Python/Tkinter, oggetti, variabili e librerie importate.
- `messagebox.` elenca funzioni e costanti pubbliche; `messagebox.showinfo(` mostra firma e argomento attivo.
- Riconoscimento degli import del progetto e dell’editor, inclusi alias come `import numpy as np`.
- Metodi ereditati dei controlli e analisi delle classi dei componenti esterni.
- Analisi Jedi in un processo separato, eseguito nel Python configurato per il progetto.
- Descrizione del simbolo selezionato, firme, completamento degli argomenti nominati e filtraggio durante la digitazione.
- Risposte obsolete scartate dopo modifiche, cambio contesto o Esc; cache temporanea dedicata.
- Pulsante **Motore…** per predisporre Jedi con il wizard PIP quando manca nell’interprete scelto.

## Funzionalità

| Area | Contenuto |
|---|---|
| Designer | Form multipli, palette, spostamento, ridimensionamento, colori e font |
| Editor eventi | Doppio clic sul controllo, sintassi colorata, indentazione e completamento |
| Assistente codice | Suggerimenti per componente/evento, metodi, proprietà e frammenti spiegati in italiano |
| Form | Creazione, apertura, duplicazione ed eliminazione; `self.show` e `self.hide` |
| Componenti esterni | Procedura guidata, descrittori JSON ed esploratore PyPI |
| Pacchetti | Wizard nell’interprete dei progetti, controllo versioni/import e conflitti |
| Dati | DatabaseView con tabella, inserimento, modifica, eliminazione e rilettura |
| Multimedia e periferiche | Immagini, audio, webcam, USB e seriale tramite pacchetti opzionali |
| Web e video | Adattatori HTML/web, VLC e risoluzione stream YouTube |
| Esecuzione | Avvio separato, output, arresto, breakpoint e comandi pdb |
| Esportazione | Sorgente Python indipendente e packaging con PyInstaller |
| Ambiente | Preset Chiaro, Scuro, Seppia e colori personalizzati persistenti |
| Help | Guida, esempi, diagnostica, pacchetti e database |

## Installazione e aggiornamento su Mac

1. Scarica i sorgenti o estrai il pacchetto ZIP in una cartella scrivibile.
2. Esegui `Install_Mac.command` con doppio clic oppure `bash Install_Mac.command` dal Terminale.
3. L’installer individua **Python 3.15 stabile o successivo con Tkinter**, prepara l’ambiente virtuale dell’IDE e crea `VisualTk Studio.app` in `~/Applications`.
4. Avvia l’app. Usa **Progetto → Configurazione…** per scegliere l’interprete dei progetti; l’installazione predefinita usa il proprio ambiente virtuale.
5. Per un componente opzionale, scegli **PIP → Prepara automaticamente il progetto…** oppure segui il wizard proposto quando lo inserisci.

Se manca Python compatibile e Homebrew è già disponibile, l’installer prova a installare Python e Tcl/Tk tramite Homebrew. Altrimenti apre il sito ufficiale Python. Alpha, beta e release candidate non sono accettate. Tkinter non si installa con PIP.

L’installazione iniziale comprende gli strumenti dell’IDE (Jedi e PyInstaller), senza imporre tutti i pacchetti multimediali. Gli ambienti precedenti conservano le librerie già installate. Per aggiornare riesegui l’installer della nuova versione. I progetti sono file `.vtk.json` separati.

Serve una sessione grafica macOS. Apple Silicon e Intel richiedono Python, librerie e dipendenze native compatibili con l’architettura. Installer e applicazione non sono firmati o notarizzati per la distribuzione Apple.

## Inizia dal designer

1. Apri `examples/Saluto.vtk.json` oppure crea un progetto.
2. Seleziona un componente: la palette ne mostra funzioni e requisiti. Doppio clic lo inserisce.
3. Trascina per spostare; il quadrato blu ridimensiona. Le proprietà si applicano dall’ispettore.
4. Doppio clic sul componente apre il codice dell’evento. Scrivi il corpo del metodo senza `def`.
5. Salva e premi **F5**. Con dipendenze esterne, il wizard verifica l’ambiente prima dell’avvio.

Nell’evento Click di Button1:

```python
self.Button1.configure(text="Operazione completata")
self.show("Form2")
```

Scrivi `self.`, `self.Button1.` o `self.Button1.configure(` per esplorare nomi, metodi e proprietà. Ctrl+Spazio richiama i suggerimenti; Invio/Tab accetta, Esc chiude. Il pannello “cosa puoi fare” inserisce esempi al cursore. Jedi, incluso nell’installazione dell’IDE, abilita l’analisi delle librerie nell’interprete scelto. Senza Jedi rimane un fallback per Python, Tkinter standard e controlli del progetto. [Guida IntelliSense](INTELLISENSE.md).

## Webcam e pacchetti

Seleziona WebcamView: il wizard mostra **opencv-python, numpy e Pillow**, verifica il Python configurato e guida all’installazione. **Solo designer** rimanda la preparazione all’avvio del progetto. PIP non sostituisce le autorizzazioni Fotocamera né installa VLC o libusb.

[Guida completa ai pacchetti](PACCHETTI.md).

## Database con tabella pronta

Inserisci **DatabaseView**, selezionalo e scegli **Azioni → Configura componente…** nell’ispettore. SQLite non richiede PIP. Per PostgreSQL/MySQL la configurazione prepara il relativo gruppo SQLAlchemy/driver. In esecuzione, **Connetti…** apre la connessione; scegli la tabella e usa i comandi per i record.

[Guida database ed esempi CRUD](DATABASE.md). Progetto dimostrativo: `examples/Database.vtk.json`.

## Documentazione

- [IntelliSense Python e librerie](INTELLISENSE.md)
- [Pacchetti e configurazione guidata](PACCHETTI.md)
- [Database locali/remoti](DATABASE.md)
- [Componenti ed estensioni](ESTENSIONI.md)
- [Esempi](ESEMPI.md)
- [Compatibilità](COMPATIBILITA.md)
- [Verifiche e limiti](VALIDAZIONE.md)
- [Note della versione](RELEASE_NOTES.md)
- [Cronologia](CHANGELOG.md)

## Verifica e limiti

Versione 1.10.1: 85 test superati, 11 grafici saltati su macOS con Python 3.15.2 e Jedi 0.20.0. Verificati caricamento lingua, catalogo, formattazione, avvio dei moduli in inglese, conservazione dei dati ed esportazione autonoma. Il percorso grafico completo e la build macOS richiedono ancora collaudo manuale.

Il completamento dipende dalle informazioni di tipo disponibili. Il designer usa coordinate assolute e non supporta ancora l’annidamento visuale. Hardware e librerie native possono richiedere configurazioni specifiche. DatabaseView non è uno strumento di amministrazione del server.

## Menu e pannelli

I comandi Apri/Salva sono in **File**; Annulla/Ripeti in **Modifica**. In alto rimangono solo Avvia, Stop e Mostra/Nascondi log. **Vista → Ripristina pannelli** riporta palette e proprietà alle larghezze iniziali e richiude il log. Il log si apre per esecuzione e verifiche, senza poter occupare tutto il designer.

Nell’ispettore **Azioni** raccoglie configurazione del controllo, colori e carattere. **Componenti** include la creazione/importazione di controlli esterni. **PIP** comprende preparazione automatica, verifica senza installare, installazione di un pacchetto per nome ed esplorazione PyPI.

## Lingue

In Progetto → Configurazione → Aspetto scegli Italiano o English, salva e riavvia. La lingua dei componenti generati è una scelta separata, salvata nel progetto. Testi e codice esistenti non vengono tradotti.
