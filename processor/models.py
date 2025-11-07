from django.db import models
from django.utils import timezone


class ProcessingTask(models.Model):
    """
    Tracks background image processing tasks.
    Provides persistent state storage beyond Celery's TTL-limited result backend.
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    task_id = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="Celery task UUID"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
    )
    result_url = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="URL or path to processed image"
    )
    error_message = models.TextField(
        null=True,
        blank=True,
        help_text="Exception traceback if task failed"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When task finished (success or failure)"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"Task {self.task_id[:8]} - {self.status}"

    def mark_processing(self):
        self.status = 'processing'
        self.save(update_fields=['status'])

    def mark_completed(self, result_url):
        self.status = 'completed'
        self.result_url = result_url
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'result_url', 'completed_at'])

    def mark_failed(self, error_message):
        self.status = 'failed'
        self.error_message = error_message
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'error_message', 'completed_at'])
