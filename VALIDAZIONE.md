# TkVisualFoundry 1.30

251 test superati per lingua, 11 grafici saltati. Rinomina di UI/documentazione, header generati e pacchetti; compatibilità di storage e ownership mantenuta. Nuove regressioni sui launcher Mac precedenti e rifiuto di registrazione dalla cartella già installata. 15 esempi compilati. Collaudo grafico, migrazione Windows e installazione nativa ancora da completare.

# Versione 1.29

249 test superati per lingua, 11 grafici saltati. Cambio frame pdb reale con locali/Watch e rifiuto di richieste obsolete; pianificazione e disinstallazione effettiva in cartelle temporanee con conservazione di progetti, file modificati e cartelle personali vuote. Verificata sintassi shell dei kit e configurazione uninstall di Inno Setup. Controllo desktop non disponibile: collaudo grafico e installazione/disinstallazione Windows nativa ancora da eseguire. Nessuna installazione reale dell’utente rimossa.

# Versione 1.28

242 test superati per lingua, 11 grafici saltati. Verificati percorsi con ambito e indici/chiavi letterali, rifiuto di chiamate/espressioni eseguibili, dati mancanti/troncati, rinomina e salvataggio, cambio di proprietà della sessione aprendo un altro progetto. Un processo reale produce campioni con valore globale osservato che cambia. Collaudo grafico ancora da completare.

# Versione 1.27

235 test superati per lingua, 11 grafici saltati. Verificati offset dei runtime incorporati, posizioni evento/startup/import, righe non eseguibili, inserimento/sostituzione/eliminazione, rinomina e salvataggio/caricamento. Un processo pdb reale si è fermato nel metodo evento generato senza creare Tk. Marcatori e scorciatoia grafica ancora da collaudare.

# Versione 1.26

230 test superati per lingua, 11 grafici saltati. Verificati aggiornamento reale di globali/attributi self, locali all’uscita dalle funzioni, pausa/next di pdb, breakpoint con variabili locali e stack, limiti/cicli, assenza di repr/proprietà personalizzate e chiusura sessioni obsolete. Campionamento circa ogni 0,5 s, non traccia completa delle assegnazioni. Collaudo grafico ancora da eseguire.

# Versione 1.25

224 test superati per lingua, 11 grafici saltati. Verificati processo pdb reale senza GUI, prompt frammentati, percorsi macOS equivalenti, frame esterni, buffer limitato, isolamento sessioni, reset marcatori e confronto esatto del sorgente. Interazione grafica di debug ancora da collaudare.

# Versione 1.24

218 test superati per lingua, 11 grafici saltati. Nuove regressioni: generazione indipendente per pagina Notebook, prima apertura dopo ridimensionamento, calibrazione area interna, cancellazione callback alla distruzione. Ridimensionamento grafico e temi reali ancora da collaudare. 14 esempi validati e compilati.

# Versione 1.23

216 test superati per lingua, 11 grafici saltati. Verificate geometria ancorata a destra/basso, espansione/minimi, centratura, posizione fissa, helper incorporato, contenitori non supportati e accorpamento degli eventi senza sostituire binding esistenti. Non verificata interazione grafica di ridimensionamento. Supporto limitato alla prima fase Tk/ttk su form/frame ordinari.

# Versione 1.22

211 test superati per lingua, 11 grafici saltati. Nuove regressioni per copia del buffer eventi senza modifica del modello, sintassi incompleta, deduplicazione/limite versioni, errori di scrittura, copie corrotte, limiti dei confronti e nomi di recupero anche dopo il salvataggio del lavoro corrente. Non eseguita simulazione grafica completa di crash/ripristino.

# Versione 1.21

204 test superati per lingua, 11 grafici saltati. Nuove regressioni per riferimenti statici/metodi evento, nomi form e parent, posizioni Unicode, accessi riflessivi letterali, conservazione stringhe/commenti, collisioni/sintassi e self ridefinito. La rinomina non esegue il codice del progetto. Revisione e undo nell’interfaccia richiedono collaudo grafico.

# Versione 1.20

198 test superati per lingua, 11 grafici saltati. Nuove regressioni per copia senza eventi/import/avvio, rimozione callback/Tcl focus, segnaposto servizi/componenti esterni, form e pagina attivi, separazione dipendenze e arresto processo prima del polling UI. Nessuna verifica grafica completa dell’anteprima effettuata.

# Versione 1.19.1

