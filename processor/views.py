import base64
import json
import os
import uuid

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from PIL import Image, UnidentifiedImageError

from processor.models import ProcessingTask
from processor.tasks import process_image_task


def health_check(request):
    return JsonResponse({'status': 'OK'})


def get_task_status(request, task_id):
    """
    API endpoint to check the status of a background processing task.

    Returns JSON with current task status, result URL (if completed), and error (if failed).
    """
    try:
        task = ProcessingTask.objects.get(task_id=task_id)

        response_data = {
            'status': task.status,
            'result_url': task.result_url,
            'error': task.error_message,
        }

        return JsonResponse(response_data)

    except ProcessingTask.DoesNotExist:
        return JsonResponse(
            {'error': 'Task not found'},
            status=404
        )


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

        image_bytes = uploaded_file.read()
        image_data_b64 = base64.b64encode(image_bytes).decode('utf-8')

        task_id = str(uuid.uuid4())

        ProcessingTask.objects.create(
            task_id=task_id,
            status='pending'
        )

        process_image_task.apply_async(
            args=(image_data_b64, task_id),
            task_id=task_id
        )

        return JsonResponse({
            'task_id': task_id,
            'status': 'pending'
        })

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
