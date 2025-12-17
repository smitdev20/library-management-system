"""
Reviews app models.
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    """User reviews for books."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    book = models.ForeignKey(
        'books.Book',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reviews'
        unique_together = ['user', 'book']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.book.title} ({self.rating}/5)"
