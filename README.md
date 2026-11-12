# VisualTk Studio 1.6

Ambiente RAD scritto in Python, ispirato al flusso di lavoro di Visual Basic 6, per creare applicazioni Tkinter. È una prima implementazione utilizzabile e modificabile, non una replica completa dell'IDE Microsoft.

## Funzionalità principali

| Area | Funzioni |
|---|---|
| Designer visuale | Palette, trascinamento, ridimensionamento, proprietà, colori e font |
| Progetti con più form | Creazione, apertura, duplicazione, eliminazione e navigazione tra finestre |
| Editor eventi | Codice Python associato ai componenti, sintassi colorata e indentazione |
| Assistente codice 1.6 | Completamento contestuale, proprietà di configure, firme e frammenti con spiegazioni in italiano |
| Componenti esterni | Procedura guidata, descrittori JSON ed esploratore PyPI |
| Multimedia e periferiche | Gallerie immagini, audio, webcam, USB e seriale tramite dipendenze opzionali |
| Web e video | Adattatori HTML/web, VLC e risoluzione stream YouTube |
| Esecuzione e debug | Processo separato, output, breakpoint e strumenti pdb |
| Esportazione | Generazione Python e packaging con PyInstaller |
| Personalizzazione IDE | Temi Chiaro, Scuro, Seppia e colori persistenti |
| Help | Manuale, esempi, ricerca e diagnostica dipendenze |

## Esempio: evento Click di Button1

```python
self.Button1.configure(text="Operazione completata")
self.show("Form2")
```

Scrivi `self.` per esplorare il progetto, `self.Button1.` per i metodi e `self.Button1.configure(` per le opzioni. Ctrl+Spazio richiama i suggerimenti; Invio/Tab accetta ed Esc chiude. Il pannello “cosa puoi fare” propone esempi per il componente e l’evento selezionati.

## Documentazione

- [Novità e cronologia](CHANGELOG.md)
- [Descrizione della versione 1.6](RELEASE_NOTES.md)
- [Componenti esterni](ESTENSIONI.md)
- [Progetti dimostrativi](ESEMPI.md)
- [Compatibilità](COMPATIBILITA.md)
- [Verifiche e limiti](VALIDAZIONE.md)

## Stato del progetto

Versione **1.6**, in sviluppo. Ultima verifica locale: **33 test superati e 6 grafici saltati**. Designer, popup di completamento, debugger interattivo, installer e integrazioni hardware richiedono collaudo in una sessione grafica sul Mac. Layout a coordinate assolute; non è una replica integrale di VB6. Le librerie esterne possono richiedere dipendenze native, ad esempio VLC o libusb. Il supporto a Python 3.15 delle singole integrazioni va verificato separatamente.

## Installazione su Mac

1. Estrai tutto lo ZIP in una cartella scrivibile.
2. Fai doppio clic su **Install_Mac.command**. In alternativa apri Terminale nella cartella ed esegui `bash Install_Mac.command`.
3. L'installer crea un ambiente Python isolato, installa Jedi, PyInstaller e le dipendenze multimediali e aggiunge **VisualTk Studio.app** a `~/Applications`.
4. Se Python con Tk manca ma Homebrew è presente, installa automaticamente Python 3.15 e python-tk. Se mancano entrambi, apre il sito ufficiale Python: installa il pacchetto macOS di Python 3.15 e rilancia lo script. Non installa Homebrew o software di sistema senza un gestore già presente.

Servono una connessione Internet e una sessione grafica macOS attiva. Sono supportati Mac Apple Silicon e Intel con Python/Tk compatibili. Gli script non sono firmati né notarizzati: eventuali richieste di macOS vanno gestite tramite le normali impostazioni di sicurezza. Non è incluso un pacchetto .pkg firmato.

Per eseguire direttamente i sorgenti con Python 3.15 stabile o successivo e Tk 8.6+: `python3 studio.py`. L'IDE base usa la libreria standard; Jedi migliora il completamento e PyInstaller serve per il packaging. Tkinter non si installa con pip.

## Prova in due minuti

Apri `examples/Saluto.vtk.json`, premi F5, inserisci il nome e premi Saluta. Il secondo pulsante apre una seconda finestra. Chiudi la prima finestra per terminare l'applicazione.

