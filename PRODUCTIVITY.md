# MIDI, Excel, PDF, stampa, cloud e LLM — VisualTk Studio 1.13

I sei nuovi componenti sono nella palette predefinita. Le librerie vengono preparate dal wizard PIP quando necessario. Seleziona il controllo e usa **Azioni → Configura componente…**: scegli servizio, file, modello e nomi delle variabili ambiente, poi **Salva e prepara dipendenze…**. I file locali richiesti vanno inclusi nel progetto per il deploy; i percorsi assoluti non vengono convertiti automaticamente.

Il designer non apre documenti, non riproduce MIDI, non accede ad account e non invia richieste API. Le operazioni partono esplicitamente nell’app generata. Le operazioni lente usano thread e una coda; i risultati e gli eventi arrivano nel thread Tk. Un componente esegue una sola operazione per volta. In caso di errore emette **ServiceError** e aggiorna `.error`.

## MIDIPlayer

Apri un file `.mid`/`.midi`, premi **Uscite MIDI**, seleziona una porta e premi **Riproduci**. Sono disponibili pausa/ripresa e stop. Si usano `mido` e `python-rtmidi`; i normali file MIDI tipo 0/1 contengono note, tempi e comandi, non campioni audio. Devi disporre di un sintetizzatore hardware o software collegato a una porta MIDI. Su Mac una porta virtuale da sola non produce suono: occorre un’app che la riceva. SoundFont, strumenti virtuali e sintetizzatore audio non sono inclusi. La disponibilità delle porte dipende dal sistema e dai driver.

Metodi: `refresh_ports()`, `play("song.mid")`, `pause()`, `stop()`. Eventi: **MidiStarted**, **MidiFinished**, **ServiceError**. MidiFinished indica la fine dell’operazione, anche dopo Stop. La pausa e lo stop azzerano i controlli dell’uscita per evitare note bloccate.

## ExcelWorkbook

Legge, crea e modifica file **XLSX/XLSM** con openpyxl. La tabella mostra fino al numero di righe configurato e 50 colonne; il workbook completo rimane disponibile in `.book`. Cambia foglio dal menu, modifica una cella oppure salva una copia. Gli indici delle celle partono da **1**.

```python
# Nell’evento ExcelLoaded:
self.Excel1.set_cell(2, 2, 42)
self.Excel1.add_sheet("Risultati")
self.Excel1.save_as("aggiornato.xlsx")
```

`load(path)`, `create(headers=[...], rows=[...])` e `save_as(path)` sono asincroni: attendi **ExcelLoaded** prima di accedere al documento. Eventi **ExcelChanged** e **ExcelSaved** segnalano modifiche e salvataggio. `get_data()` restituisce le righe dell’anteprima, compresa l’eventuale riga di intestazioni.

Le formule vengono conservate, **non calcolate**. I file XLS/XLSB non sono supportati. Per conservare VBA, apri e salva come `.xlsm`; le macro non vengono eseguite. openpyxl non preserva ogni funzionalità di Excel, perciò lavora su copie di documenti con oggetti complessi. Non viene effettuata una conversione automatica Excel→PDF.

## PDFDocument

Apre PDF, mostra il testo della prima pagina, estrae tutto il testo, unisce documenti ed esporta pagine selezionate. È una **anteprima testuale**, non un visualizzatore grafico e non un motore OCR: le scansioni senza testo possono produrre un risultato vuoto. Per documenti cifrati inserisci la password in esecuzione; il pacchetto PIP include il supporto crittografico.

Metodi asincroni: `load(path, password=None)`, `extract_text()`, `merge(paths, destination)`, `extract_pages(indexes, destination)`, `save_text(path)`. Gli indici dell’API `extract_pages` partono da **0**; il dialogo visuale chiede numeri da 1. Eventi: **PDFLoaded**, **PDFTextReady**, **PDFSaved**. Attributi: `.text`, `.page_count`, `.last_path`.

## PrintDocument

**Apri anteprima / dialogo di stampa** apre il file nell’app associata: usa il comando Stampa di quell’app per il dialogo nativo e le opzioni complete. **Invia alla stampa…** chiede conferma prima di inoltrare il documento.

- macOS: invio con CUPS/lp, stampante facoltativa e numero di copie.
- Windows: delega al comando print dell’app associata, con stampante predefinita e una copia. Per scegliere altre opzioni usa l’app associata.

L’evento **PrintSubmitted** indica l’inoltro della richiesta, non la stampa fisica riuscita. `.print_job` contiene il risultato del sistema. Sono necessari driver, stampante e un gestore del formato. Per i file Office, usa l’app associata o esporta prima un PDF con un programma adatto: il componente non rende i fogli Excel per la stampa. Nessuna stampa parte durante il design o i test automatici.

## CloudStorage

Il servizio viene scelto nella configurazione del controllo: **drive**, **s3**, **webdav**. La cartella è un ID per Drive e un prefisso/percorso per gli altri servizi. Connessione, elenco, upload e download sono asincroni. Eventi: **CloudConnected**, **CloudListed**, **CloudTransferred**. Attributi: `.files`, `.last_transfer`, `.error`.

