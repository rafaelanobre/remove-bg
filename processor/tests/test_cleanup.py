from datetime import timedelta

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from processor.models import ProcessingTask


class TaskCleanupCommandTests(TestCase):
    def setUp(self):
        self.old_completed_task = ProcessingTask.objects.create(
            task_id='old-completed-task',
            status='completed',
            result_url='/media/processed/old-completed-task.png',
        )
        self.old_completed_task.created_at = timezone.now() - timedelta(hours=25)
        self.old_completed_task.completed_at = timezone.now() - timedelta(hours=25)
        self.old_completed_task.save()

        self.old_failed_task = ProcessingTask.objects.create(
            task_id='old-failed-task',
            status='failed',
            error_message='Test error',
        )
        self.old_failed_task.created_at = timezone.now() - timedelta(hours=25)
        self.old_failed_task.save()

        self.recent_task = ProcessingTask.objects.create(
            task_id='recent-task', status='completed', result_url='/media/test.png'
        )

    def test_cleanup_command_exists(self):
        try:
            call_command('cleanup_old_tasks', '--dry-run', '--hours=1')
        except Exception as e:
            self.fail(f'cleanup_old_tasks command failed: {e}')

    def test_cleanup_dry_run_does_not_delete(self):
        initial_count = ProcessingTask.objects.count()

        call_command('cleanup_old_tasks', '--dry-run', '--hours=24')

        self.assertEqual(ProcessingTask.objects.count(), initial_count)

    def test_cleanup_deletes_old_tasks(self):
        self.assertEqual(ProcessingTask.objects.count(), 3)

        call_command('cleanup_old_tasks', '--hours=24')

        self.assertEqual(ProcessingTask.objects.count(), 1)
        self.assertTrue(ProcessingTask.objects.filter(task_id='recent-task').exists())
        self.assertFalse(
            ProcessingTask.objects.filter(task_id='old-completed-task').exists()
        )
        self.assertFalse(
            ProcessingTask.objects.filter(task_id='old-failed-task').exists()
        )

    def test_cleanup_respects_custom_hours(self):
        call_command('cleanup_old_tasks', '--hours=48')

        self.assertEqual(ProcessingTask.objects.count(), 3)

    def test_cleanup_handles_no_old_tasks(self):
        ProcessingTask.objects.filter(
            task_id__in=['old-completed-task', 'old-failed-task']
        ).delete()

        try:
            call_command('cleanup_old_tasks', '--hours=24')
        except Exception as e:
            self.fail(f'cleanup_old_tasks failed with no old tasks: {e}')

        self.assertEqual(ProcessingTask.objects.count(), 1)
