"""Bounded read-only data previews. Executable as a worker in the project Python."""
import csv
import datetime
import itertools
import json
import sqlite3
import sys
from collections import Counter
from pathlib import Path

MAX_ROWS=500
MAX_COLUMNS=80
MAX_BYTES=32*1024*1024
REQUIREMENTS={'.xlsx':['openpyxl>=3.1,<4'],'.xlsm':['openpyxl>=3.1,<4'],'.xls':['xlrd>=2,<3'],'.mdb':['pyodbc>=5,<6'],'.accdb':['pyodbc>=5,<6'],'.dbf':['dbfread>=2,<3'],'.parquet':['pyarrow>=15']}


def cell(value):
    if value is None:return 'NULL'
    if isinstance(value,bytes):return '<binary: %d bytes>'%len(value)
    if isinstance(value,(dict,list)):return json.dumps(value,ensure_ascii=False,default=str)[:512]
    return str(value)[:512]


def table_result(names,selected,columns,rows):
    result={'datasets':list(names)[:500],'selected':selected,'columns':[str(c)[:128] for c in list(columns)[:MAX_COLUMNS]],'rows':[],'limited':False}
    budget=0
    for row in itertools.islice(rows,MAX_ROWS+1):
        if len(result['rows'])==MAX_ROWS:result['limited']=True;break
        values=[cell(v) for v in list(row)[:MAX_COLUMNS]];values+=['']*(len(result['columns'])-len(values));values=values[:len(result['columns'])]
        budget+=len(json.dumps(values,ensure_ascii=False).encode('utf-8'))
        if budget>3*1024*1024:result['limited']=True;break
        result['rows'].append(values)
    return result


def records_result(names,selected,records):
    records=list(itertools.islice(records,MAX_ROWS+1))
    keys=list(dict.fromkeys(str(k) for r in records if isinstance(r,dict) for k in r))[:MAX_COLUMNS]
    if not keys:keys=['value']
    return table_result(names,selected,keys,([r.get(k) for k in keys] if isinstance(r,dict) else [r] for r in records))


def choose(names,selected):
    if not names:return ''
    return selected if selected in names else names[0]


