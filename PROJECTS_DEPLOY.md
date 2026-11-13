# File di progetto e deploy — VisualTk Studio 1.11

## Esplora progetto

La scheda Progetto della barra laterale contiene **Form e componenti** e **File e cartelle**. Salva prima il progetto `.vtk.json`: la cartella che lo contiene diventa la cartella di lavoro. È consigliata una cartella dedicata per ogni applicazione.

Il menu **File e cartelle** permette di creare file e cartelle, importare un file, rinominare, spostare nel cestino e aggiornare la vista. La nuova voce viene creata nella cartella selezionata, oppure accanto al file selezionato. Il doppio clic apre un editor per file UTF-8 fino a 2 MB. Salva e chiudi gli editor prima di generare il deploy. Alla chiusura dell’IDE o al cambio di progetto viene chiesto di salvare i file modificati.

La vista mostra al massimo 1500 elementi e omette cartelle nascoste, ambienti virtuali, build e dist. I collegamenti simbolici non sono supportati. Il cestino è `.visualtk-trash` nella cartella del progetto: i file conservano un prefisso temporale e possono essere recuperati manualmente. Le operazioni sul disco non vengono annullate da Undo. Rinomina e cancellazione non aggiornano import o percorsi nel codice: correggili prima di eseguire il progetto.

Un segno **✓** indica che il file o la cartella sono inclusi nel deploy. I file creati/importati vengono inclusi automaticamente. Per file già presenti, usa **Includi / escludi dal deploy**. Includere una cartella include ricorsivamente i suoi file visibili, esclusi gli elementi tecnici sopra indicati. Per escludere un suo singolo file, rimuovi l’inclusione della cartella e seleziona soltanto i file necessari. `main.py` è riservato al sorgente esportato. I moduli Python locali inclusi possono essere importati negli import del progetto; le altre librerie devono essere dichiarate tra i requisiti PIP.

I percorsi restano relativi alla cartella del progetto. Per spostare un progetto con risorse, copia l’intera cartella e apri la copia. Non spostare soltanto il JSON con Salva con nome. I percorsi assoluti a risorse esterne non vengono convertiti o copiati automaticamente.

## Genera deploy

Premi **Deploy…**, scegli un nome tecnico dell’app (lettere, cifre, trattino o underscore, iniziale alfabetica), una versione numerica e una destinazione. Il kit viene creato in una nuova sottocartella `Nome-Versione`; una cartella esistente non viene sovrascritta. La cartella di output non può trovarsi dentro una risorsa inclusa.

Il kit comprende `src/main.py`, i file scelti, `project.vtk.json`, requisiti PIP, metadati e README. Non è un’app già compilata. L’opzione **Compila anche su questo computer** avvia la build nel Python selezionato e mostra l’output nel log. Il kit prepara un ambiente `.venv` separato e installa dipendenze e PyInstaller; occorre una connessione Internet per la prima preparazione.

| Sistema | Avvio da sorgente | Build | Installazione |
|---|---|---|---|
| macOS | Run_Mac.command | Build_Mac.command → .app e .dmg | Install_Mac.command → ~/Applications |
| Windows | Run_Windows.cmd | Build_Windows.cmd → cartella .exe e ZIP; Setup se Inno Setup è disponibile | Install_Windows.cmd → avvia Setup |

Serve Python stabile 3.15+ con Tkinter sul computer di build. Se gli script non trovano quello corretto, imposta `VTS_PYTHON` con il percorso dell’interprete. Il Mac compila per macOS; per ottenere il pacchetto Windows trasferisci il kit su Windows e avvia lo script Windows. Anche l’architettura di destinazione deve essere compatibile con quella usata per la build.

Per il Setup Windows installa [Inno Setup](https://jrsoftware.org/isinfo.php). Il kit include `Installer_Windows.iss`; il driver cerca `ISCC` nel PATH e nelle cartelle di installazione comuni. Senza Inno Setup viene comunque generato lo ZIP portabile. Distribuisci tutta la cartella dell’app, non soltanto l’exe.

L’utente finale dell’app compilata non necessita di Python. Restano separati driver, VLC/libVLC, autorizzazioni della webcam e altre librerie native. Le build non sono firmate per distribuzione pubblica né notarizzate; il Mac applica una firma ad hoc dopo l’inserimento della descrizione fotocamera. Firma Apple/Microsoft e notarizzazione richiedono un processo successivo.

Le risorse vengono raccolte accanto ai sorgenti e nei dati del bundle. Usa percorsi relativi per leggerle. Salva database modificabili e dati persistenti in una cartella utente scrivibile, non dentro il bundle. Verifica il contenuto prima di distribuire; credenziali e file privati devono restare esclusi. Import dinamici o librerie particolari possono richiedere hook aggiuntivi in `deploy_build.py`. Collauda ogni build su un computer di destinazione pulito.

Se il sistema non permette la creazione del DMG, il driver conserva l’app e produce uno ZIP Mac con `ditto`.


## Icona applicazione

Il wizard Deploy consente di scegliere PNG/ICO/ICNS quadrata da 256–4096 px e mostra un’anteprima. L’IDE importa una copia in assets/app-icons, memorizza il percorso relativo e converte automaticamente ICNS/ICO/PNG per bundle Mac, eseguibile/Setup Windows e finestre Tk. Non occorre marcare manualmente queste icone per includerle nel kit. Rimuovi azzera la selezione senza cancellare i file importati. Copia l’intera cartella quando sposti il progetto; rinomina/cestino dal gestore file aggiornano il riferimento. L’aspetto finale va verificato sul sistema di destinazione.
