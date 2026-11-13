# PIP: preparazione automatica dei componenti

## Inserire un componente

Doppio clic su WebcamView, oppure selezionalo e premi **Inserisci nel form** (anche Invio). La preparazione controlla **OpenCV, NumPy e Pillow** nel Python configurato:

- Se sono già presenti e importabili, continua automaticamente all’inserimento.
- Se manca qualcosa, avvia PIP, prepara le dipendenze e ripete i controlli. Il designer riceve il componente dopo la verifica positiva.
- Se l’operazione fallisce, rimane aperta la scheda **Log installazione**. Non avvengono reinstallazioni in ciclo.

Prima di usare webcam, USB o audio servono anche il dispositivo e le autorizzazioni del sistema. PIP non attiva la fotocamera e non installa VLC/libusb. Le note del componente descrivono questi requisiti.

## Menu PIP

| Voce | Azione |
|---|---|
| Prepara automaticamente il progetto | Controlla e installa i requisiti dei controlli inseriti |
| Prepara il componente selezionato | Predispone i pacchetti del controllo selezionato nel designer |
| Installa un pacchetto | Inserisci un nome come `Pillow` oppure `Pillow>=10` |
| Verifica requisiti senza installare | Mostra lo stato e lascia manuale l’avvio dell’installazione |
| Esplora PyPI | Consulta metadati e scegli un pacchetto/versione; Installa avvia la preparazione |
| Impostazioni pacchetti | Scegli Python e preferenze della preparazione |

Per configurare l’ambiente usa **Progetto → Configurazione…**. Le installazioni usano il Python indicato nella finestra PIP, che è quello dei progetti. Non vengono eseguite su un altro interprete per errore né con sudo.

## Finestra di preparazione

- **Requisiti e opzioni** mostra pacchetti, versione e stato.
- **Log installazione** contiene i comandi eseguiti e l’output completo.
- **Installa / ripara**, **Verifica**, **Chiudi/Interrompi** e **Continua/Fine** occupano un’area fissa separata dal log.
- **Solo designer**, quando disponibile, inserisce il controllo senza promettere che sia pronto all’esecuzione. L’avvio può prepararlo in seguito.

Puoi disattivare la preparazione automatica nelle preferenze o nella finestra. Se i pacchetti sono già pronti, l’inserimento/avvio continua comunque senza un clic aggiuntivo. Dal menu PIP puoi sempre richiedere una preparazione esplicita.

## Scelta dei pacchetti

PIP preferisce distribuzioni precompilate compatibili, ma non esclude automaticamente le versioni distribuite come sorgenti. L’opzione **Solo wheel** è avanzata e disattivata di default: attivandola, un pacchetto senza wheel compatibile non potrà essere installato.

Se serve compilare un pacchetto sorgente, devono essere disponibili gli strumenti e le librerie richiesti da quel progetto. Non vengono aggirati errori di compatibilità, certificati TLS o protezioni del Python di sistema. Il log distingue un errore PIP dall’esito dei controlli finali.

## Verifiche ed errori

Il controllo verifica metadati/versioni e, per i pacchetti noti, l’import in processi separati: un modulo nativo difettoso non interrompe l’intero controllo senza indicare il pacchetto. Per pacchetti sconosciuti vengono controllati i metadati senza importarne il codice arbitrariamente.

Dopo l’installazione sono eseguiti `pip check` e una nuova verifica dei requisiti. Conflitti nuovi bloccano il successo; conflitti già presenti e invariati sono segnalati nel log. Se PIP manca, la preparazione prova prima `ensurepip`. Gli import guasti possono richiedere reinstallazione del gruppo di requisiti mostrato.

Un’interruzione non disinstalla pacchetti già scritti: premi Verifica prima di continuare. Se l’errore riguarda rete, certificati, distribuzioni incompatibili o un Python non scrivibile, correggi la causa o scegli un ambiente virtuale funzionante in Configurazione.

La versione 1.8 è stata provata con un’installazione PIP reale da un wheel di test locale in un ambiente temporaneo. Download da PyPI e percorso grafico completo richiedono una verifica sul Mac di destinazione.


## Catalogo interno (1.17)

Apri PIP → Catalogo pacchetti…: Consigliati raccoglie i pacchetti dei componenti; Tutto PyPI permette ricerche per nome nell’indice ufficiale; Installati mostra il Python configurato. Cerca e sfoglia 100 risultati per pagina, poi seleziona per dettagli/versione stabile compatibile e installazione o aggiunta al progetto. Nome esatto… evita il download dell’intero indice. La cache dei nomi resta utilizzabile offline; descrizioni e installazioni richiedono rete. Aggiorna indice rinnova i nomi e conserva la vecchia cache se fallisce. La ricerca per descrizione completa non è disponibile.
