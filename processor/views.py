from io import BytesIO
from PIL import Image
from django.shortcuts import render
from rembg import remove
from django.http import HttpResponse, JsonResponse


def health_check(request):
    return JsonResponse({'status': 'OK'})

def home(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('image')
        if uploaded_file:
            input_image = Image.open(uploaded_file)

            output_image = remove(input_image)

            img_io = BytesIO()
            output_image.save(img_io, format='PNG')
            img_io.seek(0)

            return HttpResponse(img_io, content_type='image/png')
    return render(request, 'processor/home.html')