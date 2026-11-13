"""Conservative, token-aware value assistance for designer objects."""
import io
import re
import tokenize
from code_assist import objects, properties

ENUMS = {'state':('normal','disabled','readonly'), 'orient':('horizontal','vertical'),
         'anchor':('center','n','s','e','w','ne','nw','se','sw'),
         'justify':('left','center','right'), 'relief':('flat','raised','sunken','groove','ridge','solid'),
         'wrap':('none','char','word'), 'compound':('none','left','right','top','bottom','center')}
STRINGS = {'text','bg','fg','background','foreground','font','cursor','text_color','fg_color',
           'bg_color','placeholder_text','placeholder_text_color','border_color','hover_color'}

def value_context(before, project):
    # A partial quoted string is accepted only immediately after a named option.
    match=re.search(r"\b([A-Za-z_]\w*)\s*=\s*(?:([\"'])([^\"'\n\\]*))?$", before)
    if not match:return None
    head=before[:match.start()];tokens=[]
    try:
        for token in tokenize.generate_tokens(io.StringIO(head).readline):
            if token.type==tokenize.COMMENT and token.end[0]==head.count('\n')+1:return None
            if token.type==tokenize.ERRORTOKEN and token.string.strip():return None
            if token.type not in (tokenize.NL,tokenize.NEWLINE,tokenize.INDENT,tokenize.DEDENT,tokenize.ENDMARKER):tokens.append(token.string)
    except tokenize.TokenError as exc:
        if 'string' in str(exc):return None
    except (IndentationError,SyntaxError):return None
    stack=[]
    for i,t in enumerate(tokens):
        if t in ('(','[','{'):stack.append(i)
        elif t in (')',']','}'):
            if stack:stack.pop()
    if not stack:return None
    i=stack[-1]
    if i<5 or tokens[i-5]!='self' or tokens[i-4]!='.' or tokens[i-2]!='.':return None
    if tokens[i-1] not in ('configure','config'):return None
    if tokens[-1] not in ('(',','):return None
    obj=objects(project).get(tokens[i-3]);key=match.group(1)
    if not obj:return None
    props=properties(obj,project)
    if key not in props:return None
    value=props.get(key)
    string=isinstance(value,str) or key in STRINGS or key in ENUMS
    return {'kind':obj.get('kind','Tk'),'key':key,'value':value,'string':string,'quote':match.group(2),'prefix':match.group(3) or ''}

def quote_pair(before, after, project):
    context=value_context(before,project)
    if not context or context['quote'] or not context['string']:return ''
    # Never replace an existing value or another expression.
    if after.lstrip() and after.lstrip()[0] not in '),\n':return ''
    return "''"

def value_items(before, project):
    c=value_context(before,project)
    if not c:return []
    values=ENUMS.get(c['key'],(True,False) if isinstance(c['value'],bool) else (c['value'],))
    if c['key']=='state' and c['kind'] not in ('Combobox','Spinbox','TSpinbox','TEntry'):values=tuple(v for v in values if v!='readonly')
    result=[]
    for value in values:
        if value is None:continue
        text=str(value) if c['quote'] else repr(value)
        if not text.startswith(c['prefix']):continue
        result.append({'name':text,'insert':text,'prefix_len':len(c['prefix']),'kind':'value',
                       'doc':f"{c['key']} • {type(value).__name__}"})
    return result
