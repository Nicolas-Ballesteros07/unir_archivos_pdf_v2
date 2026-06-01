import requests
import tempfile
import os
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings

from .utils import combinar_en_pdf_desde_urls

@require_http_methods(['GET', 'POST'])
def subir_y_combinar(request):
    if request.method == 'POST':
        zip_url = request.POST.get('zip_url')  # URL del ZIP en Blob
        pdf_urls = request.POST.getlist('pdf_urls')  # URLs de los PDFs
        
        # Validar que al menos haya algún archivo
        if not zip_url and not pdf_urls:
            return render(request, 'mi_app/subir.html', {
                'error': 'Debes subir al menos un archivo ZIP o un PDF.'
            })
        
        try:
            pdf_bytes = combinar_en_pdf_desde_urls(zip_url, pdf_urls)
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="combinado.pdf"'
            return response
        except Exception as e:
            return render(request, 'mi_app/subir.html', {
                'error': f'Error al procesar: {str(e)}'
            })
    
    return render(request, 'subir.html')