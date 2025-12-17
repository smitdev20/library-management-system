"""
Loans app models.
"""
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

class Loan(models.Model):
    """
    Tracks which user borrowed which book and when.
    Includes constraints for availability handling.
    """

    DEFAULT_LOAN_DAYS = 14

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='loans'
    )
    book = models.ForeignKey(
        'books.Book',
        on_delete=models.CASCADE,
        related_name='loans'
    )
    borrowed_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    returned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'loans'
        ordering = ['-borrowed_at']
        indexes = [
            models.Index(fields=['user', 'returned_at']),
            models.Index(fields=['book', 'returned_at']),
        ]

    def save(self, *args, **kwargs):
        # Set default due_date if not provided
        if not self.due_date:
            self.due_date = timezone.now() + timedelta(days=self.DEFAULT_LOAN_DAYS)
        super().save(*args, **kwargs)

    def clean(self):
        """Validate that the book is available for borrowing."""
        if not self.pk and self.book and not self.book.is_available:
            raise ValidationError('This book is not available for borrowing.')

    @property
    def is_active(self):
        """Check if loan is currently active (not returned)."""
        return self.returned_at is None

    @property
    def is_overdue(self):
        """Check if loan is overdue."""
        if self.returned_at:
            return False
        return timezone.now() > self.due_date

    def __str__(self):
        status = 'Active' if self.is_active else 'Returned'
        return f"{self.user.email} - {self.book.title} ({status})"
