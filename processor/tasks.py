import base64
import traceback
from io import BytesIO

from celery import shared_task
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from PIL import Image
from rembg import new_session, remove

from processor.models import ProcessingTask

# Preload model to avoid 3-5 second load time per task
_rembg_session = new_session()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_image_task(self, image_data_b64: str, task_id: str) -> dict:
    """
    Removes background from uploaded image asynchronously.

    Uses base64 encoding because Celery JSON serializer doesn't support raw bytes.
    Task retries up to 3 times on failure with exponential backoff.
    """
    task_record = None

    try:
        task_record = ProcessingTask.objects.get(task_id=task_id)
        task_record.mark_processing()

        image_bytes = base64.b64decode(image_data_b64)
        input_image = Image.open(BytesIO(image_bytes))

        output_image = remove(input_image, session=_rembg_session)

        output_buffer = BytesIO()
        output_image.save(output_buffer, format='PNG')
        output_buffer.seek(0)

        filename = f'processed/{task_id}.png'
        saved_path = default_storage.save(
            filename,
            ContentFile(output_buffer.read())
        )

        result_url = default_storage.url(saved_path)
        task_record.mark_completed(result_url)

        return {
            'status': 'completed',
            'result_url': result_url,
        }

    except ProcessingTask.DoesNotExist:
        error_msg = f"ProcessingTask with task_id={task_id} not found"
        return {
            'status': 'failed',
            'error': error_msg,
        }

    except Exception as exc:
        error_msg = f"{type(exc).__name__}: {str(exc)}\n{traceback.format_exc()}"

        if task_record:
            task_record.mark_failed(error_msg)

        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            return {
                'status': 'failed',
                'error': str(exc),
            }