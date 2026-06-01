import requests
import tempfile
import os
from io import BytesIO
from pathlib import Path
import zipfile

from pypdf import PdfWriter
from PIL import Image
import img2pdf


def descargar_archivo(url):
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
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


def procesar_zip_desde_ruta(ruta_zip, writer):
    """Añade al writer el contenido del ZIP (orden alfabético)."""
    with zipfile.ZipFile(ruta_zip, 'r') as zf:
        for nombre in sorted(zf.namelist()):
            with zf.open(nombre) as f:
                data = f.read()
                extension = Path(nombre).suffix.lower()
                if extension == '.pdf':
                    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
                        tmp_pdf.write(data)
                        tmp_pdf.flush()
                        with open(tmp_pdf.name, 'rb') as pdf_file:
                            writer.append(pdf_file)
                    os.unlink(tmp_pdf.name)
                elif extension in ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'):
                    try:
                        pdf_bytes = img2pdf.convert(BytesIO(data))
                        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_img:
                            tmp_img.write(pdf_bytes)
                            tmp_img.flush()
                            with open(tmp_img.name, 'rb') as pdf_file:
                                writer.append(pdf_file)
                        os.unlink(tmp_img.name)
                    except Exception:
                        img = Image.open(BytesIO(data))
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_img:
                            img.save(tmp_img.name, 'PDF')
                            with open(tmp_img.name, 'rb') as pdf_file:
                                writer.append(pdf_file)
                        os.unlink(tmp_img.name)


def combinar_en_pdf_desde_urls(zip_url, pdf_urls1, pdf_urls2):
    """
    Orden: PDFs grupo1 → PDFs grupo2 → contenido del ZIP (orden alfabético).
    """
    writer = PdfWriter()
    temp_files = []

    try:
        # 1. Añadir PDFs del grupo 1
        for pdf_url in pdf_urls1:
            pdf_path = descargar_archivo(pdf_url)
            temp_files.append(pdf_path)
            with open(pdf_path, 'rb') as f:
                writer.append(f)

        # 2. Añadir PDFs del grupo 2
        for pdf_url in pdf_urls2:
            pdf_path = descargar_archivo(pdf_url)
            temp_files.append(pdf_path)
            with open(pdf_path, 'rb') as f:
                writer.append(f)

        # 3. Procesar ZIP (si existe)
        if zip_url:
            zip_path = descargar_archivo(zip_url)
            temp_files.append(zip_path)
            procesar_zip_desde_ruta(zip_path, writer)

        # Escribir resultado
        output = BytesIO()
        writer.write(output)
        writer.close()
        output.seek(0)
        return output.getvalue()

    finally:
        for path in temp_files:
            if os.path.exists(path):
                os.unlink(path)