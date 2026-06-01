from django.urls import path
from . import views


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from vercel_blob import put  # necesitas instalar vercel-blob

@csrf_exempt
def get_upload_url(request):
    # Solo permitir POST
    if request.method == 'POST':
        filename = request.POST.get('filename')
        # Generar URL de subida (put) que expira en 1 hora
        blob_url = put(filename, max_size=50*1024*1024)  # 50 MB
        return JsonResponse({'url': blob_url})
    return JsonResponse({'error': 'Método no permitido'}, status=405)

urlpatterns = [
    path('', views.subir_y_combinar, name='subir'),
]