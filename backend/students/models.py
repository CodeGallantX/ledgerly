import uuid
from django.db import models

class Parent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('accounts.School', on_delete=models.CASCADE, related_name='parents')
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name

class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('accounts.School', on_delete=models.CASCADE, related_name='students')
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='students')
    class_room = models.ForeignKey('academics.ClassRoom', on_delete=models.CASCADE, related_name='students')
    admission_number = models.CharField(max_length=50) # Unique per school handled in Meta
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['school', 'admission_number'], name='unique_school_admission_number')
        ]
        indexes = [
            models.Index(fields=['admission_number']),
        ]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.full_name} ({self.admission_number})"