Per creare un progetto:

- Aggiungi i controlli dalla palette con doppio clic o con il pulsante dedicato.
- Trascina per spostare e trascina il quadratino blu per ridimensionare. Le frecce spostano di un pixel.
- Modifica colori, dimensioni, testo, font e stato nel pannello Proprietà; premi Applica.
- Doppio clic sul controllo apre il codice dell'evento. Scrivi il corpo del metodo, senza `def`: per esempio `self.Label1.configure(text=self.Entry1.get())`.
- Gli oggetti sono attributi dell'applicazione. `self.show("Form2")` apre una finestra e `self.hide("Form2")` la nasconde. La prima finestra chiude tutto; le altre si nascondono.
- Il menu Progetto contiene import/funzioni globali e codice di avvio. Le finestre sono inizialmente nascoste; il codice di avvio mostra Form1.
- Ctrl+Spazio propone completamenti Jedi e i nomi dei componenti. Non è un assistente generativo: la comprensione dei tipi dei componenti dinamici è limitata.
- Salva come `.vtk.json`; Esporta Python genera un'applicazione indipendente dall'IDE che richiede solo Python/Tk (oltre alle librerie che aggiungi tu).

## Nuove estensioni della versione 1.3

Il menu **Help** include guida rapida (F1), manuale, esempi cercabili, compatibilità, accesso alla cartella esempi e diagnostica dell’interprete. La palette comprende ora anche Treeview, Notebook, ScrolledText, file drop, dialoghi, HTML/web, video/YouTube, calendari e controlli CustomTkinter. **Librerie → Tema del progetto** imposta un tema ttkbootstrap per il codice generato.

Consulta `COMPATIBILITA.md` per requisiti e limiti delle nuove integrazioni e `ESEMPI.md` per il codice degli eventi. Consulta `ESTENSIONI.md` per i cinque componenti multimediali/periferiche, il registro di componenti esterni e l’esploratore PyPI. Il menu **Librerie** consente di importare descrittori, vedere i componenti registrati e installare le dipendenze del progetto. Il runtime dei componenti integrati viene incluso direttamente nel Python esportato; viene scritto anche `requirements-visualtk.txt`.

## Componenti ed eventi

Button, Label, Entry, Text, Checkbutton, Radiobutton, Listbox, Combobox, Scale, Spinbox, Frame, Canvas, Progressbar. Sono configurabili le proprietà esposte per ciascun tipo; proprietà Tk aggiuntive si possono impostare nel codice Load con `configure(...)`.

Eventi: Click, DoubleClick, Enter, Leave, KeyPress, FocusIn, FocusOut, Change e Load. Change è `<<ComboboxSelected>>`, quindi serve per Combobox; non è una notifica universale di modifica. Click corrisponde a `<Button-1>`: per attivazione da tastiera o comandi semantici usa `self.Button1.configure(command=...)` in Load. Load parte una volta, all'avvio del loop. `event` contiene i dati Tk dell'evento; in Load vale None.

Il designer rappresenta i componenti come sagome modificabili; l'applicazione avviata usa veri widget Tkinter. Su macOS alcuni colori dei pulsanti possono dipendere dal tema nativo.

## Debug

F9 avvia il debugger Python `pdb` in un processo separato. Nel pannello Python generato, doppio clic su una riga eseguibile aggiunge o rimuove un breakpoint. Premi Continua per avviare la finestra, poi aziona il componente. Quando il debugger si ferma, usa Passo, Entra, Stack, Locali, o digita comandi nella riga sotto l'output:

```python
p self.Entry1.get()
pp locals()
break 35
continue
quit
```

I breakpoint sono numeri di riga del Python generato e valgono nella sessione corrente: vanno ricontrollati dopo modifiche strutturali. La GUI dell'app in debug resta ferma mentre pdb attende un comando. Gli errori callback sono mostrati con finestra di errore e traceback nell'output. Non sono presenti watch persistenti, breakpoint condizionali grafici o attach a processi esistenti (i comandi pdb sono comunque disponibili). Shift-F5 termina il processo.

## Verifica e compilazione

