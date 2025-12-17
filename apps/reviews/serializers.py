"""
Reviews app serializers - Simple and clean.
"""
from rest_framework import serializers
from .models import Review
from apps.books.models import Book


class ReviewSerializer(serializers.ModelSerializer):
    """Review output serializer."""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user_email', 'book', 'book_title', 'rating', 'text', 'created_at']
        read_only_fields = ['id', 'user_email', 'book_title', 'created_at']


class ReviewCreateSerializer(serializers.Serializer):
    """Simple review create serializer - just book_id, rating, text."""
    book_id = serializers.IntegerField(help_text="ID of the book to review")
    rating = serializers.IntegerField(min_value=1, max_value=5, help_text="Rating 1-5")
    text = serializers.CharField(required=False, allow_blank=True, help_text="Review text (optional)")

    def validate_book_id(self, value):
        """Ensure book exists."""
        if not Book.objects.filter(pk=value).exists():
            raise serializers.ValidationError('Book not found.')
        return value

    def validate(self, attrs):
        """Ensure user hasn't already reviewed this book."""
        request = self.context.get('request')
        if request and request.user:
            if Review.objects.filter(user=request.user, book_id=attrs['book_id']).exists():
                raise serializers.ValidationError({'book_id': 'You have already reviewed this book.'})
        return attrs

    def create(self, validated_data):
        """Create review with current user."""
        book = Book.objects.get(pk=validated_data['book_id'])
        return Review.objects.create(
            user=self.context['request'].user,
            book=book,
            rating=validated_data['rating'],
            text=validated_data.get('text', '')
        )


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """Update review - only rating and text."""
    class Meta:
        model = Review
        fields = ['rating', 'text']
