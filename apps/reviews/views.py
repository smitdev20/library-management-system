"""
Reviews app views - Simple review endpoints.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import Avg, Count
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Review
from .serializers import ReviewSerializer, ReviewCreateSerializer, ReviewUpdateSerializer
from apps.accounts.permissions import IsOwnerOrAdministrator


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Book Reviews API
    
    Public: View reviews
    Members: Create reviews  
    Owner/Admin: Update/Delete reviews
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    filter_backends = []  # Disable auto-generated filters
    pagination_class = None  # Simple list

    def get_queryset(self):
        queryset = Review.objects.select_related('user', 'book').order_by('-created_at')
        book_id = self.request.query_params.get('book_id')
        if book_id:
            queryset = queryset.filter(book_id=book_id)
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        if self.action in ['update', 'partial_update']:
            return ReviewUpdateSerializer
        return ReviewSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsOwnerOrAdministrator()]
        return super().get_permissions()

    @swagger_auto_schema(
        operation_summary="List all reviews",
        operation_description="Get all reviews. Filter by book with ?book_id=123",
        manual_parameters=[
            openapi.Parameter('book_id', openapi.IN_QUERY, description="Filter by book ID", type=openapi.TYPE_INTEGER, required=False)
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a review",
        operation_description="Add a review for a book (1 review per book)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['book_id', 'rating'],
            properties={
                'book_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Book ID'),
                'rating': openapi.Schema(type=openapi.TYPE_INTEGER, description='Rating 1-5'),
                'text': openapi.Schema(type=openapi.TYPE_STRING, description='Review text (optional)')
            }
        ),
        responses={201: ReviewSerializer}
    )
    def create(self, request, *args, **kwargs):
        serializer = ReviewCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        review = serializer.save()
        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(operation_summary="Get review details")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update review",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'rating': openapi.Schema(type=openapi.TYPE_INTEGER, description='Rating 1-5'),
                'text': openapi.Schema(type=openapi.TYPE_STRING, description='Review text')
            }
        )
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Delete review")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="My reviews")
    @action(detail=False, methods=['get'])
    def my_reviews(self, request):
        """Get current user's reviews."""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)
        queryset = Review.objects.filter(user=request.user).select_related('book').order_by('-created_at')
        serializer = ReviewSerializer(queryset, many=True)
        return Response(serializer.data)