193 test superati per lingua, 11 grafici saltati. Nuove regressioni per dimensioni iniziali non ancora assegnate, prima visualizzazione dei pannelli, recupero pannelli collassati e conservazione delle dimensioni valide. La verifica visiva interattiva resta necessaria.

# Versione 1.19

191 test superati in italiano e inglese, 11 grafici saltati per esecuzione. Verificati spostamento dei gruppi/gerarchie, distribuzione/allineamento, posizioni degli errori, analisi senza esecuzione e gestione moduli. Ambiente .venv reale creato e riutilizzato senza installazioni di rete; verificati preservazione cartelle esistenti, pulizia dopo errore, isolamento delle preferenze globali e assenza di fallback silenzioso.

I flussi grafici di selezione, navigazione dei problemi e wizard ambiente richiedono verifica interattiva.

# Versione 1.18 — icone applicazione

179 test superati per lingua, 11 grafici saltati. Conversione reale PNG/ICO/ICNS, lettura dei formati generati, sorgente runtime e passaggio icona ai comandi build Mac/Windows verificati. Controllati riferimento Setup, input non validi, pulizia dopo errore e aggiornamento riferimenti dopo rinomina/cestino. Nessuna build Windows reale o verifica visuale Dock/taskbar effettuata.

# Versione 1.17 — catalogo PIP integrato

176 test superati per lingua, 11 grafici saltati per esecuzione. Verificati cache offline, conservazione dopo aggiornamento fallito, cancellazione, paginazione/priorità, metadati di versioni compatibili, selezioni obsolete e gestione dei wizard già aperti. Download reale dal Simple Index PyPI: 938.819 nomi; ricerca NumPy verificata. Non effettuata installazione massiva dei pacchetti. Il nuovo gestore richiede ancora verifica grafica interattiva.

# Versione 1.16 — debugging generale

Suite completa: 167 test superati in italiano e 167 in inglese; 11 test grafici saltati per esecuzione. Nuove regressioni: impostazioni malformate, colori nominati, reset del contesto/undo editor, chiusura worker e cancellazione delle verifiche in coda, validità dei report, geometria e salvataggio atomico con errore simulato.

Validati e compilati tutti i 12 progetti di esempio; verificata la lettura reale delle API Tkinter senza creare widget. Controlli Python/shell e link locali README completati. Non eseguiti collaudo grafico completo, installazione su Windows/sistemi puliti o operazioni su account, dispositivi e stampanti reali.

# Versione 1.15

155 test superati; 11 grafici saltati. Verificate otto maniglie, conservazione dei bordi opposti, limiti minimi/coordinate e palette sintassi chiare/scure. La riorganizzazione grafica richiede verifica interattiva a diverse dimensioni; non è una replica MDI con pannelli flottanti.

# Versione 1.14

151 test superati; 11 test grafici saltati. Nuovi controlli: valori tipizzati, stringhe/commenti invariati, chiamate multilinea, descrittori esterni, riferimento locale per tutti i componenti, versioni stabili/Python compatibili, release ritirate e distinzione errori HTTP/rete. Nessun aggiornamento di pacchetti eseguito dal controllo di avvio. Verifica interattiva di digitazione/focus e avvio app ancora necessaria.

# Validation — 1.13

141 tests passed, 11 graphical tests skipped on macOS Python 3.15.2 / Jedi 0.20.0.

New tests cover real temporary Excel workbook/formula/sheet round-trips, VBA format guards, PDF merge/extraction/AES password handling, atomic file preservation, all six generated components, provider-specific dependencies, credential property validation, session/environment secret redaction, job queues and contextual examples.

OpenAI, Claude, Gemini, MIDI, print, Drive and S3 protocols are tested with mocks. No real credentials, paid LLM calls, OAuth account access, uploads, MIDI device playback or physical print jobs were used.

Actual imports passed: openpyxl 3.1.5, pypdf 7.0.1, mido 1.3.3, python-rtmidi 1.5.8 (built locally), openai 3.50.0, anthropic 1.17.0, google-genai 2.34.0, google-api-python-client 2.202.0 and boto3 1.44.2. Imports do not certify remote-service access.

A real PyInstaller 6.22.3 Office example build produced a macOS app and ZIP. Document library resources and ad hoc codesign verification were checked. hdiutil could not create a DMG in this session, so ZIP fallback was used.

Graphical app launch, live cloud/OAuth/LLM requests, real MIDI/printing, Windows builds and clean-machine installation require target-system validation. Excel formula evaluation, PDF OCR/rendering, built-in MIDI synthesis, automatic cloud synchronization and automatic LLM conversation history are not implemented.
