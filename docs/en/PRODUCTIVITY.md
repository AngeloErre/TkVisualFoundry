# MIDI, Excel, PDF, printing, cloud and LLM components

The six controls are part of the default palette. Use **Actions → Configure component…**, then **Save and prepare dependencies…**. Provider-specific packages are installed in the selected project interpreter. Local resources must be explicitly included for deployment. The designer never opens documents, plays MIDI, connects accounts or sends API requests.

Slow operations run in worker threads; completion handlers and virtual events run on the Tk thread. Each component runs one task at a time. Errors emit **ServiceError** and populate `.error`.

## MIDIPlayer

Open a .mid/.midi file, list MIDI outputs, choose an output connected to a synthesizer, then play. APIs: refresh_ports(), play(path), pause(), stop(). Events: MidiStarted/MidiFinished. A normal type 0/1 MIDI file contains notes and commands, not audio. mido/python-rtmidi provide MIDI output, not an included audio synthesizer or SoundFont. An external/virtual synthesizer and appropriate drivers are required. A virtual MIDI port alone does not make sound. Stop/pause reset output controls to avoid hanging notes.

## ExcelWorkbook

Supports XLSX/XLSM through openpyxl, sheets, cells and saving copies. The preview is limited to the configured rows and 50 columns; `.book` holds the full workbook. Cell indexes start at 1. APIs: load(path), create(headers=..., rows=...), set_cell(row,column,value), add_sheet(name), get_data(), save_as(path). Loading/creation/saving are asynchronous; wait for ExcelLoaded before accessing cells. Events: ExcelLoaded, ExcelChanged, ExcelSaved. get_data() returns preview rows, including any header row.

Formulas are preserved, not evaluated. XLS/XLSB are unsupported. Save macro workbooks as XLSM to preserve VBA; macros are not executed. Some complex Excel features may not survive openpyxl round-tripping, so work on copies. This component does not convert Excel to PDF.

## PDFDocument

Text preview of the first page, full text extraction, merge and selected-page export through pypdf with crypto support. This is not graphical PDF rendering or OCR; image-only scans may yield no text. Passwords for encrypted files are entered at runtime.

Asynchronous APIs: load(path,password=None), extract_text(), merge(paths,destination), extract_pages(indexes,destination), save_text(path). API page indexes are zero-based; the visual page-selection dialog uses numbers starting at 1. Events: PDFLoaded, PDFTextReady, PDFSaved. Read `.text`, `.page_count` and `.last_path` after completion.

## PrintDocument

Preview opens the document in its associated application; use that application's Print command for the native dialog and full options. Direct submission asks for confirmation. macOS uses CUPS/lp with optional printer and copy count. Windows delegates to the associated application's print verb using the default printer and one copy. Drivers, a printer and a compatible file handler are required.

PrintSubmitted means the request was handed off, not that paper was successfully printed. `.print_job` holds submission information. For Office formats, use the associated application or first export a PDF with a suitable program; this component is not an Excel renderer. No physical printing occurs during design or automated tests.

## CloudStorage

Choose drive, s3 or webdav. APIs: connect(), list_files(folder=None), upload(path,folder=None), download(file_id,destination). Events: CloudConnected, CloudListed, CloudTransferred. Read `.files`, `.last_transfer` and `.error`. Connection initializes authentication/client state; the first operation verifies access to the requested resource.

**Drive:** enable Drive API in your own Google Cloud project, configure consent and a Desktop OAuth client. Use Credentials… at runtime to select its JSON or set GOOGLE_OAUTH_CLIENT_FILE. Connect opens the consent flow. Tokens default to ~/.visualtkstudio-credentials/drive-app.json or drive-all.json, outside the project; GOOGLE_TOKEN_FILE may specify another external location. Test-user or organizational configuration may be required. App scope uses drive.file and sees app-created/opened/shared files, not the entire Drive. All scope requests broader consent and can require additional Google/organization verification. ADC mode uses previously configured Application Default Credentials. Service accounts only see resources shared/authorized for that account. The folder field takes an ID (root initially); this is not a complete folder browser. Native Google documents download as PDF; binary files keep their format. Upload creates a new Drive file. No remote deletion or automatic synchronization.

**S3/MinIO:** configure bucket and optional prefix, normally empty. Use standard AWS credentials or runtime Credentials… for the session. S3_ENDPOINT_URL or the session dialog can configure a MinIO HTTPS endpoint. Existing objects are not silently overwritten. Upload uses PutObject, not multipart upload for very large files.

**WebDAV:** Nextcloud/ownCloud-compatible listing, upload and download. Use runtime credentials or WEBDAV_URL, WEBDAV_USER and WEBDAV_PASSWORD. Supply the actual WebDAV root URL, not the service website. Listing is one level and upload does not replace existing files. HTTPS is required; HTTP is allowed only for localhost. This is not a full synchronization client.

## LLMClient

Choose openai, anthropic or gemini. Official SDKs use Responses, Messages and Generate Content APIs. This is a single text request per operation, without tools, attachments or automatic conversation history.

Supply a provider API account with model access, billing/quota and a key. A chat-app subscription does not configure API access. API key… keeps a key only for the session; alternatively use OPENAI_API_KEY, ANTHROPIC_API_KEY or GEMINI_API_KEY. List models or enter an account-accessible ID. Model listings may contain non-text models; choose an appropriate one. The output token limit does not guarantee a total cost.

Call send(prompt), then read `.response`, `.usage` and `.last_result` in LLMResponse. LLMModelsReady signals model listing. Text is sent only when the running app's user clicks Send or your code calls send(). No paid generation occurs during design or automated checks.

## Credentials and deployment

Project JSON stores settings and environment variable names, not secrets entered in runtime session dialogs. Session secrets remain in memory. Do not include OAuth clients, tokens, AWS credential files or keys in project resources. Deployed applications need their own user's/infrastructure credentials and authorization; developer accounts are not embedded.

The deploy kit collects configured provider SDKs, certificates and resources. Device playback, live accounts, physical printing and Windows require target-system validation. Automated tests use temporary files and mocked services, without paid LLM calls, uploads, personal credentials or print jobs.

Examples: examples/Productivity/OfficeDemo.vtk.json, ServicesDemo.vtk.json and MidiPrintDemo.vtk.json.
