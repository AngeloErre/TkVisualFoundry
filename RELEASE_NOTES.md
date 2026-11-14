# TkVisualFoundry 1.41

Complete the 32-starter collection with Micro Invaders, Dot Maze Chase, Mini Platformer, Falling Blocks, Neural Driving Lab, Study Agent, QR and Barcode Studio, and Soundboard. Each has editable designer controls and English-commented helper/startup/event code. Games use original geometric graphics and cancellable timers. Neural Driving trains a real small supervised tanh network. Study Agent reuses the async OpenAI client; Code Studio creates and decodes local QR/Code128 images; Soundboard assigns eight local-file pads to the existing audio player.

The chooser shows project dependencies: 29 starters need no additional PIP; the other three use OpenAI, QR/barcode imaging or pygame-ce. Models and API keys remain user-configured; no requests or audio start automatically. Sound paths are session-only; no media is bundled. See [starter guide](docs/STARTER_TEMPLATES.md).

Remote Python 3.15.2/Linux: 394 tests passed per language, 11 graphical tests skipped; all 47 examples validate and compile. Nineteen new offline regressions include real QR/Code128 PNG round trips with qrcode 8.2, python-barcode 0.16.1, zxing-cpp 3.1.1 and Pillow 12.3.0. Service/audio actions are mocked. The trained neural simulation also completed 2500 steps / 10000 distance units without leaving the road in a deterministic remote check.

Mac GUI, keyboard/audio behavior, live API use, native package installation and generated-app builds remain pending until the user reports **ambiente collegato**. No Mac access or native validation is claimed. Checklist: [MAC_RECONNECT_CHECKLIST.md](docs/MAC_RECONNECT_CHECKLIST.md).
