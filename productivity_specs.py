"""Built-in productivity descriptors and provider-specific requirements."""
from i18n import tr

PROVIDER_REQUIREMENTS={
 'openai':['openai>=2,<4'],'anthropic':['anthropic>=0.70,<2'],'gemini':['google-genai>=1,<3'],
 'drive':['google-api-python-client>=2,<3','google-auth-oauthlib>=1,<2','google-auth-httplib2>=0.2,<1'],
 's3':['boto3>=1.35,<2'],'webdav':['requests>=2.32,<3'],
}
PRODUCTIVITY_COMPONENTS={
 'MIDIPlayer':{'family':'MIDI','defaults':{'source':'','port':''},'requirements':['mido>=1.3,<2','python-rtmidi>=1.5,<2'],'description':tr('Riproduce file MIDI su un’uscita collegata a un sintetizzatore; pausa e stop.')},
 'ExcelWorkbook':{'family':'Excel','defaults':{'source':'','sheet':'','preview_rows':500},'requirements':['openpyxl>=3.1,<4'],'description':tr('Legge, crea e modifica file XLSX/XLSM, fogli e celle. Non calcola formule.')},
 'PDFDocument':{'family':'PDF','defaults':{'source':''},'requirements':['pypdf[crypto]>=6,<8'],'description':tr('Testo PDF, unione ed estrazione pagine; anteprima testuale, senza OCR.')},
 'PrintDocument':{'family':'Stampa','defaults':{'source':'','printer':'','copies':1},'requirements':[],'description':tr('Anteprima con l’app associata e invio al sistema di stampa. Richiede stampante e driver.')},
 'CloudStorage':{'family':'Cloud','defaults':{'provider':'drive','folder':'root','bucket':'','auth_mode':'desktop','scope':'app','client_env':'GOOGLE_OAUTH_CLIENT_FILE','token_env':'GOOGLE_TOKEN_FILE','endpoint_env':'S3_ENDPOINT_URL','url_env':'WEBDAV_URL','user_env':'WEBDAV_USER','password_env':'WEBDAV_PASSWORD'},'requirements':[],'description':tr('Google Drive, S3/MinIO e WebDAV: elenco, caricamento e download. Credenziali esterne.')},
 'LLMClient':{'family':'LLM','defaults':{'provider':'openai','model':'','api_key_env':'','max_tokens':1024},'requirements':[],'description':tr('API OpenAI, Claude e Gemini: scelta modello, invio testo e risposta asincrona. Chiavi esterne.')},
}
for name,descriptor in PRODUCTIVITY_COMPONENTS.items():descriptor.update(module='productivity_runtime',**{'class':name})

def productivity_requirements(kind,props=None):
    descriptor=PRODUCTIVITY_COMPONENTS.get(kind)
    if not descriptor:return []
    values={**descriptor['defaults'],**(props or {})}
    return PROVIDER_REQUIREMENTS.get(values['provider'],[]) if kind in ('CloudStorage','LLMClient') else list(descriptor['requirements'])

def validate_productivity(kind,props):
    if kind=='ExcelWorkbook' and not 1<=int(props.get('preview_rows',500))<=2000:raise ValueError('Preview rows must be 1–2000')
    if kind=='PrintDocument' and not 1<=int(props.get('copies',1))<=100:raise ValueError('Copies must be 1–100')
    if kind=='LLMClient':
        if props.get('provider','openai') not in ('openai','anthropic','gemini'):raise ValueError('Invalid LLM provider')
        if not 1<=int(props.get('max_tokens',1024))<=32768:raise ValueError('Output token limit must be 1–32768')
    if kind=='CloudStorage':
        if props.get('provider','drive') not in ('drive','s3','webdav'):raise ValueError('Invalid cloud provider')
        if props.get('auth_mode','desktop') not in ('desktop','adc') or props.get('scope','app') not in ('app','all'):raise ValueError('Invalid Google authorization mode/scope')
    if kind in PRODUCTIVITY_COMPONENTS:
        for key,value in props.items():
            if key.endswith('_env') and (not isinstance(value,str) or (value and not value.isidentifier())):raise ValueError('Use an environment variable NAME for '+key+'; do not enter credentials')
        if any(key in props for key in ('api_key','access_token','refresh_token','password','client_secret')):raise ValueError('Credentials must remain outside project files')
