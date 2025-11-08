import os
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from processor.models import ProcessingTask


class Command(BaseCommand):
    help = 'Delete old processing tasks and their associated files (older than 1 hour)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=1,
            help='Delete tasks older than this many hours (default: 1)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        hours = options['hours']
        dry_run = options['dry_run']

        cutoff_time = timezone.now() - timedelta(hours=hours)

        old_tasks = ProcessingTask.objects.filter(created_at__lt=cutoff_time)
        task_count = old_tasks.count()

        if task_count == 0:
            self.stdout.write(
                self.style.SUCCESS(f'No tasks older than {hours} hour(s) found.')
            )
            return

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'[DRY RUN] Would delete {task_count} task(s) older than {hours} hour(s)'
                )
            )
            for task in old_tasks[:10]:
                self.stdout.write(f'  - {task.task_id[:8]} ({task.status})')
            if task_count > 10:
                self.stdout.write(f'  ... and {task_count - 10} more')
            return

        files_deleted = 0
        files_not_found = 0

        for task in old_tasks:
            if task.result_url:
                file_path = os.path.join(
                    settings.MEDIA_ROOT,
                    task.result_url.replace(settings.MEDIA_URL, '', 1)
                )

                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        files_deleted += 1
                    except OSError as e:
                        self.stdout.write(
                            self.style.ERROR(f'Error deleting {file_path}: {e}')
                        )
                else:
                    files_not_found += 1

        old_tasks.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully deleted {task_count} task(s) and {files_deleted} file(s)'
            )
        )

        if files_not_found > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'{files_not_found} file(s) were already missing'
                )
            )