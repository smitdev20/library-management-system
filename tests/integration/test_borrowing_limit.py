import pytest
from django.urls import reverse
from apps.books.models import Book

@pytest.mark.django_db
class TestBorrowingLimit:
    """Test the 1-book borrowing limit per user."""

    def test_cannot_borrow_more_than_one_book(self, authenticated_member_client, authenticated_admin_client, sample_book):
        """
        Verify that a user cannot borrow a second book while having an active loan.
        """
        # Create a second book
        second_book = Book.objects.create(
            title="Second Book",
            author="Author Two",
            isbn="9876543210123",
            page_count=200,
            is_available=True
        )

        borrow_url = reverse('loan-borrow')

        # 1. Borrow first book (Should Succeed)
        response1 = authenticated_member_client.post(borrow_url, {'book_id': sample_book.id})
        assert response1.status_code == 201, "First borrow should succeed"

        # 2. Try to borrow second book (Should Fail)
        response2 = authenticated_member_client.post(borrow_url, {'book_id': second_book.id})
        assert response2.status_code == 400, "Second borrow should fail due to limit"
        assert "only borrow 1 book" in str(response2.data['error'])

        # 3. Return first book (Using Admin client)
        loan_id = response1.data['id']
        return_url = reverse('loan-return-book', args=[loan_id])
        
        return_response = authenticated_admin_client.post(return_url)
        assert return_response.status_code == 200, "Admin should be able to return book"

        # 4. Borrow second book again (Should Succeed now)
        response3 = authenticated_member_client.post(borrow_url, {'book_id': second_book.id})
        assert response3.status_code == 201, "After returning, borrowing should ensure success"
