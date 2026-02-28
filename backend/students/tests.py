from django.test import TestCase
from accounts.models import School, User
from academics.models import ClassRoom
from .models import Student, Parent
from .serializers import StudentSerializer

class MultiTenancyTest(TestCase):
    def setUp(self):
        self.school1 = School.objects.create(name="School 1", slug="school-1")
        self.school2 = School.objects.create(name="School 2", slug="school-2")

        self.class1 = ClassRoom.objects.create(school=self.school1, name="Class 1")
        self.class2 = ClassRoom.objects.create(school=self.school2, name="Class 2")

        self.parent1 = Parent.objects.create(school=self.school1, full_name="Parent 1")
        self.parent2 = Parent.objects.create(school=self.school2, full_name="Parent 2")

    def test_student_isolation(self):
        Student.objects.create(
            school=self.school1,
            parent=self.parent1,
            class_room=self.class1,
            admission_number="001",
            first_name="John",
            last_name="Doe"
        )

        Student.objects.create(
            school=self.school2,
            parent=self.parent2,
            class_room=self.class2,
            admission_number="001", # Same admission number but different school
            first_name="Jane",
            last_name="Smith"
        )

        self.assertEqual(Student.objects.filter(school=self.school1).count(), 1)
        self.assertEqual(Student.objects.filter(school=self.school2).count(), 1)

    def test_serializer_annotated_field(self):
        s = Student.objects.create(
            school=self.school1,
            parent=self.parent1,
            class_room=self.class1,
            admission_number="003",
            first_name="Bob",
            last_name="The Builder"
        )
        # Mocking what the ViewSet's get_queryset would do.
        # Serializer now requires this annotated field.
        s.annotated_outstanding_balance = 100.00
        serializer = StudentSerializer(s)
        self.assertEqual(float(serializer.data['outstanding_balance']), 100.00)
