# VisualTk Studio 1.6

Ambiente di sviluppo visuale per applicazioni Python/Tkinter, ispirato a Visual Basic 6 e pensato principalmente per macOS.

## Novità

- Assistente codice contestuale al componente e all’evento selezionato.
- Completamento automatico per componenti, form, metodi e proprietà configure.
- Pannello “cosa puoi fare” con esempi inseribili e spiegazioni in italiano.
- Firme dei metodi e navigazione dei suggerimenti con tastiera.
- Suggerimenti specifici per i principali widget Tkinter e proprietà dei descrittori esterni.

## Funzioni incluse dalle versioni precedenti

Designer visuale, progetti multi-form, editor eventi, esportazione Python, esecuzione e debug, procedura per componenti esterni, esploratore PyPI, temi dell’IDE, controlli multimediali, Help e installer macOS.

## Installazione

Con Python 3.15 stabile o successivo e Tkinter disponibili, eseguire `Install_Mac.command`. Per aggiornare, estrarre il pacchetto ed eseguire nuovamente l’installer. I progetti sono file `.vtk.json` separati.

## Verifica

33 test superati; 6 test grafici saltati. Il comportamento grafico e le periferiche richiedono verifica manuale sul Mac. I componenti esterni devono essere compatibili con Tkinter; l’installazione di un pacchetto non genera automaticamente un widget visuale.

## Descrizione breve per GitHub

IDE visuale Python/Tkinter ispirato a VB6 per macOS: designer multi-form, editor eventi, completamento contestuale, componenti esterni, debug e packaging.
