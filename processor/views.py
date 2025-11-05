import json
import os
from io import BytesIO

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from PIL import Image, UnidentifiedImageError
from rembg import new_session, remove

_rembg_session = new_session()


def health_check(request):
    return JsonResponse({'status': 'OK'})


def validate_image_file(uploaded_file):
    """
    Validate uploaded image file for security and compatibility.

    Returns tuple: (is_valid: bool, error_message: str | None)
    """
    if not uploaded_file:
        return False, 'No file was uploaded'

    if uploaded_file.size > settings.MAX_UPLOAD_SIZE:
        max_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
        return False, f'File size exceeds maximum allowed size of {max_mb:.0f}MB'

    file_ext = os.path.splitext(uploaded_file.name)[1].lower()
    if file_ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
        allowed_formats = ', '.join(settings.ALLOWED_IMAGE_EXTENSIONS)
        return False, f'Invalid file type. Allowed formats: {allowed_formats}'

    if uploaded_file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        return False, 'Invalid file format. Please upload a valid image file'

    try:
        img = Image.open(uploaded_file)
        img.verify()
        uploaded_file.seek(0)  # Reset file pointer after verify() consumes it
        return True, None
    except UnidentifiedImageError:
        return False, 'Unable to process file. Please upload a valid image'
    except Exception as e:
        return False, f'Error validating image: {e!s}'


def home(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('image')

        is_valid, error_message = validate_image_file(uploaded_file)
        if not is_valid:
            return JsonResponse({'error': error_message}, status=400)

        try:
            input_image = Image.open(uploaded_file)
            output_image = remove(input_image, session=_rembg_session)

            img_io = BytesIO()
            output_image.save(img_io, format='PNG')
            img_io.seek(0)

            return HttpResponse(img_io, content_type='image/png')

        except Exception:
            return JsonResponse(
                {
                    'error': 'Failed to process image. Please try again or use a different image'
                },
                status=500,
            )

    context = {
        'upload_config': json.dumps(
            {
                'maxFileSize': settings.MAX_UPLOAD_SIZE,
                'allowedTypes': settings.ALLOWED_IMAGE_TYPES,
                'allowedExtensions': settings.ALLOWED_IMAGE_EXTENSIONS,
            }
        )
    }

    return render(request, 'processor/home.html', context)
