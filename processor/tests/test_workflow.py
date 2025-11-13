import io
import time

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from processor.models import ProcessingTask


@override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPAGATES=True)
class AsyncWorkflowIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_image = self._create_test_image()

    def _create_test_image(self):
        image = Image.new('RGB', (100, 100), color='red')
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        return SimpleUploadedFile(
            'test.png', buffer.getvalue(), content_type='image/png'
        )

    def test_complete_async_workflow(self):
        """Test complete workflow: upload → task creation → polling → result"""
        upload_response = self.client.post(reverse('home'), {'image': self.test_image})

        self.assertEqual(upload_response.status_code, 200)
        data = upload_response.json()
        self.assertIn('task_id', data)
        self.assertEqual(data['status'], 'pending')

        task_id = data['task_id']

        time.sleep(0.1)

        status_response = self.client.get(reverse('task_status', args=[task_id]))
        self.assertEqual(status_response.status_code, 200)

        status_data = status_response.json()
        self.assertEqual(status_data['status'], 'completed')
        self.assertIsNotNone(status_data['result_url'])
        self.assertFalse(status_data['error'])

        task = ProcessingTask.objects.get(task_id=task_id)
        self.assertEqual(task.status, 'completed')
        self.assertIsNotNone(task.result_url)
        self.assertIsNotNone(task.completed_at)

    def test_multiple_concurrent_uploads(self):
        """Test system handles multiple concurrent image uploads"""
        images = [self._create_test_image() for _ in range(3)]
        task_ids = []

        for img in images:
            response = self.client.post(reverse('home'), {'image': img})
            self.assertEqual(response.status_code, 200)
            task_ids.append(response.json()['task_id'])

        self.assertEqual(len(task_ids), 3)
        self.assertEqual(len(set(task_ids)), 3)

        time.sleep(0.2)

        for task_id in task_ids:
            task = ProcessingTask.objects.get(task_id=task_id)
            self.assertEqual(task.status, 'completed')


@override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPAGATES=True)
class ErrorHandlingIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_upload_without_file_returns_error(self):
        response = self.client.post(reverse('home'), {})

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

    def test_upload_invalid_file_type_returns_error(self):
        invalid_file = SimpleUploadedFile(
            'test.txt', b'not an image', content_type='text/plain'
        )
        response = self.client.post(reverse('home'), {'image': invalid_file})

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

    def test_upload_oversized_file_returns_error(self):
        large_image = Image.new('RGB', (5000, 5000), color='blue')
        buffer = io.BytesIO()
        large_image.save(buffer, format='PNG', quality=100)
        buffer.seek(0)

        large_file = SimpleUploadedFile(
            'large.png', buffer.getvalue(), content_type='image/png'
        )

        response = self.client.post(reverse('home'), {'image': large_file})

        if response.status_code == 400:
            self.assertIn('error', response.json())

    def test_status_check_for_nonexistent_task_returns_404(self):
        response = self.client.get(reverse('task_status', args=['invalid-uuid']))

        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json())


@override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPAGATES=True)
class TaskStatusPollingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_image = self._create_test_image()

    def _create_test_image(self):
        image = Image.new('RGB', (100, 100), color='yellow')
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        return SimpleUploadedFile(
            'test.png', buffer.getvalue(), content_type='image/png'
        )

    def test_frontend_polling_behavior(self):
        """Simulate frontend polling behavior"""
        upload_response = self.client.post(reverse('home'), {'image': self.test_image})
        task_id = upload_response.json()['task_id']

        max_polls = 30
        poll_interval = 0.1

        for _ in range(max_polls):
            response = self.client.get(reverse('task_status', args=[task_id]))
            self.assertEqual(response.status_code, 200)

            status = response.json()['status']

            if status == 'completed':
                break

            if status == 'failed':
                self.fail(f'Task failed: {response.json().get("error")}')

            time.sleep(poll_interval)

        task = ProcessingTask.objects.get(task_id=task_id)
        self.assertEqual(task.status, 'completed')
