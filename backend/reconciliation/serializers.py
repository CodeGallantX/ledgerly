from rest_framework import serializers
from .models import BankTransaction, ReconciliationLog

class BankTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankTransaction
        fields = '__all__'
        read_only_fields = ('school', 'matched')

class ReconciliationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReconciliationLog
        fields = '__all__'
        read_only_fields = ('school',)
