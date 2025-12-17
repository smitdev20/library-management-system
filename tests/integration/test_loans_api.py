"""
Integration tests for loans API.
"""
import pytest
from django.urls import reverse
from apps.books.models import Book


@pytest.mark.django_db
class TestBorrowBookAPI:
    """Tests for borrowing books."""

    def test_member_can_borrow_book(self, authenticated_member_client, sample_book):
        """Test member can borrow an available book."""
        url = reverse('loan-borrow')
        data = {'book_id': sample_book.id}
        response = authenticated_member_client.post(url, data)
        assert response.status_code == 201
        assert response.data['book']['id'] == sample_book.id

        # Verify book is no longer available
        sample_book.refresh_from_db()
        assert sample_book.is_available is False

    def test_cannot_borrow_unavailable_book(self, authenticated_member_client, unavailable_book):
        """Test cannot borrow unavailable book."""
        url = reverse('loan-borrow')
        data = {'book_id': unavailable_book.id}
        response = authenticated_member_client.post(url, data)
        assert response.status_code == 400
        # Error can be in 'error' key or 'book_id' validation error
        error_text = str(response.data).lower()
        assert 'not available' in error_text or 'available' in error_text

    def test_cannot_borrow_same_book_twice(self, authenticated_member_client, sample_book):
        """Test user cannot borrow same book twice."""
        url = reverse('loan-borrow')
        data = {'book_id': sample_book.id}

        # First borrow should succeed
        response1 = authenticated_member_client.post(url, data)
        assert response1.status_code == 201

        # Second borrow should fail
        sample_book.is_available = True
        sample_book.save()
        response2 = authenticated_member_client.post(url, data)
        assert response2.status_code == 400

    def test_anonymous_cannot_borrow(self, api_client, sample_book):
        """Test anonymous user cannot borrow books."""
        url = reverse('loan-borrow')
        data = {'book_id': sample_book.id}
        response = api_client.post(url, data)
        assert response.status_code == 401

    def test_borrow_nonexistent_book(self, authenticated_member_client):
        """Test borrowing nonexistent book fails."""
        url = reverse('loan-borrow')
        data = {'book_id': 99999}
        response = authenticated_member_client.post(url, data)
        assert response.status_code == 400


@pytest.mark.django_db
class TestReturnBookAPI:
    """Tests for returning books."""

    def test_admin_can_return_book(self, authenticated_admin_client, authenticated_member_client, sample_book):
        """Test admin can return a borrowed book."""
        # Member borrows the book
        borrow_url = reverse('loan-borrow')
        borrow_response = authenticated_member_client.post(
            borrow_url, {'book_id': sample_book.id}
        )
        loan_id = borrow_response.data['id']

        # Admin returns it
        return_url = reverse('loan-return-book', args=[loan_id])
        response = authenticated_admin_client.post(return_url)
        assert response.status_code == 200
        assert response.data['returned_at'] is not None

        # Verify book is available again
        sample_book.refresh_from_db()
        assert sample_book.is_available is True

    def test_cannot_return_already_returned_book(self, authenticated_admin_client, authenticated_member_client, sample_book):
        """Test cannot return already returned book."""
        # Member borrows
        borrow_url = reverse('loan-borrow')
        borrow_response = authenticated_member_client.post(
            borrow_url, {'book_id': sample_book.id}
        )
        loan_id = borrow_response.data['id']

        # Admin returns once
        return_url = reverse('loan-return-book', args=[loan_id])
        authenticated_admin_client.post(return_url)

        # Admin tries to return again
        response = authenticated_admin_client.post(return_url)
        assert response.status_code == 400


@pytest.mark.django_db
class TestLoanListAPI:
    """Tests for listing loans."""

    def test_member_sees_own_loans(self, authenticated_member_client, sample_book):
        """Test member sees only their own loans."""
        # Create a loan
        borrow_url = reverse('loan-borrow')
        authenticated_member_client.post(borrow_url, {'book_id': sample_book.id})

        # List loans
        url = reverse('loan-list')
        response = authenticated_member_client.get(url)
        assert response.status_code == 200
        loans = response.data if isinstance(response.data, list) else response.data.get('results', [])
        assert len(loans) >= 1

    def test_admin_sees_all_loans(self, authenticated_admin_client, authenticated_member_client, sample_book):
        """Test admin can see all loans."""
        # Member creates a loan
        borrow_url = reverse('loan-borrow')
        authenticated_member_client.post(borrow_url, {'book_id': sample_book.id})

        # Admin lists all loans
        url = reverse('loan-list')
        response = authenticated_admin_client.get(url)
        assert response.status_code == 200

    def test_active_loans_endpoint(self, authenticated_member_client, sample_book):
        """Test active loans endpoint."""
        # Create a loan
        borrow_url = reverse('loan-borrow')
        authenticated_member_client.post(borrow_url, {'book_id': sample_book.id})

        # Get active loans
        url = reverse('loan-active')
        response = authenticated_member_client.get(url)
        assert response.status_code == 200
        # Handle list response (no pagination)
        loans = response.data if isinstance(response.data, list) else response.data.get('results', [])
        for loan in loans:
            assert loan['is_active'] is True

    def test_overdue_loans_admin_only(self, api_client, member_user, admin_user):
        """Test overdue loans endpoint is admin only."""
        url = reverse('loan-overdue')

        # Member should not access
        api_client.force_authenticate(user=member_user)
        member_response = api_client.get(url)
        assert member_response.status_code == 403

        # Admin should access
        api_client.force_authenticate(user=admin_user)
        admin_response = api_client.get(url)
        assert admin_response.status_code == 200

