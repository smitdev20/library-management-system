"""
Loans app views - Clean and simple borrowing endpoints.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema, no_body
from drf_yasg import openapi
from .models import Loan
from .serializers import LoanSerializer, LoanDetailSerializer, BorrowBookSerializer, EmptySerializer
from apps.books.models import Book
from apps.accounts.permissions import IsAdministrator, IsOwnerOrAdministrator


class LoanViewSet(viewsets.ModelViewSet):
    """
    Borrowing Management API
    
    Members: Borrow books, view own loans, return books
    Admin: View all loans, manage overdue
    """
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post']
    filter_backends = []  # Disable all filters to clean up Swagger
    pagination_class = None  # Simple list without pagination for loans

    def get_queryset(self):
        """Members see only their loans. Admins see all."""
        user = self.request.user
        queryset = Loan.objects.select_related('user', 'book')
        
        if getattr(self, 'swagger_fake_view', False):
            return Loan.objects.none()
        
        if user.groups.filter(name='Administrators').exists():
            return queryset.order_by('-borrowed_at')
        return queryset.filter(user=user).order_by('-borrowed_at')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return LoanDetailSerializer
        return LoanSerializer

    @swagger_auto_schema(
        operation_summary="List loans (Admin: all, Members: own)",
        operation_description="""**Administrators**: View all loans in the system  
**Members**: View only your own loans
        """,
        responses={200: LoanSerializer(many=True)},
        manual_parameters=[]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get loan details",
        operation_description="Get details of a specific loan by ID"
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Borrow a book",
        operation_description="Borrow a book by its ID",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['book_id'],
            properties={
                'book_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the book to borrow')
            }
        ),
        responses={
            201: LoanSerializer,
            400: "Book not available or already borrowed"
        }
    )
    @action(detail=False, methods=['post'])
    def borrow(self, request):
        """Borrow a book by ID."""
        serializer = BorrowBookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        book_id = serializer.validated_data['book_id']

        with transaction.atomic():
            try:
                book = Book.objects.select_for_update().get(pk=book_id)
            except Book.DoesNotExist:
                return Response({'error': 'Book not found.'}, status=status.HTTP_404_NOT_FOUND)

            if not book.is_available:
                return Response({'error': 'Book is not available.'}, status=status.HTTP_400_BAD_REQUEST)

            if Loan.objects.filter(user=request.user, book=book, returned_at__isnull=True).exists():
                return Response({'error': 'You already have this book.'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if user has ANY active loan (limit 1 book at a time)
            if Loan.objects.filter(user=request.user, returned_at__isnull=True).exists():
                return Response({'error': 'You can only borrow 1 book at a time.'}, status=status.HTTP_400_BAD_REQUEST)

            loan = Loan.objects.create(user=request.user, book=book)
            book.is_available = False
            book.save()

        return Response(LoanSerializer(loan).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="Verify book return",
        operation_description="Process a book return by loan ID. Requires administrator verification.",
        request_body=no_body,
        responses={
            200: LoanSerializer,
            400: "Book already returned",
            404: "Loan not found"
        }
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAdministrator])
    def return_book(self, request, pk=None):
        """Return a borrowed book by loan ID (Admin only)."""
        loan = self.get_object()

        if loan.returned_at:
            return Response({'error': 'Book already returned.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            loan.returned_at = timezone.now()
            loan.save()
            loan.book.is_available = True
            loan.book.save()

        return Response(LoanSerializer(loan).data)

    @swagger_auto_schema(
        operation_summary="My active loans (with loan IDs)",
        operation_description="""Get your currently active (unreturned) loans.
        
**The 'id' field in each loan is the LOAN ID** - use this ID to return books!
        """
    )
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active loans with loan IDs for returning books."""
        queryset = self.get_queryset().filter(returned_at__isnull=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="All loans (Admin only)",
        operation_description="View all loans in the system across all users - requires administrator access"
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAdministrator])
    def all_loans(self, request):
        """Get all loans in the system (Admin only)."""
        queryset = Loan.objects.select_related('user', 'book').order_by('-borrowed_at')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Overdue loans (Admin only)",
        operation_description="Get all overdue loans - requires admin access"
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAdministrator])
    def overdue(self, request):
        """Get overdue loans (Admin only)."""
        queryset = Loan.objects.filter(
            returned_at__isnull=True,
            due_date__lt=timezone.now()
        ).select_related('user', 'book').order_by('-due_date')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="My loans (all history)",
        operation_description="Get all your loans including returned"
    )
    @action(detail=False, methods=['get'])
    def my_loans(self, request):
        """Get current user's all loans."""
        queryset = Loan.objects.filter(user=request.user).select_related('book').order_by('-borrowed_at')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
