# Aggiornamento 1.3

Sono stati aggiunti altri 18 controlli/descrittori alla palette, oltre ai cinque originali. Vedi COMPATIBILITA.md per la mappa completa e ESEMPI.md per gli handler. Il descrittore CTkButton è ora già registrato; importarlo nuovamente non è necessario. Il menu Help apre questi documenti e la diagnostica delle dipendenze.

# Estensioni e librerie — versione 1.1

## Componenti pronti nella palette

| Componente | Funzioni | Librerie |
|---|---|---|
| ImageGallery | Scelta cartella, miniature, selezione immagine, orientamento EXIF | Pillow |
| AudioPlayer | Apertura MP3/WAV/OGG, play, pausa, riprendi, stop, volume | pygame-ce (import pygame) |
| WebcamView | Apertura camera per indice, anteprima, stop e snapshot PNG | OpenCV, Pillow |
| USBExplorer | Scansione periferiche, identificativi VID/PID, bus e indirizzo, selezione | PyUSB, libusb |
| SerialMonitor | Elenco porte, connessione a baudrate configurabile, lettura e invio testo | pySerial |

Apri `examples/Multimedia.vtk.json` per provare tutti i controlli. Nessuna webcam, porta o periferica è aperta automaticamente: occorre premere Avvia, Scansiona o Connetti. La galleria con directory configurata carica le immagini all'avvio.

I controlli sono rappresentati da sagome nel designer e diventano interattivi eseguendo l'applicazione. I nuovi eventi sono disponibili nel selettore eventi; hanno effetto sui controlli che li emettono:

- ImageSelected: `self.ImageGallery1.selected_path` contiene il percorso scelto.
- PlaybackStarted: emesso quando viene avviato il player.
- SnapshotSaved: emesso dopo il salvataggio dello snapshot.
- DeviceSelected: `self.USBExplorer1.selected_device` contiene l'oggetto PyUSB selezionato.
- DeviceError: errore del componente webcam/USB/seriale.
- DataReceived: `self.SerialMonitor1.last_data` contiene i byte ricevuti.

Esempio evento Load di una finestra:

```python
self.AudioPlayer1.source = "/percorso/brano.mp3"
self.WebcamView1.camera_index = 0
self.SerialMonitor1.baudrate = 115200
```

Esempio evento ImageSelected:

```python
print(self.ImageGallery1.selected_path)
```

Esempio invio seriale da un pulsante:

```python
self.SerialMonitor1.send(b"LED_ON\n")
```

## Componenti visuali di librerie esterne

Usa **Librerie → Importa componente visuale** e scegli un file descrittore `.vtk-component.json`. È incluso un esempio pronto per `customtkinter.CTkButton`:

```json
{
  "name": "CTkButton",
  "module": "customtkinter",
  "class": "CTkButton",
  "defaults": {"text": "Premi", "corner_radius": 8},
  "requirements": ["customtkinter>=5.2"]
}
```

Il componente appare nella palette e le proprietà dichiarate in defaults diventano modificabili. Il descrittore è incorporato nel progetto JSON e viene conservato salvando/riaprendo il progetto. La classe Python non viene importata durante il design: viene importata soltanto eseguendo il sorgente generato.

Il contratto richiede una classe compatibile con Tkinter: costruttore `Classe(master, **proprieta)`, metodi `place(...)` e `bind(...)`. Non tutte le classi delle librerie sono widget: non si possono inserire funzioni o classi non visuali come componenti. Per widget con costruttori differenti serve un piccolo adapter Python distribuito come pacchetto installabile. Il registro non converte automaticamente un pacchetto PyPI in un widget e non installa codice da URL/Git arbitrari.

Dopo aver inserito il componente usa **Installa dipendenze progetto**. L'esempio richiede accesso a Internet per scaricare customtkinter. Gli eventi personalizzati arbitrari dei plugin non sono ancora definibili nel descrittore: sono disponibili i normali eventi Tk e gli eventi virtuali predefiniti dell'IDE.

## Esploratore collegato a PyPI

**Librerie → Esplora PyPI** offre:

1. Catalogo filtrabile: Pillow, pygame-ce, OpenCV, PyUSB, pySerial, CustomTkinter, ttkbootstrap, tkcalendar, tksheet, matplotlib e NumPy. È una selezione pratica, non una classifica quantitativa di utilizzo.
2. Consultazione online per nome esatto attraverso l'API JSON ufficiale PyPI.
3. Scheda con versione pubblicata, descrizione, requisito Python, licenza e URL del progetto/repository.
4. Ricerca libera su PyPI nel browser: l'API di ricerca XML-RPC è dismessa, quindi non viene usato `pip search`.
5. Installazione esplicita della versione selezionata nell'interprete configurato nelle impostazioni dell'IDE.
6. Aggiunta della versione esatta alle dipendenze del progetto, elenco dei pacchetti installati e installazione delle dipendenze necessarie ai componenti usati.

Le operazioni HTTP/pip si svolgono in background, con timeout e visualizzazione degli errori. Se chiudi la finestra durante un'installazione già iniziata, questa continua in background: attendi il completamento prima di chiudere l'IDE. Il catalogo è disponibile anche offline; metadati e installazione richiedono Internet. Installare un pacchetto non aggiunge automaticamente una voce alla palette: per questo serve il relativo descrittore.

## Installazione e Mac

L'installer richiede e seleziona Python 3.15 stabile, installa `requirements.txt` e `requirements-multimedia.txt`, e installa libusb quando trova Homebrew. Se Homebrew manca, USBExplorer richiede l'installazione separata del backend libusb; il monitor seriale può funzionare indipendentemente da PyUSB.

La fotocamera richiede il consenso di macOS in Privacy e sicurezza → Fotocamera. Per i progetti impacchettati il generatore del bundle aggiunge NSCameraUsageDescription e una firma ad hoc. Non vengono richiesti accesso al microfono o registrazione audio. L'accesso USB effettivo dipende dal dispositivo, dal driver e dal protocollo: elencare una periferica non significa poterla comandare senza conoscerne gli endpoint. I dispositivi USB seriali richiedono eventuali driver del produttore.

## Esportazione, build e limiti

Il sorgente esportato contiene il runtime dei componenti integrati e può essere spostato fuori dall'IDE; accanto viene salvato `requirements-visualtk.txt`. Installa quel file nello stesso ambiente Python che esegue l'applicazione. I plugin esterni restano dipendenze importabili da installare. La cartella delle immagini e i file audio sono riferimenti a percorsi: non sono copiati automaticamente nel bundle.

La galleria carica al massimo 300 miniature per cartella, in modo sincrono, e non scorre ricorsivamente le sottocartelle. pygame.mixer.music usa un canale musicale condiviso: in questa versione va usato un solo AudioPlayer attivo per applicazione. WebcamView non registra video; lo snapshot cattura l'ultimo frame disponibile. USBExplorer espone l'oggetto PyUSB per il codice utente, ma non comprende un editor universale di protocolli USB/HID. Letture/scritture USB lente vanno svolte dal codice utente su un worker; gli aggiornamenti Tk devono avvenire nel thread grafico. SerialMonitor è un monitor testuale UTF-8 con accesso ai byte originali via last_data.

Documentazione ufficiale: https://docs.pypi.org/api/json/ — https://pillow.readthedocs.io/ — https://www.pygame.org/docs/ref/music.html — https://docs.opencv.org/ — https://github.com/pyusb/pyusb — https://pyserial.readthedocs.io/
