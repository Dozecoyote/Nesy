from rest_framework import serializers
from .models import Transaction, Balance, Users, TypeTransaction

class BalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        fields = '__all__'


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeTransaction
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):

    type_id = TypeSerializer(read_only=True)
    type_id_id = serializers.PrimaryKeyRelatedField(
        queryset=TypeTransaction.objects.all(),
        source='type_id',
        write_only=True
    )

    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['id', 'date']