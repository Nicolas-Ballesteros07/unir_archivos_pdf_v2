import json
import vercel_blob
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .utils import combinar_en_pdf_desde_urls


@require_http_methods(['GET', 'POST'])
def subir_y_combinar(request):
    if request.method == 'POST':
        zip_url = request.POST.get('zip_url')
        pdf_urls1 = request.POST.getlist('pdf_urls1')
        pdf_urls2 = request.POST.getlist('pdf_urls2')

        if not zip_url and not pdf_urls1 and not pdf_urls2:
            return render(request, 'subir.html', {
                'error': 'Debes subir al menos un PDF o un ZIP.'
            })

        try:
            pdf_bytes = combinar_en_pdf_desde_urls(zip_url, pdf_urls1, pdf_urls2)
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="combinado.pdf"'
            return response
        except Exception as e:
            print(f"ERROR en combinación: {e}")
            return render(request, 'subir.html', {'error': f'Error interno: {str(e)}'})

    return render(request, 'subir.html')


@csrf_exempt
@require_http_methods(['POST'])
def get_upload_url(request):
    try:
        data = json.loads(request.body)
        filename = data.get('filename')
        if not filename:
            return JsonResponse({'error': 'Falta el nombre del archivo'}, status=400)

        result = vercel_blob.put(filename, max_size=50 * 1024 * 1024)
        return JsonResponse({'url': result['url']})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)