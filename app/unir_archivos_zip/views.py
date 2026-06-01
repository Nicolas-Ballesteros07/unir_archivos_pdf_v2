import os
import requests
import tempfile
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings

from .utils import combinar_en_pdf_desde_urls
import vercel_blob  # para generar URLs de subida


@require_http_methods(['GET', 'POST'])
def subir_y_combinar(request):
    if request.method == 'POST':
        zip_url = request.POST.get('zip_url')
        pdf_urls = request.POST.getlist('pdf_urls')
        
        if not zip_url and not pdf_urls:
            return render(request, 'subir.html', {
                'error': 'Debes subir al menos un archivo ZIP o un PDF.'
            })
        
        try:
            pdf_bytes = combinar_en_pdf_desde_urls(zip_url, pdf_urls)
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="combinado.pdf"'
            return response
        except Exception as e:
            # Mejor mostrar el error en logs de Vercel
            print(f"ERROR en combinación: {e}")
            return render(request, 'subir.html', {'error': f'Error interno: {str(e)}'})
    
    # GET: pasa el token para generar URLs de subida (opcional, pero no exponemos el token directamente)
    # En su lugar, pasamos una URL de API para que el frontend solicite URLs firmadas.
    # Por simplicidad, aquí devolvemos el template sin token y el frontend usará el endpoint.
    return render(request, 'subir.html')


# Endpoint para obtener una URL de subida a Vercel Blob (sin exponer el token)
@csrf_exempt
@require_http_methods(['POST'])
def get_upload_url(request):
    import json
    data = json.loads(request.body)
    filename = data.get('filename')
    if not filename:
        return JsonResponse({'error': 'Falta filename'}, status=400)
    try:
        # put() devuelve la URL pública donde se debe subir con PUT
        result = vercel_blob.put(filename, max_size=50*1024*1024)  # 50 MB
        # result es un dict con 'url'
        return JsonResponse({'url': result['url']})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)