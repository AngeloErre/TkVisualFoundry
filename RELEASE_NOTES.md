# VisualTk Studio 1.8

## Interfaccia

La palette ora mostra icone e supporta l’inserimento con Invio. I comandi di inserimento e applicazione delle proprietà sono fissati sopra le rispettive aree di lavoro, mentre i comandi secondari si trovano nei menu. La barra in alto offre File, Modifica, Progetto, Esegui, PIP, Componenti, Vista e Help. Il log è richiudibile e non può espandersi fino a coprire i controlli del designer.

## Pacchetti automatici

Quando inserisci o avvii un componente con dipendenze, la preparazione controlla l’interprete configurato, installa ciò che manca e prosegue dopo la verifica. Se tutto è già pronto, continua senza richiedere altri clic. Una installazione fallita non provoca tentativi infiniti: log ed errori restano consultabili.

Il menu PIP permette di preparare il progetto, il componente selezionato o un pacchetto per nome. La finestra riserva spazio ai pulsanti anche quando il log o i messaggi sono lunghi. PIP preferisce wheel disponibili ma può usare pacchetti sorgenti; l’opzione avanzata solo-wheel è disattivata di default.

## Aggiornamento

Riesegui Install_Mac.command dal pacchetto 1.8. Le librerie già presenti vengono mantenute. Le nuove preferenze attivano la preparazione automatica e mantengono facoltativo il blocco dei pacchetti sorgenti.

## Verifica

58 test superati, 10 grafici saltati. Testata una reale installazione PIP offline in un ambiente temporaneo, oltre alle decisioni automatiche e al controllo degli errori. Verificata in sola lettura la disponibilità della webcam nel Python configurato (OpenCV/NumPy/Pillow importabili); non verificato l’accesso alla fotocamera. GUI, download live e packaging richiedono ancora collaudo.
