from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions
from rest_framework.pagination import CursorPagination

from .models import Account, Transaction
from .serializers import AccountSerializer, TransactionSerializer


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to see it unless the user is an admin.
    """
    def has_object_permission(self, request, view, obj):
        # if request.user.is_staff:
        #     return True
        # return obj.user == request.user
        # Check if the user is an admin
        if request.user.is_staff:
            return True

        # Handle the case where the object is a Transaction
        if isinstance(obj, Transaction):
            obj = obj.account  # Get the related Account object for the Transaction

        # Now obj is guaranteed to be an Account, so we can check the user attribute
        return obj.user == request.user

class AccountList(generics.ListAPIView):
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    pagination_class = CursorPagination

    def get_queryset(self):
        if self.request.user.is_staff:
            return Account.objects.all()
        return Account.objects.filter(user=self.request.user)

class AccountDetail(generics.RetrieveAPIView):
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Account.objects.all()
        return Account.objects.filter(user=self.request.user)

class TransactionList(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    pagination_class = CursorPagination

    filter_backends = [DjangoFilterBackend]

    filterset_fields = ['timestamp', 'account', 'transaction_category']

    def get_queryset(self):
        queryset = Transaction.objects.order_by('-timestamp')
        if not self.request.user.is_staff:
            queryset = queryset.filter(account__user=self.request.user)
        return queryset

class TransactionDetail(generics.RetrieveAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Transaction.objects.all()
        return Transaction.objects.filter(account__user=self.request.user)
