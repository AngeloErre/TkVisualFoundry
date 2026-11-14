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
)


def catalog():
    return [{'id':key,'title':tr(title),'category':tr(category),'description':tr(description)} for key,file,title,category,description in TEMPLATES]


def instantiate(key):
    entry=next((entry for entry in TEMPLATES if entry[0]==key),None)
    if entry is None:raise ValueError('Unknown starter template.')
    return new_project() if entry[1] is None else load(Path(__file__).with_name('examples')/'StarterTemplates'/(entry[1]+'.vtk.json'))
