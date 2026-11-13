# VisualTk Studio 1.8

Ambiente visuale per creare applicazioni Python/Tkinter, ispirato al flusso di lavoro di Visual Basic 6 e pensato principalmente per macOS. Disegna i form, modifica le proprietà, scrivi il codice degli eventi e avvia il progetto dall’IDE.

## Novità 1.8

- **Palette con icone** Tk native per i componenti, ricerca e inserimento con doppio clic o Invio.
- **Barra compatta di menu a tendina**: File, Modifica, Progetto, Esegui, PIP, Componenti, Vista e Help, visibili dentro la finestra anche su Mac.
- **Inserisci nel form** e **Applica proprietà** fissati sopra le rispettive aree scorrevoli.
- **Log richiudibile**, nascosto all’apertura, con altezza limitata per preservare lo spazio del designer.
- **PIP automatico**: controlla, installa se necessario, verifica e continua l’inserimento o l’avvio senza premere ogni volta Continua.
- Preferenza per pacchetti precompilati senza escludere quelli sorgenti. La modalità “solo wheel” rimane un’opzione avanzata.
- Finestra PIP a schede, pulsanti sempre riservati nel layout, log dettagliato e interruzione.

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

Scrivi `self.`, `self.Button1.` o `self.Button1.configure(` per esplorare nomi, metodi e proprietà. Ctrl+Spazio richiama i suggerimenti; Invio/Tab accetta, Esc chiude. Il pannello “cosa puoi fare” inserisce esempi al cursore. Jedi è opzionale per i suggerimenti Python generali; il completamento contestuale Tkinter funziona anche senza Jedi.

## Webcam e pacchetti

Seleziona WebcamView: il wizard mostra **opencv-python, numpy e Pillow**, verifica il Python configurato e guida all’installazione. **Solo designer** rimanda la preparazione all’avvio del progetto. PIP non sostituisce le autorizzazioni Fotocamera né installa VLC o libusb.

[Guida completa ai pacchetti](PACCHETTI.md).

## Database con tabella pronta

Inserisci **DatabaseView**, selezionalo e scegli **Azioni → Configura componente…** nell’ispettore. SQLite non richiede PIP. Per PostgreSQL/MySQL la configurazione prepara il relativo gruppo SQLAlchemy/driver. In esecuzione, **Connetti…** apre la connessione; scegli la tabella e usa i comandi per i record.

[Guida database ed esempi CRUD](DATABASE.md). Progetto dimostrativo: `examples/Database.vtk.json`.

## Documentazione

- [Pacchetti e configurazione guidata](PACCHETTI.md)
- [Database locali/remoti](DATABASE.md)
- [Componenti ed estensioni](ESTENSIONI.md)
- [Esempi](ESEMPI.md)
- [Compatibilità](COMPATIBILITA.md)
- [Verifiche e limiti](VALIDAZIONE.md)
- [Note della versione](RELEASE_NOTES.md)
- [Cronologia](CHANGELOG.md)

## Verifica e limiti

Versione in sviluppo: **58 test superati, 10 grafici saltati**, con Python 3.15.2. Verificati SQLite reale, transazioni, chiavi, generazione, dipendenze e flusso di installazione simulato. Eseguita anche un’installazione PIP reale da un wheel di prova locale in un ambiente temporaneo isolato, con verifica finale dell’import. Non sono stati eseguiti collaudi GUI, download PIP da Internet, connessioni a server remoti o build `.app` in questa sessione.

Il designer usa coordinate assolute. I contenitori non consentono ancora l’annidamento visuale dei controlli. Installare una libreria non crea automaticamente il relativo widget: occorre una classe Tkinter compatibile o un adattatore. Le funzioni hardware dipendono da driver, librerie native e autorizzazioni. DatabaseView copre tabelle dello schema predefinito e tipi comuni, senza amministrazione del server o migrazioni.

Per eseguire i sorgenti: `python3 studio.py`. Per i test: `python3 -m unittest discover -s tests -v`. Per preparare l’app dell’IDE sul Mac: `Build_Mac.command` dalla cartella installata con `.venv`; il packaging deve essere collaudato sul sistema di destinazione.

## Menu e pannelli

I comandi Apri/Salva sono in **File**; Annulla/Ripeti in **Modifica**. In alto rimangono solo Avvia, Stop e Mostra/Nascondi log. **Vista → Ripristina pannelli** riporta palette e proprietà alle larghezze iniziali e richiude il log. Il log si apre per esecuzione e verifiche, senza poter occupare tutto il designer.

Nell’ispettore **Azioni** raccoglie configurazione del controllo, colori e carattere. **Componenti** include la creazione/importazione di controlli esterni. **PIP** comprende preparazione automatica, verifica senza installare, installazione di un pacchetto per nome ed esplorazione PyPI.