### Google Drive

1. Nel tuo progetto Google Cloud abilita Drive API e configura consenso OAuth e un client di tipo **Desktop**. Per account di test può essere necessario aggiungere l’utente tra quelli autorizzati.
2. Nell’app in esecuzione premi **Credenziali…** e scegli il JSON del client, oppure imposta `GOOGLE_OAUTH_CLIENT_FILE` con il percorso del file esterno.
3. Premi **Connetti…** e completa il consenso nel browser. I token vengono salvati fuori dal progetto in `~/.visualtkstudio-credentials/drive-app.json` (o drive-all.json); `GOOGLE_TOKEN_FILE` può indicare un altro percorso esterno.
4. Premi **Elenca file**. Il valore iniziale `root` indica la radice. Non è un browser completo di tutte le cartelle: inserisci l’ID della cartella desiderata.

`scope=app` usa drive.file e vede soltanto i file creati/aperti/condivisi con questa app, non tutto il Drive. `scope=all` richiede un consenso più ampio e può richiedere configurazioni/verifiche aggiuntive di Google o dell’organizzazione. `auth_mode=adc` usa le Application Default Credentials già predisposte; per service account valgono i file e i permessi assegnati a quell’account.

I documenti nativi Google vengono scaricati come **PDF**; i file binari nel loro formato originale. Il componente non sincronizza automaticamente cartelle e non elimina file remoti. L’upload Drive crea un nuovo file.

### S3/MinIO

Configura il bucket e un prefisso facoltativo (normalmente vuoto). Sono utilizzabili le credenziali standard AWS o **Credenziali…** per una sessione. Per MinIO indica un endpoint HTTPS con la variabile `S3_ENDPOINT_URL` o nel dialogo di sessione. HTTP è ammesso solo su localhost. Gli oggetti già presenti non vengono sovrascritti silenziosamente; un conflitto produce ServiceError. L’upload usa PutObject, quindi non è un uploader multipart per file enormi.

### WebDAV

Per Nextcloud/ownCloud e server compatibili, usa **Credenziali…** oppure `WEBDAV_URL`, `WEBDAV_USER`, `WEBDAV_PASSWORD`. L’URL deve essere la radice WebDAV effettiva, non la pagina web del servizio. Sono implementati elenco di un livello, upload e download di file; non una sincronizzazione completa. L’upload non sostituisce un file esistente. È richiesto HTTPS, salvo localhost.

## LLMClient: OpenAI, Claude, Gemini

Configura **openai**, **anthropic** o **gemini**. Si usano gli SDK ufficiali e le API Responses, Messages e Generate Content. Il componente invia una richiesta testuale per operazione; non implementa strumenti, allegati o una cronologia conversazionale automatica.

1. Predisponi un account **API** del fornitore, con accesso al modello e fatturazione/quote appropriate. Un abbonamento all’app ChatGPT, Claude o Gemini non configura automaticamente questi accessi.
2. Nell’app premi **Chiave API…** per una chiave valida soltanto per la sessione, oppure imposta `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` o `GEMINI_API_KEY` prima dell’avvio.
3. Premi **Modelli** o inserisci un ID disponibile al tuo account. L’elenco può contenere modelli che non supportano la generazione testuale: scegli quello appropriato.
4. Scrivi e premi **Invia**. Il limite token controlla l’output richiesto, non garantisce un costo totale. Disponibilità, limiti e costi dipendono dal servizio.

```python
# Nell’evento Click di un pulsante:
self.LLM1.send("Spiega questo risultato in modo semplice")

# Nell’evento LLMResponse del componente:
self.Label1.configure(text=self.LLM1.response)
print(self.LLM1.usage)
```

Eventi: **LLMModelsReady**, **LLMResponse**, **ServiceError**. `.last_result` contiene anche fornitore e modello. Non vengono inviate richieste durante la progettazione; negli esempi non sono presenti chiavi. La richiesta parte nell’app quando l’utente preme Invia o quando il tuo codice chiama `send()`.

## Credenziali, deploy e verifica

Nel progetto vengono salvati impostazioni e **nomi** delle variabili, mai chiavi o password fornite dai dialoghi di sessione. Queste ultime restano in memoria fino alla chiusura. Non includere JSON OAuth, token, file AWS o chiavi tra le risorse del progetto. Un’app distribuita deve ricevere credenziali e autorizzazioni dal proprio utente o dall’infrastruttura prevista; non contiene l’account dello sviluppatore.

Il deploy raccoglie solo gli SDK del fornitore configurato, insieme a certificati e risorse necessarie. MIDI, servizi remoti, stampa fisica e Windows richiedono collaudo sul sistema reale. I test automatici usano documenti temporanei e servizi simulati, senza account personali, chiamate LLM a pagamento, upload reali o stampe.

Esempi: `examples/Productivity/OfficeDemo.vtk.json`, `ServicesDemo.vtk.json`, `MidiPrintDemo.vtk.json`.
