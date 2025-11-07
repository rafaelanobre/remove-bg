import base64
import uuid

from django.http import JsonResponse
from django.shortcuts import render

from processor.models import ProcessingTask
from processor.tasks import process_image_task


def health_check(request):
    return JsonResponse({'status': 'OK'})


def home(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('image')
        if not uploaded_file:
            return JsonResponse({
                'error': 'No image file provided'
            }, status=400)

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

    return render(request, 'processor/home.html')
