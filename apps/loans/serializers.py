"""
Loans app serializers.
"""
from rest_framework import serializers
from .models import Loan
from apps.books.serializers import BookListSerializer
from apps.books.models import Book


class LoanSerializer(serializers.ModelSerializer):
    """Serializer for Loan model with computed fields."""

    book = BookListSerializer(read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Loan
        fields = [
            'id', 'user_email', 'book', 'borrowed_at',
            'due_date', 'returned_at', 'is_active', 'is_overdue'
        ]
        read_only_fields = ['id', 'borrowed_at', 'returned_at']


class LoanDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single loan view."""

    book = BookListSerializer(read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Loan
        fields = [
            'id', 'user_email', 'user_username', 'book', 'borrowed_at',
            'due_date', 'returned_at', 'is_active', 'is_overdue'
        ]


class BorrowBookSerializer(serializers.Serializer):
    """Serializer for borrowing a book."""

    book_id = serializers.IntegerField()

    def validate_book_id(self, value):
        try:
            book = Book.objects.get(pk=value)
        except Book.DoesNotExist:
            raise serializers.ValidationError('Book not found.')

        if not book.is_available:
            raise serializers.ValidationError('Book is not available for borrowing.')

        return value


class EmptySerializer(serializers.Serializer):
    """Empty serializer for endpoints that don't need a request body."""
    pass
