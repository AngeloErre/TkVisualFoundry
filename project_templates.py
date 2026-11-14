"""Built-in starter catalog; load fresh project copies without executing their code."""
from pathlib import Path
from core import load,new_project
from i18n import tr

TEMPLATES=(
    ('blank',None,'Progetto vuoto','Base','Un form vuoto: costruisci liberamente la tua applicazione.'),
    ('quiz','Quiz','Gioco a quiz','Giochi','Cinque domande, quattro risposte, punteggio e riavvio. Modifica il questionario nel codice di avvio.'),
    ('dice','DiceRoller','Simulatore di dadi','Giochi','D6, D20 e D100, da 1 a 100 dadi e bonus. Controlli degli input e totale.'),
    ('text','TextConverter','Convertitore di testi','Utilità','Maiuscolo, minuscolo, camelCase, liste Markdown e conteggio parole/caratteri.'),
    ('notes','StickyNote','Post-it digitali','Utilità','Una nota colorata con apertura e salvataggio manuale UTF-8. Nessun salvataggio automatico.'),
    ('odd','OddOneOut','Trova l’intruso','Giochi','Cinque turni su una griglia di nove tessere: trova il simbolo diverso e accumula punti.'),
    ('memory','MemoryPairs','Memory • coppie','Giochi','Otto coppie di lettere, contatore mosse e riavvio. Le coppie sbagliate si richiudono dopo una breve pausa.'),
    ('puzzle15','Sliding15','Gioco del 15','Giochi','Griglia 4×4, mosse legali e mescolamento sempre risolvibile. Riordina le tessere da 1 a 15.'),
    ('paint','MiniPaint','Mini-Paint','Creatività','Pennello, gomma bianca, linee, rettangoli e ovali. Colori, spessore, pulizia ed esportazione EPS.'),
    ('clocks','ClocksAndTimers','Sveglia e timer','Utilità','Cronometro con pausa, conto alla rovescia e sveglia HH:MM. Segnale tramite campanella di sistema.'),
    ('notepad','TabbedNotepad','Blocco note a schede','Utilità','Note multiple con apertura e salvataggio UTF-8, schede dinamiche e protezione delle modifiche non salvate.'),
    ('habits','HabitTracker','Tracker di abitudini','Organizzazione','Abitudini giornaliere, serie consecutive e cronologia. Apertura e salvataggio manuale JSON.'),
    ('pixels','PixelArt','Editor Pixel Art','Creatività','Griglia 16×16, colori e gomma bianca. Esporta immagini PPM o SVG senza librerie esterne.'),
    ('calculator','ScientificCalculator','Calcolatrice scientifica','Utilità','Espressioni aritmetiche, funzioni scientifiche in radianti e cronologia. Valutazione AST senza eval.'),
    ('timetable','WeeklyTimetable','Orario settimanale','Organizzazione','Lezioni, giorni, orari, aula e docente. Verifica sovrapposizioni e salva un archivio JSON.'),
    ('recipes','RecipeManager','Ricettario','Organizzazione','Ricette, ingredienti, preparazione, categorie e tempi. Ricerca e gestione di un archivio JSON.'),
    ('books','BookCatalog','Catalogo libri','Organizzazione','Titoli, autori, stato di lettura, prestiti e valutazioni. Ricerca e gestione di un archivio JSON.'),
    ('contacts','ContactBook','Rubrica contatti','Organizzazione','Nomi, telefoni, email, note e foto PNG/GIF. Salvataggio esplicito in un database SQLite dedicato.'),
    ('expenses','ExpenseManager','Gestionale spese','Organizzazione','Entrate e uscite, date e categorie. Totali decimali separati per valuta e salvataggio JSON.'),
    ('inventory','InventoryManager','Inventario casa/magazzino','Organizzazione','Codici univoci, quantità, costi EUR e soglie scorte basse. Modifica stock e salva JSON.'),
    ('media','MediaCatalog','Archivio CD/DVD/giochi','Organizzazione','Titoli, tipo, artista/piattaforma, anno e prestiti. Ricerca e salvataggio JSON.'),
    ('mines','Minesweeper','Campo Minato','Giochi','Griglia 9×9, dieci mine, primo clic sicuro e bandierine con clic destro o Control-clic.'),
    ('maze','MazeExplorer','Labirinto','Giochi','Labirinto generato con percorso verso l’uscita. Movimento con frecce, WASD o pulsanti.'),
    ('agenda','AgendaCalendar','Agenda e calendario','Organizzazione','Calendario mensile navigabile e appuntamenti con date/orari. Ricerca e salvataggio JSON.'),
    ('slideshow','ImageSlideshow','Slideshow PNG/GIF','Creatività','Cartella immagini PNG/GIF, precedente/successiva e riproduzione automatica. Nessun PIP aggiuntivo.'),
    ('invaders', 'MicroInvaders', 'Micro Invaders', 'Giochi', 'Microgioco arcade: movimento, spari, formazione di nemici e punteggio.'),
    ('chase', 'DotMazeChase', 'Dot Maze Chase', 'Giochi', 'Labirinto con punti e inseguitore, controlli da tastiera e pausa.'),
    ('platformer', 'MiniPlatformer', 'Mini Platformer', 'Giochi', 'Piattaforme originali: gravità, salto, caduta e traguardo.'),
    ('blocks', 'FallingBlocks', 'Falling Blocks', 'Giochi', 'Sette blocchi, rotazione, caduta rapida e cancellazione delle righe.'),
    ('neural', 'NeuralDriving', 'Neural Driving Lab', 'Giochi', 'Piccola rete neurale addestrabile per guidare su una strada sintetica. Solo libreria standard.'),
    ('study', 'StudyAgent', 'Study Agent', 'Utilità', 'Tutor di studio con client OpenAI asincrono. Richiede PIP, modello e chiave API personale.'),
    ('codes', 'CodeStudio', 'QR and Barcode Studio', 'Utilità', 'Generazione PNG e lettura QR/barcode locali. Richiede qrcode, python-barcode, zxing-cpp e Pillow.'),
    ('soundboard', 'Soundboard', 'Soundboard', 'Creatività', 'Otto pad con file audio locali, volume e stop. Richiede pygame; nessun audio incluso.'),
    ('kanban', 'KanbanPomodoro', 'Kanban e Pomodoro', 'Utilità', 'Schede trascinabili, scadenze, salvataggio JSON e timer di concentrazione.'),
    ('data', 'DataExplorer', 'Esploratore dati interattivo', 'Archivi', 'CSV/TSV, XLSX e SQLite in sola lettura; filtri, statistiche, grafico ed export. XLSX richiede openpyxl.'),
    ('cognitive', 'CognitiveLab', 'Laboratorio memoria e attenzione', 'Giochi', 'Sequenze adattive, ricerca visiva, tempi di risposta e CSV. Attività educativa, non diagnostica.'),
    ('escape', 'ClockworkEscape', 'Escape room investigativa', 'Giochi', 'Tre stanze originali, inventario, due enigmi e finali alternativi con salvataggio JSON.'),
)


def catalog():
    return [{'id':key,'title':tr(title),'category':tr(category),'description':tr(description)} for key,file,title,category,description in TEMPLATES]


def instantiate(key):
    entry=next((entry for entry in TEMPLATES if entry[0]==key),None)
    if entry is None:raise ValueError('Unknown starter template.')
    return new_project() if entry[1] is None else load(Path(__file__).with_name('examples')/'StarterTemplates'/(entry[1]+'.vtk.json'))
