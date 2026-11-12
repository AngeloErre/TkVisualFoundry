# DatabaseView: database locale o remoto con tabella dati

**DatabaseView** è disponibile nella palette senza importare descrittori esterni. Include connessione, elenco tabelle, griglia con scorrimento, scelta del record, aggiunta, modifica, eliminazione e aggiornamento della visualizzazione.

## Configurazione

1. Inserisci **DatabaseView** nel form.
2. Selezionalo e premi **Configura componente / dipendenze…**.
3. Scegli il backend e compila i campi. Salva; per un server remoto puoi premere **Salva e prepara dipendenze…**.
4. Avvia il progetto. **Connetti…** consente di confermare o cambiare la connessione e inserire la password.

| Backend | Configurazione | PIP |
|---|---|---|
| SQLite | Percorso del file; se non esiste viene creato quando connetti | Nessuno: sqlite3 è incluso in Python |
| PostgreSQL | Host, porta, database, utente | SQLAlchemy >=2.0 e psycopg[binary] >=3 |
| MySQL | Host, porta, database, utente | SQLAlchemy >=2.0 e PyMySQL >=1.1 |

La porta 0 usa quella predefinita del driver. Un percorso SQLite relativo si riferisce alla cartella di lavoro del progetto. Per distribuire un’app conviene scegliere un percorso assoluto scrivibile. Il componente non apre connessioni durante la progettazione né all’inserimento: connetti esplicitamente o usa l’evento Load.

Le password non sono opzioni del componente e non vengono salvate nel progetto o nel sorgente generato. Durante l’esecuzione puoi inserirle nella finestra di connessione, oppure predisporre la variabile ambiente indicata da `password_env` (predefinita `VISUALTK_DB_PASSWORD`). Username, host e nome database fanno parte del progetto.

## Prova con SQLite

Apri `examples/Database.vtk.json` e avvialo. Il progetto apre un file dimostrativo `visualtk_demo.sqlite` nella cartella di lavoro e crea, se manca, la tabella `contatti`. Non inserisce dati personali o credenziali.

In un progetto nuovo, dopo **Connetti**, premi **Crea tabella esempio** per predisporre:

```sql
CREATE TABLE IF NOT EXISTS contatti (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    email TEXT,
    note TEXT
);
```

Seleziona la tabella dal menu. **+ Nuovo record** apre l’editor: attiva i campi da scrivere, lascia disattivato `id` per usare l’identificativo automatico. `NULL` è distinto dalla stringa vuota. **Modifica selezionato** apre il record corrente; **Elimina selezionato** chiede conferma. **Aggiorna** rilegge i dati dal database.

## Codice pronto nell’assistente

Apri un evento del componente: il pannello “cosa puoi fare” e il completamento propongono i metodi seguenti. Gli esempi di scrittura si riferiscono alla tabella `contatti`: adatta nomi di colonne e chiavi al tuo database.

Connessione (evento Load):

```python
self.DatabaseView1.connect()
```

Aggiunta di un record (ad esempio Click di un pulsante):

```python
self.DatabaseView1.insert_record({"nome": "Mario", "email": "mario@example.com"})
```

Modifica/scrittura di campi tramite chiave primaria:

```python
self.DatabaseView1.update_record({"id": 1}, {"nome": "Nuovo nome"})
```

Eliminazione da codice, con conferma:

```python
if messagebox.askyesno("Elimina", "Eliminare il record 1?"):
    self.DatabaseView1.delete_record({"id": 1})
```

Aggiornamento della tabella visualizzata:

```python
self.DatabaseView1.refresh()
```

Lettura (nell’evento **DataLoaded**):

```python
records = self.DatabaseView1.rows
print("Record caricati:", len(records))
```

Riga selezionata (evento **RecordSelected**):

```python
record = self.DatabaseView1.selected_record
if record is not None:
    print(record)
```

Le operazioni sono asincrone: non concatenare `connect()` e una scrittura aspettandoti un risultato immediato. Attendi **DatabaseConnected**, **DataLoaded** o **DataChanged**. Una scrittura riuscita aggiorna automaticamente la griglia. Un’operazione già in corso impedisce di inviarne un’altra. Dopo `DataChanged`, la lettura aggiornata arriva in `DataLoaded`.

| Evento | Significato |
|---|---|
| DatabaseConnected | Connessione aperta |
| DataLoaded | Dati disponibili in `rows` |
| RecordSelected | Dizionario disponibile in `selected_record` |
| DataChanged | Scrittura conclusa; segue aggiornamento dei dati |
| DatabaseError | Leggi `last_error` e lo stato del componente |

## Limiti e comportamento

- SQLite è stato provato con database reali locali; PostgreSQL/MySQL richiedono ancora collaudo con server reali.
- Sono elencate le tabelle dello schema predefinito, non le viste. Massimo 5.000 righe per lettura (200 predefinite), senza paginazione, filtri o ordinamento persistente.
- Modifica ed eliminazione richiedono una chiave primaria completa, anche composta. Senza chiave primaria restano possibili lettura e inserimento.
- Le chiavi primarie esistenti non sono modificabili nell’editor. Campi binari e tipi avanzati si gestiscono da codice; non è un editor universale di tutti i tipi SQL.
- Valori e chiavi sono parametrizzati; i nomi delle tabelle/colonne provengono dai metadati. Le scritture usano transazioni. Un record non trovato provoca errore, non una modifica estesa.
- La creazione guidata della tabella esempio è disponibile solo su SQLite. Non sono inclusi editor SQL libero, migrazioni, creazione utenti o amministrazione del server.
- Per configurazioni remote avanzate (schema, TLS personalizzato, tunnel o autenticazione specifica) occorre adattare il codice del backend: la procedura copre la connessione base PostgreSQL/MySQL.

Riferimento: [configurazione dei driver SQLAlchemy](https://docs.sqlalchemy.org/en/20/core/engines.html).
