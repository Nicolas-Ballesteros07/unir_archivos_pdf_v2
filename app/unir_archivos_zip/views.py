import os
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from .utils import combinar_en_pdf_desde_urls

@require_http_methods(['GET', 'POST'])
def subir_y_combinar(request):
    # Obtener variables de entorno necesarias
    blob_token = os.environ.get('BLOB_READ_WRITE_TOKEN', '')
    blob_store_id = os.environ.get('BLOB_STORE_ID', '')  # Opcional, para construir la URL

    if request.method == 'POST':
        zip_url = request.POST.get('zip_url')
        pdf_urls1 = request.POST.getlist('pdf_urls1')
        pdf_urls2 = request.POST.getlist('pdf_urls2')

        if not zip_url and not pdf_urls1 and not pdf_urls2:
            return render(request, 'subir.html', {
                'error': 'Debes subir al menos un PDF o un ZIP.',
                'blob_token': blob_token,
                'blob_store_id': blob_store_id,
            })

        try:
            pdf_bytes = combinar_en_pdf_desde_urls(zip_url, pdf_urls1, pdf_urls2)
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="combinado.pdf"'
            return response
        except Exception as e:
            print(f"ERROR: {e}")
            return render(request, 'subir.html', {
                'error': f'Error interno: {str(e)}',
                'blob_token': blob_token,
                'blob_store_id': blob_store_id,
            })
    # GET
    return render(request, 'subir.html', {
        'blob_token': blob_token,
        'blob_store_id': blob_store_id,
    })