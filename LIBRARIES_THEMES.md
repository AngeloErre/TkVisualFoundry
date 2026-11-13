# Librerie, temi e contenitori — TkVisualFoundry 1.12

Apri **Componenti → Librerie e temi…**. La finestra presenta tutte le 19 famiglie discusse, il tipo di integrazione, i requisiti e l’ultima verifica nell’interprete selezionato. La palette dispone di un filtro per famiglia, oltre alla ricerca per nome.

## Livelli di verifica

- **Da verificare**: nessuna verifica valida per l’interprete e la configurazione correnti.
- **Installata**: requisiti/versioni e importazione verificati in un processo esterno. Questo stato non certifica il comportamento grafico.
- **Prova grafica superata**: un controllo rappresentativo è stato creato e distrutto in un processo separato, con un breve ciclo eventi. Non significa che ogni controllo, evento o combinazione di librerie sia stato collaudato.
- **Da preparare / Errore**: leggi il dettaglio e usa **Prepara con PIP…**. La prova grafica richiede una sessione grafica utilizzabile.
- Il deploy della singola libreria non viene dichiarato verificato automaticamente: occorre collaudare l’app generata su ciascuna piattaforma.

Le verifiche non importano librerie esterne nel processo dell’editor. I risultati vengono conservati nel progetto, con interprete, data e configurazione del tema; sono risultati dell’ultima verifica e possono diventare obsoleti dopo modifiche all’ambiente.

## Integrazioni disponibili

| Famiglia | Supporto in questa versione |
|---|---|
| tkinter / tkinter.ttk | Controlli standard e palette ttk ampliata: TButton, TLabel, TEntry, TCheckbutton, TRadiobutton, TScale, TSpinbox, TFrame, TLabelframe, TSeparator, TScrollbar, TMenubutton, TSizegrip e TPanedwindow; Combobox, Progressbar, Treeview e Notebook già presenti |
| CustomTkinter | Pulsanti, etichette, entry, checkbox, radio, switch, slider, progressbar, menu/combo, pulsanti segmentati, textbox, frame, frame scorrevoli e schede |
| ttkbootstrap | Temi della serie 1.x, con requisito >=1.10,<2 per conservare il catalogo di temi esistente |
| ttkthemes / sv-ttk | Motori di tema del progetto |
| Azure / Forest | Importazione locale della cartella Tcl e delle risorse; nessun download automatico |
| Pmw | ComboBox, EntryField, Counter e ScrolledText, con inizializzazione automatica |
| tkcalendar / tkinterweb | Adattatori calendario/campo data e web già presenti |
| tksheet | Sheet: dati, intestazioni, modifica celle ed eventi SheetChanged e SheetSelected |
| tkintermapview | MapView: posizione, zoom, indirizzi, marcatori, eventi MapClicked e MarkerSelected |
| tkVideoPlayer / TkinterDnD2 | Adattatori opzionali esistenti, requisiti e raccolta risorse per la build |
| Tix | Non disponibile: tkinter.tix è stato rimosso da Python 3.13; l’IDE richiede Python 3.15+ |
| PySimpleGUI / FreeSimpleGUI / guizero | Catalogati come motori separati; questa versione non genera progetti per questi framework e non li offre come widget della palette |

Le dimensioni CustomTkinter vengono passate al costruttore, come richiesto dalla libreria. L’IntelliSense usa Jedi nell’interprete scelto e dispone anche di esempi specifici per Sheet, MapView, schede e principali controlli moderni. Per accedere alle API complete degli adattatori puoi usare `.sheet`, `.map` o `.view`.

## Contenitori annidati

Seleziona un frame o un contenitore a schede, poi inserisci un controllo: il nuovo controllo viene creato al suo interno. Nell’ispettore trovi **parent** e **page**. Puoi modificare il padre usando l’elenco dei contenitori validi; le coordinate x/y sono relative al padre, quindi controllale dopo uno spostamento tra contenitori.

Sono supportati Frame, LabelFrame, Canvas, TFrame, TLabelframe, CTkFrame, CTkScrollableFrame, Notebook e CTkTabview. Per le schede scegli **Pagina visibile** nell’ispettore del contenitore. Selezionare un figlio nell’albero rende visibile la sua pagina. Il codice generato crea prima il contenitore e poi i figli; vengono impediti cicli, padri inesistenti, padri non contenitori e pagine non valide.

Duplicare un contenitore copia anche i discendenti; eliminare un contenitore elimina il suo sottoalbero. La duplicazione del form rimappa i riferimenti ai padri. Il codice degli eventi resta invariato: aggiorna eventuali riferimenti ai nomi originali. La rimozione/rinomina di una pagina che contiene controlli viene rifiutata finché i figli non vengono spostati.

L’anteprima rimane schematica e non carica componenti esterni o servizi di rete nel designer. Non rappresenta con precisione stile, bordi, scorrimento e ritaglio dei contenitori. I pannelli TPanedwindow si gestiscono da codice con la sua API; l’editor visuale non crea ancora le singole sezioni del pannello.

## Temi del progetto

Apri **Vista → Tema applicazione…** oppure il pulsante nel gestore librerie. Scegli un solo motore ttk: none, ttkbootstrap, ttkthemes, sv-ttk, Azure o Forest. Le opzioni disponibili si aggiornano in base al motore. CustomTkinter ha una scelta separata System/Light/Dark. Queste impostazioni riguardano l’app generata; i colori dell’IDE restano nelle preferenze dell’ambiente.

Un tema ttk non cambia automaticamente i widget Tk classici o i controlli CustomTkinter. Per un’app visivamente coerente, usa soprattutto una famiglia di controlli.

Per Azure/Forest scarica ed estrai il tema dalla sua sorgente ufficiale, quindi seleziona **Importa cartella tema…**. La cartella deve contenere `azure.tcl`, oppure `forest-light.tcl` e `forest-dark.tcl`, insieme alle immagini richieste. Viene copiata in una nuova cartella `themes/` del progetto e inclusa nel deploy. Non vengono sovrascritte cartelle precedenti. Il limite di importazione è 2000 file / 50 MB. File nascosti e collegamenti simbolici vengono esclusi.

Fonti: [Azure](https://github.com/rdbende/Azure-ttk-theme), [Forest](https://github.com/rdbende/Forest-ttk-theme), [Sun Valley](https://github.com/rdbende/Sun-Valley-ttk-theme), [ttkthemes](https://ttkthemes.readthedocs.io/). Conserva le licenze dei temi e delle librerie che distribuisci.

## Deploy e collaudo

Il kit include il codice degli adattatori e del motore di tema. Il driver PyInstaller raccoglie i dati delle librerie attive: temi, font, Tcl e risorse native, oltre agli import necessari. Per Azure e Forest devi includere l’intera cartella del tema, non solo il Tcl. Per mappe e geocodifica possono servire connessione di rete e servizi esterni; driver, codec e autorizzazioni restano requisiti separati.

Prova `examples/Libraries/NestedLibraries.vtk.json` (Notebook, frame ttk/CTk, tabella e Sun Valley) e `MapExample.vtk.json`. Preparare i pacchetti, superare un import o compilare la build non sostituisce il collaudo grafico su Mac e Windows.
