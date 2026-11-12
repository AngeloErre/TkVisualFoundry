# Esempi di codice — corpi degli eventi

Scrivi questi esempi nel codice dell'evento, senza aggiungere def. I nomi devono corrispondere ai controlli del tuo progetto.

## Tabella Treeview — evento Load

```python
self.Treeview1.heading('nome', text='Nome')
self.Treeview1.heading('valore', text='Valore')
self.Treeview1.insert('', 'end', text='Studente', values=('Alessandro', 10))
```

## Schede Notebook — evento Load

```python
pagina = self.Notebook1.pages['Pagina 1']
ttk.Label(pagina, text='Contenuto della prima scheda').pack(padx=20, pady=20)
```

I widget dentro le schede si aggiungono da codice: il designer non supporta ancora contenitori annidati.

## File trascinati dal Finder — evento FilesDropped

```python
for percorso in self.FileDropZone1.paths:
    print(percorso)
```

## File scelti — evento FileSelected

```python
print(self.FileBrowserButton1.paths)
```

## Messaggio/input — evento DialogClosed

```python
print(self.MessageButton1.result)
```

I mode di MessageButton sono info, warning, error, confirm, text, integer, float e color.

## HTML e browser — evento di un pulsante

```python
self.HtmlView1.set_html('<h1>Lezione</h1><p>Contenuto di esempio</p>')
self.WebView1.navigate('https://www.python.org')
self.NativeWebButton1.open()
```

## Video e YouTube

```python
self.VideoPlayer1.play('/percorso/video.mp4')
```

Per YouTube inserisci un URL nel controllo e premi Apri YouTube. Il backend predefinito è yt-dlp; puoi selezionare pytubefix nelle proprietà. Il controllo estrae uno stream, senza scaricare un file permanente. Il funzionamento dipende dagli aggiornamenti del servizio e dalle eventuali restrizioni del video. VLC è richiesto anche per YouTube.

## Data selezionata

```python
print(self.Calendar1.get_date())
print(self.DateEntry1.get_date())
```

## Esempi inclusi

- Saluto.vtk.json: testo, pulsanti e seconda finestra.
- Multimedia.vtk.json: galleria immagini, MP3, webcam, USB e seriale.
- Controlli_Standard.vtk.json: Treeview, Notebook, ScrolledText, dialoghi e file trascinati.
- Web_Video.vtk.json: HTML, web, video e YouTube.
- Moderni.vtk.json: pulsanti moderni, interruttore e calendario.

Prima di avviare un esempio con librerie esterne, usa Librerie → Installa dipendenze progetto. Aprire un esempio non avvia automaticamente webcam o riproduzione video.

## Database.vtk.json
Esempio SQLite locale: connessione dal Load del componente, tabella contatti creata solo se il database è vuoto. Usa i comandi del controllo per aggiungere, modificare e cancellare record. Dettagli ed esempi nell’Help → Database.