Verifica controlla modello e sintassi Python. Build .app esegue PyInstaller nell'interprete impostato e mostra il risultato nell'output; su macOS produce `dist/VisualTkApplication.app`. Non è compilazione nativa del sorgente: è packaging con runtime incluso. Le build si producono sul sistema di destinazione; risorse esterne e import dinamici particolari richiedono una configurazione PyInstaller dedicata.

Il packaging dei progetti aggiunge la descrizione di utilizzo fotocamera al bundle macOS e applica una firma locale ad hoc, che non equivale a una firma Developer ID o alla notarizzazione.

Per creare un DMG dello stesso IDE, dopo l'installazione esegui `bash ~/Applications/VisualTkStudio/Build_Mac.command`. La versione congelata richiede un interprete esterno nelle impostazioni per avviare, debuggare e impacchettare i progetti; il launcher installato usa già l'ambiente corretto. Firma Developer ID, notarizzazione e distribuzione commerciale richiedono credenziali Apple e passaggi ulteriori.

## Impostazioni e limiti

Menu Modifica → Impostazioni: griglia, dimensione font del codice, percorso interprete. Sono salvate in `~/.visualtkstudio.json`. Salvataggio atomico del progetto, annulla/ripeti fino a 100 modifiche, conferma modifiche non salvate.

Layout assoluto in pixel: non sono presenti layout responsivi, controlli annidati nei Frame, menu dell'applicazione progettati visualmente, immagini nel designer, componenti ActiveX, import di progetti VB6, refactoring dei nomi, selezione multipla, gestione automatica delle dipendenze dei progetti o marketplace. Il nome Python è assegnato alla creazione e resta fisso per preservare il codice manuale. Allinea X/Y porta il componente all'origine sull'asse scelto. Il codice del progetto è codice Python arbitrario: esegui progetti di cui conosci l'origine.

## Test

`python3 -m unittest discover -s tests -v`

La suite controlla generazione, persistenza anche di codice incompleto, vincoli sui nomi e — quando esiste una sessione grafica — widget, eventi, designer, undo/redo, processo standalone e breakpoint pdb. Consulta `VALIDAZIONE.md` per il risultato effettivamente ottenuto nell'ambiente di produzione del pacchetto.

## Struttura

- `studio.py`: IDE, designer, editor, gestione processi e debugger.
- `core.py`: modello JSON, validazione e generazione Python.
- `components.py`: registro dichiarativo e dipendenze dei componenti.
- `visualtk_runtime.py`: componenti immagini, audio, webcam, USB e seriale.
- `library_explorer.py`: catalogo e metadati PyPI.
- `build_project.py`: packaging dei progetti con metadati privacy macOS.
- `Install_Mac.command`: installazione con ambiente isolato e launcher .app.
- `Build_Mac.command`: creazione app congelata e DMG sul Mac.
- `Start.command`: avvio rapido.
- `examples/`: progetto e sorgente generato dimostrativi.
- `tests/`: test automatici.

Documentazione delle dipendenze: https://docs.python.org/3/library/tkinter.html — https://docs.python.org/3/library/pdb.html — https://jedi.readthedocs.io/ — https://pyinstaller.org/en/stable/usage.html — https://formulae.brew.sh/formula/python-tk@3.15

La versione 1.3 installa anche requirements-integrations.txt. VLC/libVLC richiede installazione separata. I componenti legacy tkVideoPlayer/pytube sono opzionali; cefpython3 resta escluso dal runtime moderno. I menu di Help e gli esempi sono disponibili anche nella distribuzione congelata.

## Requisito Python dalla versione 1.3

IDE, interprete dei progetti e build richiedono Python >=3.15 in versione final. Alpha, beta e release candidate vengono rifiutate, anche se numericamente superiori. L’installer seleziona Python 3.15 stabile e conserva un eventuale vecchio ambiente virtuale in una cartella di backup prima di ricrearlo. Non modifica né rimuove le installazioni Python di sistema.

Il backend MP3 usa ora pygame-ce>=2.5.8, mantenendo import pygame; PyInstaller richiede almeno 6.22.3. Non installare pygame e pygame-ce insieme nello stesso ambiente. Non è ancora stato eseguito il collaudo completo su Python 3.15.

### Diagnosi Python già installato

