# VisualTk Studio 1.7

La versione 1.7 rende visibili e guidate le operazioni di configurazione e preparazione dei componenti, e introduce un controllo database pronto all’uso.

## Miglioramenti principali

- Centro Configurazione con Python, designer, preferenze PIP e accesso ai temi.
- Wizard PIP con verifica automatica iniziale, requisiti espliciti, installazione in background, output, interruzione e verifica finale.
- Requisiti mostrati prima dell’inserimento di un controllo; scelta Solo designer per rimandare l’installazione.
- WebcamView include esplicitamente NumPy, OpenCV e Pillow.
- Esploratore PyPI collegato allo stesso wizard per i pacchetti selezionati.
- Installer base più leggero, con integrazioni opzionali predisposte dall’IDE.
- DatabaseView: SQLite senza dipendenze aggiuntive; PostgreSQL e MySQL tramite SQLAlchemy e driver dedicati.
- Griglia, elenco tabelle, editor record e operazioni parametrizzate in transazione. Password solo a runtime o da variabile ambiente.
- Esempi CRUD nell’assistente, nuovo progetto Database e guide integrate nell’Help.
- Palette informativa, ispettore proprietà scorrevole e toolbar su due righe.

## Validazione

50 test superati; 8 grafici saltati su Python 3.15.2. Test SQLite reali e simulazioni per flusso PIP/connessione remota. GUI, installazioni live, server PostgreSQL/MySQL, periferiche e packaging richiedono collaudo dedicato.

## Aggiornamento

Estrai i sorgenti ed esegui Install_Mac.command. Le preferenze esistenti vengono mantenute; le nuove opzioni hanno valori predefiniti. I progetti precedenti restano leggibili. I pacchetti già installati non vengono rimossi.

## Descrizione breve

IDE visuale Python/Tkinter per macOS con designer multi-form, assistente codice, wizard PIP, componenti multimediali e database SQLite/PostgreSQL/MySQL con tabella e CRUD.
