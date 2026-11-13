# Verifica corrente — 1.9

88 test con Python 3.12.14 e Jedi 0.20.0 nel nuovo ambiente Linux: **77 superati, 11 grafici saltati**. La policy di avvio dell’app mantiene Python >=3.15 stabile; i relativi test simulano versioni compatibili/non compatibili.

- `messagebox.` completo di metodi/costanti pubbliche, filtro `sh`, firma di showinfo, argomento attivo e argomenti nominati.
- Alias/import del progetto e dell’editor, Path concatenati, variabili stringa/lista, metodi ereditati di Button, NumPy installato.
- Componente esterno definito in un modulo di test con un’operazione al livello globale: Jedi ne riconosce i membri senza eseguire tale operazione.
- Libreria fixture collocata soltanto nel site-packages di un ambiente virtuale temporaneo: il worker usa il Python di quell’ambiente e la riconosce.
- Trasporto JSON persistente, riuso del processo, timeout senza blocco del chiamante, assenza di Jedi con messaggio gestibile, chiusura dei worker e risposte obsolete scartate.
- Inserimento del solo membro: messagebox.sh diventa messagebox.showinfo, senza duplicare il ricevitore.
- Test GUI aggiunto per popup e accettazione; saltato insieme agli altri per assenza di una sessione grafica.

Non eseguiti: percorso UI sul Mac, build app/DMG, connessioni a server database o test hardware. Il codice precedente non è stato modificato nell’installazione Mac, attualmente non collegata. Rimangono validi i test non grafici delle funzioni preesistenti.

Le verifiche seguenti sono storiche e descrivono le singole versioni.

---

# Verifica corrente — 1.8

68 test eseguiti con Python 3.15.2: **58 superati e 10 grafici saltati**.

- Installazione PIP reale e offline di un wheel di prova creato dal test, in un ambiente virtuale temporaneo. Verificati metadati, pip check e import effettivo. Nessun pacchetto aggiunto all’ambiente di lavoro dell’utente.
- Decisioni automatiche verificate: requisiti mancanti → installazione; requisiti pronti → continuazione; errore persistente → nessun ciclo infinito di reinstallazione.
- Verificati isolamento degli import nativi, mancata dichiarazione di successo su errori PIP, prosecuzione automatica dopo la verifica e limite alla dimensione del log.
- Test aggiunti per visibilità dei pulsanti alla dimensione minima della finestra e per il footer PIP: saltati perché la sessione grafica non è disponibile.
- Controllo di sola lettura sul Python configurato del Mac: PIP funzionante; OpenCV, NumPy e Pillow già presenti e importabili. Non è stata necessaria la loro reinstallazione.

Restano da collaudare visivamente palette/iconografia, menu, log, wizard e percorso completo di inserimento; non eseguiti download PIP da Internet, test hardware, database remoti o packaging in questa sessione.

Le verifiche storiche sotto descrivono le rispettive versioni.

---

# Verifica corrente — 1.7

Eseguiti 58 test con Python 3.15.2: **50 superati, 8 grafici saltati**.

- SQLite reale: inserimento/lettura/modifica/eliminazione, valori parametrizzati, rollback, chiavi composte, assenza di chiavi, identificatori non validi, persistenza su file e limite righe.
- Generazione autonoma del componente database e progetto dimostrativo; dipendenze condizionali al backend.
- Driver remoto: simulato URL con password contenente caratteri speciali e chiusura engine su errore. Nessun server remoto reale contattato.
- Verifiche PIP: metadati reali dell’interprete (PIP presente, distribuzione fittizia assente, vincolo incompatibile), comando senza shell, pipeline di installazione simulata e mancata verifica di successo quando PIP fallisce.
- Test già esistenti per modello, estensioni, integrazioni, completamento e policy interprete.
- Non installati pacchetti nell’ambiente dell’utente per questa verifica.

Restano da collaudare: nuove finestre grafiche, flusso completo di installazione con rete, webcam/USB/audio, database PostgreSQL/MySQL reali, installer completo e PyInstaller/app/DMG.

Le verifiche storiche sotto descrivono le rispettive versioni e non lo stato dell’interprete corrente.

---

# Verifica aggiuntiva 1.3.1

32 test: 26 superati e 6 grafici saltati. Verificata sul Mac la presenza di Python 3.15.0rc3 con Tk 9.0. Eseguita solo la sezione di rilevamento dell’installer, senza installare o modificare software: il messaggio identifica correttamente rc3 e la distingue da un interprete mancante. Nessun collaudo GUI su 3.15 final.

# Verifica della versione 1.3 — 12 novembre 2026

## Requisito introdotto

IDE, interprete configurato per avvio/debug/installazione dipendenze e strumenti di build richiedono Python >=3.15 con releaselevel final. Alpha, beta e release candidate sono rifiutate. L'installer seleziona Python 3.15 stabile con Tkinter e conserva in backup eventuali ambienti precedenti incompatibili.

## Risultati effettivi

- 31 test: 25 superati, 6 test grafici saltati.
- Test eseguiti con Python 3.14.8 per validare modello, generazione e policy di versione senza avviare l'IDE. I casi 3.15 final, 3.15 prerelease e 3.16 alpha sono simulati nei test della policy.
- Provato realmente l'avvio con Python 3.14.8 e Python 3.16.0a2 installati nell'ambiente: entrambi sono rifiutati con il messaggio che richiede 3.15 stabile, senza tentare l'apertura di Tk.
- Sintassi di sorgenti Python, esempi generati e quattro script shell: verificata.
- pygame-ce>=2.5.8 sostituisce pygame nei requisiti del componente audio; resta valido import pygame. La disponibilità di un wheel CPython 3.15 macOS universal2 è stata verificata su PyPI.
- PyInstaller minimo aggiornato a 6.22.3.

## Non verificato

Python 3.15 non è installato nell'ambiente di verifica: non è stato eseguito un collaudo reale del programma o delle dipendenze su quell'interprete. Nessuna installazione Python di sistema è stata modificata. Restano da collaudare GUI, completamento, debug interattivo, audio/video, webcam, USB/seriale, browser nativo, collegamenti live e packaging sul Mac di destinazione.

## Procedura sul Mac

Eseguire Install_Mac.command. Se manca Python 3.15 e Homebrew è presente, lo script installa python@3.15 e python-tk@3.15; senza Homebrew apre il sito ufficiale Python. Dopo l'installazione verificare Help → Diagnostica dipendenze, esempi e suite di test con l'interprete 3.15. Impostare nelle preferenze un interprete stabile >=3.15 se era stato memorizzato un percorso precedente. VLC/libVLC richiede installazione separata.
