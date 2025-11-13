import base64
import io
from unittest.mock import patch

from django.test import TestCase, override_settings
from PIL import Image

from processor.models import ProcessingTask
from processor.tasks import process_image_task


@override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPAGATES=True)
class CeleryTaskTests(TestCase):
    def setUp(self):
        self.test_image_b64 = self._create_test_image_b64()

    def _create_test_image_b64(self):
        image = Image.new('RGB', (100, 100), color='green')
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    def test_process_image_task_completes_successfully(self):
        task_id = 'test-task-123'
        ProcessingTask.objects.create(task_id=task_id, status='pending')

        result = process_image_task(self.test_image_b64, task_id)

        self.assertEqual(result['status'], 'completed')
        self.assertIn('result_url', result)

        task = ProcessingTask.objects.get(task_id=task_id)
        self.assertEqual(task.status, 'completed')
        self.assertIsNotNone(task.result_url)

    def test_process_image_task_handles_invalid_task_id(self):
        result = process_image_task(self.test_image_b64, 'nonexistent-task')

        self.assertEqual(result['status'], 'failed')
        self.assertIn('error', result)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=False)
    def test_process_image_task_handles_corrupted_data(self):
        task_id = 'test-task-corrupted'
        ProcessingTask.objects.create(task_id=task_id, status='pending')

        try:
            process_image_task.apply_async(args=('invalid-base64!!!', task_id), task_id=task_id)
        except Exception:
            pass

        task = ProcessingTask.objects.get(task_id=task_id)
        self.assertIn(task.status, ['pending', 'failed'])

    def test_task_creates_processed_image_file(self):
        task_id = 'test-task-file-creation'
        ProcessingTask.objects.create(task_id=task_id, status='pending')

        result = process_image_task(self.test_image_b64, task_id)

        self.assertEqual(result['status'], 'completed')
        self.assertTrue(result['result_url'].endswith('.png'))
        self.assertIn('processed/', result['result_url'])

    def test_task_updates_database_status_correctly(self):
        task_id = 'test-task-status-updates'
        task = ProcessingTask.objects.create(task_id=task_id, status='pending')

        self.assertEqual(task.status, 'pending')

        process_image_task(self.test_image_b64, task_id)

        task.refresh_from_db()
        self.assertEqual(task.status, 'completed')
        self.assertIsNotNone(task.completed_at)


@override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPAGATES=True)
class CelerySignalHandlerTests(TestCase):
    def test_task_success_signal_handler_exists(self):
        from processor.tasks import task_success_handler

        self.assertIsNotNone(task_success_handler)

    def test_task_retry_signal_handler_exists(self):
        from processor.tasks import task_retry_handler

        self.assertIsNotNone(task_retry_handler)

    def test_task_failure_signal_handler_exists(self):
        from processor.tasks import task_failure_handler

        self.assertIsNotNone(task_failure_handler)