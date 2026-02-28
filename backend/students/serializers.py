from rest_framework import serializers
from .models import Student, Parent

class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parent
        fields = '__all__'
        read_only_fields = ('school',)

class StudentSerializer(serializers.ModelSerializer):
    # Using the annotated field for performance
    outstanding_balance = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        source='annotated_outstanding_balance',
        read_only=True
    )

    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ('school',)
