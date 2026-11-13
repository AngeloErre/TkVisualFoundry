# VisualTk Studio 1.9

Il completamento è ora collegato automaticamente ai moduli e agli oggetti Python. Digitare `messagebox.` elenca i membri pubblici; aprire una chiamata mostra la firma e l’argomento corrente. Il motore comprende import, alias, variabili, chiamate concatenate e tipi dei componenti, utilizzando Jedi nell’interprete configurato per il progetto.

L’analisi avviene in un processo persistente separato dalla UI. Gli eventi del progetto non vengono eseguiti per ottenere suggerimenti. Esc, cambi di contesto e nuova digitazione invalidano le risposte precedenti. I simboli selezionati mostrano documentazione e firma; il completamento sostituisce soltanto la porzione di nome digitata.

L’installer include Jedi; se si sceglie un altro Python, il pulsante Motore nell’editor guida alla sua predisposizione. Dopo un’installazione PIP il motore si ricarica per vedere le nuove librerie. Per librerie esterne serve il relativo import. Codice dinamico o estensioni native prive di informazioni di tipo possono dare risultati parziali.

Per aggiornare rieseguire Install_Mac.command. Il requisito dell’app rimane Python >=3.15 stabile. Nuova guida Help → IntelliSense.

Validazione: 77 test superati, 11 grafici saltati su Linux Python 3.12.14/Jedi 0.20.0; Mac, GUI e packaging non verificati in questa sessione.
