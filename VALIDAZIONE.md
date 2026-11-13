# Versione 1.15

155 test superati; 11 grafici saltati. Verificate otto maniglie, conservazione dei bordi opposti, limiti minimi/coordinate e palette sintassi chiare/scure. La riorganizzazione grafica richiede verifica interattiva a diverse dimensioni; non è una replica MDI con pannelli flottanti.

# Versione 1.14

151 test superati; 11 test grafici saltati. Nuovi controlli: valori tipizzati, stringhe/commenti invariati, chiamate multilinea, descrittori esterni, riferimento locale per tutti i componenti, versioni stabili/Python compatibili, release ritirate e distinzione errori HTTP/rete. Nessun aggiornamento di pacchetti eseguito dal controllo di avvio. Verifica interattiva di digitazione/focus e avvio app ancora necessaria.

# Validation — 1.13

141 tests passed, 11 graphical tests skipped on macOS Python 3.15.2 / Jedi 0.20.0.

New tests cover real temporary Excel workbook/formula/sheet round-trips, VBA format guards, PDF merge/extraction/AES password handling, atomic file preservation, all six generated components, provider-specific dependencies, credential property validation, session/environment secret redaction, job queues and contextual examples.

OpenAI, Claude, Gemini, MIDI, print, Drive and S3 protocols are tested with mocks. No real credentials, paid LLM calls, OAuth account access, uploads, MIDI device playback or physical print jobs were used.

Actual imports passed: openpyxl 3.1.5, pypdf 7.0.1, mido 1.3.3, python-rtmidi 1.5.8 (built locally), openai 3.50.0, anthropic 1.17.0, google-genai 2.34.0, google-api-python-client 2.202.0 and boto3 1.44.2. Imports do not certify remote-service access.

A real PyInstaller 6.22.3 Office example build produced a macOS app and ZIP. Document library resources and ad hoc codesign verification were checked. hdiutil could not create a DMG in this session, so ZIP fallback was used.

Graphical app launch, live cloud/OAuth/LLM requests, real MIDI/printing, Windows builds and clean-machine installation require target-system validation. Excel formula evaluation, PDF OCR/rendering, built-in MIDI synthesis, automatic cloud synchronization and automatic LLM conversation history are not implemented.