def preview(filename,dataset=''):
    p=Path(filename).expanduser().resolve(strict=True)
    if not p.is_file():raise ValueError('Select a regular data file.')
    ext=p.suffix.lower()
    with p.open('rb') as f:magic=f.read(16)
    if magic==b'SQLite format 3\x00':
        con=sqlite3.connect(p.as_uri()+'?mode=ro',uri=True,timeout=2)
        try:
            con.execute('PRAGMA query_only=ON')
            if hasattr(con,'enable_load_extension'):con.enable_load_extension(False)
            con.execute('PRAGMA trusted_schema=OFF')
            names=[r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name LIMIT 500")]
            name=choose(names,dataset)
            if not name:return table_result([],name,[],[])
            quoted='"'+name.replace('"','""')+'"'
            cursor=con.execute('SELECT * FROM '+quoted+' LIMIT ?', (MAX_ROWS+1,))
            result=table_result(names,name,[c[0] for c in cursor.description],cursor)
        finally:con.close()
    elif ext in ('.sqlite','.sqlite3','.db'):
        raise ValueError('This file is not a SQLite database. Export the source database to SQLite, CSV or JSON.')
    elif ext=='.dbx':
        raise ValueError('DBX is ambiguous (including Outlook mail archives). Only DBX files with a SQLite header are readable. Export other DBX data to CSV or JSON.')
    elif ext in ('.mdb','.accdb'):
        import pyodbc
        drivers=[d for d in pyodbc.drivers() if 'access' in d.lower() and ('mdb' in d.lower() or 'accdb' in d.lower())]
        if not drivers:raise ValueError('Access requires a compatible Microsoft Access ODBC driver (matching Python architecture). PIP alone cannot install it. On macOS/Linux export to SQLite or CSV if no compatible driver is available.')
        escape=lambda s:'{'+s.replace('}','}}')+'}'
        con=pyodbc.connect('DRIVER='+escape(drivers[-1])+';DBQ='+escape(str(p))+';',readonly=True,timeout=5)
        try:
            cur=con.cursor();names=sorted(r.table_name for r in cur.tables(tableType='TABLE'))[:500];name=choose(names,dataset)
            if not name:return table_result([],name,[],[])
            cur.execute('SELECT TOP '+str(MAX_ROWS+1)+' * FROM ['+name.replace(']',']]')+']')
            result=table_result(names,name,[c[0] for c in cur.description],cur)
        finally:con.close()
    elif ext in ('.xlsx','.xlsm'):
        from openpyxl import load_workbook
        book=load_workbook(p,read_only=True,data_only=False,keep_links=False)
        try:
            name=choose(book.sheetnames,dataset);sheet=book[name]
            # Preserve the first spreadsheet row as data: never guess whether it is a header.
            columns=['C'+str(i+1) for i in range(min(sheet.max_column or 1,MAX_COLUMNS))]
            result=table_result(book.sheetnames,name,columns,sheet.iter_rows(max_col=MAX_COLUMNS,values_only=True))
        finally:book.close()
    elif ext=='.xls':
        import xlrd
        book=xlrd.open_workbook(str(p),on_demand=True)
        try:
            names=book.sheet_names();name=choose(names,dataset);sheet=book.sheet_by_name(name)
            result=table_result(names,name,['C'+str(i+1) for i in range(min(sheet.ncols,MAX_COLUMNS))],(sheet.row_values(i) for i in range(min(sheet.nrows,MAX_ROWS+1))))
        finally:book.release_resources()
    elif ext=='.parquet':
        import pyarrow.parquet as pq
        with pq.ParquetFile(p) as source:
            columns=source.schema_arrow.names[:MAX_COLUMNS]
            rows=(record for batch in source.iter_batches(batch_size=MAX_ROWS+1,columns=columns) for record in batch.to_pylist())
            result=table_result(['data'],'data',columns,([r.get(k) for k in columns] for r in rows))
    elif ext=='.dbf':
        from dbfread import DBF
        source=DBF(str(p),load=False)
        result=table_result(['data'],'data',source.field_names,(list(r.values()) for r in source))
    else:
        if p.stat().st_size>MAX_BYTES:raise ValueError('Text/JSON preview is limited to 32 MiB. Split or export the file first.')
        if ext in ('.json','.jsonl','.ndjson'):
            with p.open(encoding='utf-8-sig') as f:
                if ext!='.json':result=records_result(['data'],'data',(json.loads(line) for line in f if line.strip()))
                else:
                    data=json.load(f)
                    if isinstance(data,dict) and any(isinstance(v,list) for v in data.values()):
                        names=[k for k,v in data.items() if isinstance(v,list)];name=choose(names,dataset);records=data[name]
                    else:names=['data'];name='data';records=data if isinstance(data,list) else [data]
                    result=records_result(names,name,iter(records))
        elif ext in ('.csv','.tsv','.txt'):
            with p.open(encoding='utf-8-sig',newline='') as f:
                sample=f.read(8192);f.seek(0)
                try:dialect=csv.Sniffer().sniff(sample,delimiters=',;\t|')
                except csv.Error:dialect=csv.excel_tab if ext=='.tsv' else csv.excel
                reader=csv.reader(f,dialect);header=next(reader,[])
                result=table_result(['data'],'data',header,reader)
        elif ext=='.sql':
            with p.open(encoding='utf-8-sig') as f:result=table_result(['SQL script'],'SQL script',['line','SQL (not executed)'],enumerate(f,1))
        else:raise ValueError('Unsupported format. Use SQLite, SQL text, Access, Excel, CSV/TSV, JSON/JSONL, DBF or Parquet.')
    result['path']=str(p);result['read_at']=datetime.datetime.now().astimezone().isoformat(timespec='seconds')
    result['stamp']=[p.stat().st_mtime_ns,p.stat().st_size]
    result['note']='First 500 rows, 80 columns, 512 characters per cell; CSV first row is a header. Excel formulas are shown, not calculated. Comparison covers this preview only.'
    return result


def difference(before,after):
    if before['path']!=after['path'] or before['selected']!=after['selected']:return None
    old=Counter(tuple(r) for r in before['rows']);new=Counter(tuple(r) for r in after['rows'])
    return {'added':sum((new-old).values()),'removed':sum((old-new).values()),'columns_changed':before['columns']!=after['columns']}


if __name__=='__main__':
    try:
        request=json.load(sys.stdin);answer={'ok':True,'data':preview(request['path'],request.get('dataset',''))}
    except ModuleNotFoundError as error:answer={'ok':False,'missing':error.name,'error':str(error)}
    except Exception as error:answer={'ok':False,'error':str(error)[:1500]}
    print(json.dumps(answer,ensure_ascii=True))
