from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, DecimalField, Sum
from django.db.models.functions import Coalesce
from django.utils.timezone import now
from rest_framework import serializers

from .models import Account, Transaction


class AccountSerializer(serializers.ModelSerializer):
    transaction_count_last_thirty_days = serializers.SerializerMethodField()
    balance_change_last_thirty_days = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ['id', 'user', 'name', 'transaction_count_last_thirty_days', 'balance_change_last_thirty_days']

    def get_transaction_count_last_thirty_days(self, obj):
        thirty_days_ago = now() - timedelta(days=30)
        return Transaction.objects.filter(account=obj, timestamp__gte=thirty_days_ago).count()

    def get_balance_change_last_thirty_days(self, obj):
        thirty_days_ago = now() - timedelta(days=30)
        # total = Transaction.objects.filter(account=obj, timestamp__gte=thirty_days_ago)\
        #     .aggregate(total=Coalesce(Sum('amount'), 0, output_field=DecimalField()))['total']
        # return str(total)
        total = Transaction.objects.filter(account=obj, timestamp__gte=thirty_days_ago)\
            .aggregate(total=Coalesce(Sum('amount'), Decimal('0.00')))['total']
        return "{:.2f}".format(total)

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'account', 'timestamp', 'amount', 'description', 'transaction_category']
