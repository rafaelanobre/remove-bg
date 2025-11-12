import base64
import logging
import traceback
from io import BytesIO

from celery import shared_task
from celery.signals import task_failure, task_retry, task_success
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from PIL import Image
from rembg import new_session, remove

from processor.models import ProcessingTask

logger = logging.getLogger(__name__)

_rembg_session = new_session()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_image_task(self, image_data_b64: str, task_id: str) -> dict:
    """
    Removes background from uploaded image asynchronously.

    Uses base64 encoding because Celery JSON serializer doesn't support raw bytes.
    Task retries up to 3 times on failure with exponential backoff.
    """
    task_record = None
    extra = {'task_id': task_id, 'celery_task_id': self.request.id}

    try:
        logger.info('Starting image processing', extra=extra)

        task_record = ProcessingTask.objects.get(task_id=task_id)
        task_record.mark_processing()

        image_bytes = base64.b64decode(image_data_b64)
        input_image = Image.open(BytesIO(image_bytes))

        logger.info(
            'Image loaded successfully',
            extra={**extra, 'image_size': input_image.size, 'image_format': input_image.format}
        )

        output_image = remove(input_image, session=_rembg_session)

        output_buffer = BytesIO()
        output_image.save(output_buffer, format='PNG')
        output_buffer.seek(0)

        filename = f'processed/{task_id}.png'
        saved_path = default_storage.save(filename, ContentFile(output_buffer.read()))

        result_url = default_storage.url(saved_path)
        task_record.mark_completed(result_url)

        logger.info('Image processing completed', extra={**extra, 'result_url': result_url})

        return {
            'status': 'completed',
            'result_url': result_url,
        }

    except ProcessingTask.DoesNotExist:
        error_msg = f'ProcessingTask with task_id={task_id} not found'
        logger.error('ProcessingTask not found', extra={**extra, 'error': error_msg})
        return {
            'status': 'failed',
            'error': error_msg,
        }

    except Exception as exc:
        error_msg = f'{type(exc).__name__}: {exc!s}\n{traceback.format_exc()}'

        logger.error(
            'Image processing failed',
            extra={**extra, 'error_type': type(exc).__name__, 'error_message': str(exc)},
            exc_info=True
        )

        if task_record:
            task_record.mark_failed(error_msg)

        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            logger.error('Max retries exceeded', extra=extra, exc_info=True)
            return {
                'status': 'failed',
                'error': str(exc),
            }


@task_success.connect
def task_success_handler(sender=None, result=None, **kwargs):
    extra = {
        'task_id': kwargs.get('task_id'),
        'task_name': sender.name,
    }
    logger.info('Task succeeded', extra=extra)


@task_retry.connect
def task_retry_handler(sender=None, reason=None, **kwargs):
    extra = {
        'task_id': kwargs.get('task_id'),
        'task_name': sender.name,
        'retry_reason': str(reason),
        'retries': kwargs.get('retries', 0),
    }
    logger.warning('Task retrying', extra=extra)


@task_failure.connect
def task_failure_handler(sender=None, exception=None, **kwargs):
    extra = {
        'task_id': kwargs.get('task_id'),
        'task_name': sender.name,
        'exception_type': type(exception).__name__,
        'exception_message': str(exception),
        'traceback': kwargs.get('traceback'),
    }
    logger.error('Task failed', extra=extra, exc_info=exception)