Il nome della cartella 3.15 non prova che il runtime sia stabile: `python3.15 --version` può restituire 3.15.0rc3. La versione 1.3.1 mostra il numero completo, distingue prerelease da assenza di Python e segnala separatamente Tkinter non disponibile. In caso di rc3 installare la release final da https://www.python.org/downloads/release/python-3150/ e rieseguire l’installer.

## Interfaccia 1.4
Palette chiara, editor scuri coordinati, ricerca componenti, toolbar gerarchica, schede e albero più leggibili. La ricerca filtra i nomi dei componenti; cancellare il testo ripristina la palette completa.

## Novità 1.5 — componenti, form e personalizzazione
- **+ Componente esterno…** sotto la palette: procedura guidata per nome, modulo, classe, pacchetti PyPI e proprietà JSON. Sono supportate classi compatibili con Tkinter (master, place e bind); librerie non grafiche richiedono un adattatore. Il modulo deve essere installato nell’interprete configurato: Librerie → Installa dipendenze progetto dopo aver inserito il controllo nel form. I descrittori sono salvati nel progetto.
- **Librerie → Esplora PyPI**: catalogo online e dettagli per nome esatto; il nuovo pulsante apre la procedura guidata. Installare una libreria non crea automaticamente un controllo. È disponibile anche l’importazione dei descrittori JSON.
- **Progetto → Gestione form…** oppure **Form…** nel designer: creazione, apertura, duplicazione e rimozione. Il form principale non può essere rimosso. La copia assegna nomi univoci ai controlli e conserva il codice: aggiornare manualmente eventuali riferimenti ai controlli originali. Per passare da una finestra all’altra usare `self.show("Form2")` e `self.hide("Form2")` nel codice evento.
- **Modifica → Aspetto ambiente…**: preset Chiaro, Scuro e Seppia, con selettori per sfondo pannelli, testo, superficie controlli, accento, sfondo/testo editor e sfondo designer. Le preferenze sono applicate subito e conservate tra gli avvii. I colori dei progetti restano gestiti nelle proprietà; finestre native macOS e colorazione sintassi seguono impostazioni proprie.
- Verifica: 28 test superati, 6 grafici saltati. Nuove finestre e aspetto richiedono collaudo manuale sul Mac.

## Assistente codice 1.6
Apri un evento con doppio clic sul controllo, quindi scegli ad esempio Click.
Il pannello **cosa puoi fare** mostra esempi contestuali. Seleziona una voce per leggerne la spiegazione; usa **Inserisci esempio** o doppio clic per inserirla nel codice. Un corpo contenente solo `pass` viene sostituito; altrimenti il frammento viene inserito al cursore o sostituisce la selezione. Gli esempi sono modificabili e non sono applicati al componente finché non esegui il progetto.

Esempio Button1 → Click:
```python
self.Button1.configure(text='Nuovo testo')
self.Button1.configure(state='disabled')
messagebox.showinfo('Informazione', 'Operazione completata')
```
- Scrivi `self.`: suggerisce i componenti e i form del progetto.
- Scrivi `self.Button1.`: suggerisce metodi con descrizioni.
- Scrivi `self.Button1.configure(` oppure `self.Button1.configure(te`: propone opzioni come `text=` e mostra l’elenco proprietà.
- **Ctrl+Spazio** richiama il completamento; **↑/↓** selezionano, **Invio/Tab** accettano, **Esc** chiude. Puoi anche fare clic su un suggerimento. Le proposte automatiche appaiono dopo una breve pausa.
- Entry, Text, Combobox, Listbox, Scale, Progressbar, Treeview e Canvas hanno suggerimenti specifici. Le finestre propongono titolo, dimensioni, mostra/nascondi.
- Per i componenti esterni vengono lette le proprietà del descrittore e del progetto, senza caricarne il codice. Metodi specifici delle librerie esterne non sono rilevati automaticamente; il completamento non equivale a una verifica di compatibilità del componente.
- Jedi è opzionale per il completamento Python generale richiamato manualmente. I suggerimenti Tkinter funzionano anche senza Jedi.

Verifica 1.6: 33 test superati, 6 grafici saltati. Popup, navigazione da tastiera e inserimento nell’editor richiedono ancora una prova grafica sul Mac.
