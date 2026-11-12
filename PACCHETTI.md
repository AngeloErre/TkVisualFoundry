# Pacchetti PIP: configurazione guidata

## Webcam: percorso facilitato

1. Nella palette seleziona **WebcamView**. La descrizione anticipa i requisiti: **opencv-python, NumPy e Pillow**.
2. Doppio clic oppure **Inserisci nel form** apre il wizard, prima di creare il controllo.
3. Il wizard mostra il Python di destinazione e verifica versioni e import. Se mancano pacchetti, premi **Installa / ripara**.
4. Attendi l’output di PIP, il controllo dei conflitti (`pip check`) e la verifica finale. Il pulsante **Continua** si abilita solo se i requisiti risultano pronti.
5. Inserisci il controllo e avvia il progetto. Nel componente premi **Avvia webcam**; autorizza la Fotocamera nelle impostazioni di macOS se richiesto.

**Solo designer** consente di disegnare subito senza installare nulla. Non significa che il componente sia pronto per l’esecuzione. Avvia/Debug propone nuovamente il wizard quando il progetto contiene dipendenze esterne.

## Altri punti di accesso

- Pulsante **Pacchetti PIP…** in alto: intero progetto oppure un componente del catalogo.
- **Configura componente / dipendenze…** nell’ispettore: requisiti del controllo selezionato.
- **Librerie → Esplora PyPI**: consulta un pacchetto per nome esatto; **Installa versione selezionata** apre lo stesso wizard.
- **Configurazione → Pacchetti e componenti**: scegli se mostrare i requisiti prima dell’inserimento, prima dell’avvio e se preferire distribuzioni precompilate.

I pacchetti vengono installati nel Python indicato dal wizard, che è lo stesso configurato per eseguire i progetti. Cambialo in **Configurazione → Python e designer**. L’installer iniziale prepara l’ambiente dell’IDE; i pacchetti opzionali sono installati su richiesta. Gli ambienti esistenti conservano i pacchetti già presenti.

## Cosa verifica il wizard

- Presenza della distribuzione e rispetto dei vincoli di versione.
- Import effettivo per le librerie note (ad esempio NumPy, OpenCV, Pillow e driver database).
- Per pacchetti sconosciuti: metadati/versione; il codice esterno non viene importato automaticamente.
- Dopo un’installazione, esito del comando, `pip check` e nuovo controllo dei requisiti.
- Se PIP manca, prova a predisporlo con `ensurepip` durante l’installazione.

Le installazioni e le verifiche avvengono in background. Puoi interrompere l’installazione; i pacchetti già scritti restano installati e devono essere verificati nuovamente. Se un import risulta guasto, **Installa / ripara** forza la reinstallazione dei requisiti mostrati. Il wizard non disinstalla automaticamente pacchetti estranei per risolvere conflitti.

## Errori comuni

| Stato | Come procedere |
|---|---|
| Mancante | Premi Installa / ripara |
| Versione fuori requisito | Lascia che PIP risolva i vincoli dell’intero gruppo |
| Import fallito | Prova Installa / ripara e rileggi il log |
| Nessuna distribuzione compatibile | Cerca una versione compatibile con Python/architettura; se sai predisporre compilatori e librerie, disattiva “solo precompilati” |
| `pip check` segnala conflitti | Usa un ambiente virtuale dedicato o correggi i vincoli; il wizard non dichiara riuscita l’installazione |
| PIP assente e ensurepip non disponibile | Scegli un Python ufficiale con PIP oppure un ambiente virtuale funzionante |
| Rete non disponibile | Ripristina la connessione e riprova |
| Pacchetti pronti ma periferica non funziona | Verifica autorizzazioni, dispositivo e librerie native |

USBExplorer richiede anche **libusb**; i componenti VLC richiedono **VLC/libVLC**. Queste dipendenze native sono indicate prima dell’uso e non sono installate dal wizard PIP. Il controllo dei pacchetti non equivale a un collaudo di webcam, USB, audio o server remoti.

Riferimenti tecnici: [OpenCV su PyPI](https://pypi.org/project/opencv-python/), [PIP](https://pip.pypa.io/en/stable/).
