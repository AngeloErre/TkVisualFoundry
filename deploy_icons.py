"""Validate/import application artwork and prepare native build icon formats."""
import hashlib
import io
from pathlib import Path
from project_files import project_file

def icon_image(source):
    from PIL import Image,ImageOps
    source=Path(source)
    if source.suffix.lower() not in ('.png','.ico','.icns'):raise ValueError('Choose a PNG, ICO or ICNS icon.')
    if source.stat().st_size>32*1024*1024:raise ValueError('Icon file exceeds 32 MB.')
    with Image.open(source) as image:
        if image.format not in ('PNG','ICO','ICNS'):raise ValueError('Unsupported icon image format.')
        if image.width!=image.height or not 256<=image.width<=4096:raise ValueError('Use a square icon between 256 and 4096 pixels; 1024 is recommended.')
        image.load();result=ImageOps.exif_transpose(image).convert('RGBA')
    return result.resize((1024,1024),Image.Resampling.LANCZOS)

def import_icon(source,root):
    image=icon_image(source);output=io.BytesIO();image.save(output,format='PNG');data=output.getvalue()
    relative='assets/app-icons/'+hashlib.sha256(data).hexdigest()+'.png'
    target=project_file(root,relative);target.parent.mkdir(parents=True,exist_ok=True)
    if not target.exists():target.write_bytes(data)
    return relative

def prepare_icons(source,kit):
    image=icon_image(source);folder=Path(kit)/'build-assets';folder.mkdir()
    image.save(folder/'app.icns',format='ICNS')
    image.save(folder/'app.ico',format='ICO',sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
    image.save(Path(kit)/'src/_visualtk_icon.png',format='PNG')
    return {'mac':'build-assets/app.icns','windows':'build-assets/app.ico','runtime':'_visualtk_icon.png'}
