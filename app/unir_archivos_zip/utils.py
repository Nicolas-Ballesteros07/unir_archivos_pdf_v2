import requests
import tempfile
import os
from io import BytesIO
from pathlib import Path
import zipfile

from pypdf import PdfMerger
from PIL import Image
import img2pdf

def descargar_archivo(url):
    """Descarga un archivo desde una URL y devuelve la ruta de un archivo temporal."""
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    # Detectamos extensión por Content-Type o por URL
    content_type = resp.headers.get('content-type', '')
    if 'zip' in content_type or url.endswith('.zip'):
        suffix = '.zip'
    elif 'pdf' in content_type or url.endswith('.pdf'):
        suffix = '.pdf'
    else:
        suffix = '.tmp'
    
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(resp.content)
        return tmp.name

def procesar_zip_desde_ruta(ruta_zip, merger):
    """Igual que antes, recibe ruta de ZIP y agrega al merger."""
    with zipfile.ZipFile(ruta_zip, 'r') as zf:
        for nombre in sorted(zf.namelist()):
            with zf.open(nombre) as f:
                data = f.read()
                extension = Path(nombre).suffix.lower()
                
                if extension == '.pdf':
                    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
                        tmp_pdf.write(data)
                        tmp_pdf.flush()
                        merger.append(tmp_pdf.name)
                    os.unlink(tmp_pdf.name)
                
                elif extension in ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'):
                    try:
                        pdf_bytes = img2pdf.convert(BytesIO(data))
                        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_img:
                            tmp_img.write(pdf_bytes)
                            tmp_img.flush()
                            merger.append(tmp_img.name)
                        os.unlink(tmp_img.name)
                    except Exception:
                        img = Image.open(BytesIO(data))
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_img:
                            img.save(tmp_img.name, 'PDF')
                            merger.append(tmp_img.name)
                        os.unlink(tmp_img.name)

def combinar_en_pdf_desde_urls(zip_url, pdf_urls):
    """Recibe URL del ZIP y lista de URLs de PDFs, devuelve bytes del PDF final."""
    merger = PdfMerger()
    temp_files = []  # Para limpiar después
    
    try:
        # Procesar ZIP si existe
        if zip_url:
            zip_path = descargar_archivo(zip_url)
            temp_files.append(zip_path)
            procesar_zip_desde_ruta(zip_path, merger)
        
        # Procesar PDFs desde URLs
        for pdf_url in pdf_urls:
            pdf_path = descargar_archivo(pdf_url)
            temp_files.append(pdf_path)
            merger.append(pdf_path)
        
        # Escribir resultado
        output = BytesIO()
        merger.write(output)
        merger.close()
        output.seek(0)
        return output.getvalue()
    
    finally:
        # Limpiar archivos temporales
        for path in temp_files:
            if os.path.exists(path):
                os.unlink(path)