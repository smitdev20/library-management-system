"""
Unit tests for models.
"""
import pytest
from django.utils import timezone
from datetime import timedelta
from apps.accounts.models import User
from apps.books.models import Book
from apps.loans.models import Loan
from apps.reviews.models import Review


@pytest.mark.django_db
class TestUserModel:
    """Tests for the User model."""

    def test_user_creation(self, member_group):
        """Test user can be created successfully."""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!'
        )
        assert user.email == 'test@example.com'
        assert user.username == 'testuser'
        assert user.check_password('TestPass123!')
        assert user.is_active is True

    def test_user_str(self, member_user):
        """Test user string representation."""
        assert str(member_user) == 'member@library.com'

    def test_is_administrator_property(self, admin_user, member_user):
        """Test is_administrator property."""
        assert admin_user.is_administrator is True
        assert member_user.is_administrator is False

    def test_is_member_property(self, admin_user, member_user):
        """Test is_member property."""
        assert member_user.is_member is True
        # Note: admin_user may also be in Members group due to auto-assignment signal


@pytest.mark.django_db
class TestBookModel:
    """Tests for the Book model."""

    def test_book_creation(self):
        """Test book can be created successfully."""
        book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='1234567890123'
        )
        assert book.title == 'Test Book'
        assert book.is_available is True

    def test_book_str(self, sample_book):
        """Test book string representation."""
        assert str(sample_book) == 'The Great Gatsby by F. Scott Fitzgerald'

    def test_book_default_availability(self):
        """Test book is available by default."""
        book = Book.objects.create(
            title='New Book',
            author='Author',
            isbn='9876543210987'
        )
        assert book.is_available is True


@pytest.mark.django_db
class TestLoanModel:
    """Tests for the Loan model."""

    def test_loan_creation(self, member_user, sample_book):
        """Test loan can be created successfully."""
        loan = Loan.objects.create(
            user=member_user,
            book=sample_book
        )
        assert loan.user == member_user
        assert loan.book == sample_book
        assert loan.returned_at is None

    def test_loan_default_due_date(self, member_user, sample_book):
        """Test loan sets default due date."""
        loan = Loan.objects.create(
            user=member_user,
            book=sample_book
        )
        expected_due = timezone.now() + timedelta(days=14)
        # Allow 1 minute tolerance
        assert abs((loan.due_date - expected_due).total_seconds()) < 60

    def test_loan_is_active_property(self, member_user, sample_book):
        """Test is_active property."""
        loan = Loan.objects.create(
            user=member_user,
            book=sample_book
        )
        assert loan.is_active is True

        loan.returned_at = timezone.now()
        loan.save()
        assert loan.is_active is False

    def test_loan_is_overdue_property(self, member_user, sample_book):
        """Test is_overdue property."""
        loan = Loan.objects.create(
            user=member_user,
            book=sample_book,
            due_date=timezone.now() - timedelta(days=1)  # Due yesterday
        )
        assert loan.is_overdue is True

        loan.returned_at = timezone.now()
        loan.save()
        assert loan.is_overdue is False

    def test_loan_str(self, member_user, sample_book):
        """Test loan string representation."""
        loan = Loan.objects.create(
            user=member_user,
            book=sample_book
        )
        assert 'Active' in str(loan)

        loan.returned_at = timezone.now()
        loan.save()
        assert 'Returned' in str(loan)


@pytest.mark.django_db
class TestReviewModel:
    """Tests for the Review model."""

    def test_review_creation(self, member_user, sample_book):
        """Test review can be created successfully."""
        review = Review.objects.create(
            user=member_user,
            book=sample_book,
            rating=5,
            text='Great book!'
        )
        assert review.rating == 5
        assert review.text == 'Great book!'

    def test_review_str(self, member_user, sample_book):
        """Test review string representation."""
        review = Review.objects.create(
            user=member_user,
            book=sample_book,
            rating=4,
            text='Good read'
        )
        assert '4/5' in str(review)

    def test_review_unique_constraint(self, member_user, sample_book):
        """Test user can only review a book once."""
        Review.objects.create(
            user=member_user,
            book=sample_book,
            rating=5,
            text='First review'
        )
        with pytest.raises(Exception):  # IntegrityError
            Review.objects.create(
                user=member_user,
                book=sample_book,
                rating=3,
                text='Second review'
            )
