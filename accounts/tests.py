import logging

from django.contrib.auth import get_user_model
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Account, Transaction

logger = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.INFO)
class TestAccountsApiAsStaff(APITestCase):

    # this line loads the fixture data with sample users, accounts and transactions
    fixtures = ["sample.json"]

    def setUp(self):
        super().setUp()
        # this user exists in the fixtures
        admin_user = get_user_model().objects.get(username="test-admin")
        self.client.force_authenticate(admin_user)

    def test_accounts_list(self):
        response = self.client.get("/accounts/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert len(response.json()) > 0
    # the freeze_time annotation ensures that the test always runs as if stuck at a
    # specific point in time, so assertions about the transaction_count_last_thirty_days
    # and balance_change_last_thirty_days fields will work predictably.
   
    @freeze_time("2022-06-14 18:00:00")
    def test_retrieve_account(self):
        response = self.client.get("/accounts/1/")

        assert response.status_code == status.HTTP_200_OK

        assert response.json() == {
            "id": 1,
            "user": 2,
            "name": "John Smith",
            "transaction_count_last_thirty_days": 119,
            "balance_change_last_thirty_days": "-1304.67",
        }

    @freeze_time("2022-06-14 18:00:00")
    def test_accounts_list_as_normal_user(self):
        user1 = get_user_model().objects.get(username="user1")
        self.client.force_authenticate(user1)
        response = self.client.get("/accounts/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_response = response.json()  # Parse JSON response
        logger.info(f"Response: {json_response}")
        logger.info(f'User Details: {user1.id}')
        self.assertTrue(all(account['user'] == user1.id for account in json_response)) 
        
    @freeze_time("2022-06-14 18:00:00")
    def test_retrieve_account_unauthorized(self):
        # Try to access an account not belonging to the authenticated user
        user2 = get_user_model().objects.get(username="user2")
        self.client.force_authenticate(user2)

        response = self.client.get("/accounts/1/")  # Assuming Account 1 does not belong to user2

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
class TestTransactionsApi(APITestCase):
    fixtures = ["sample.json"]

    def setUp(self):
        super().setUp()
        self.user1 = get_user_model().objects.get(username="user1")
        self.client.force_authenticate(self.user1)

    def test_transactions_list(self):
        response = self.client.get("/transactions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_response = response.json()  # Parse JSON response
        self.assertGreater(len(json_response), 0)

    @freeze_time("2022-06-14 18:00:00")
    def test_transactions_filter_by_account(self):
        response = self.client.get("/transactions/", {'account': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_response = response.json()  # Parse JSON response
        self.assertTrue(all(transaction['account'] == 1 for transaction in json_response))
    
    
    def test_retrieve_transaction_unauthorized(self):
        # Create a new user and attempt to access a transaction not belonging to them
        user2 = get_user_model().objects.get(username="user2")
        self.client.force_authenticate(user2)

        # Assuming Transaction 1 does not belong to user2
        response = self.client.get("/transactions/1/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
