from django.test import TestCase
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Earning, Expense, PersonalDetails, FinancialYear
from django.core.exceptions import ValidationError
from decimal import Decimal


class ModelTests(TestCase):
    def setUp(self):
        self.financial_year = FinancialYear.objects.create(year=2024)
        """Setup common data for tests."""
        self.earning_data = {
            'description': 'Freelance project',
            'amount': 1500.00,
            'date': timezone.now(),
            'attachment': SimpleUploadedFile('receipt.jpg', b'file_content', content_type='image/jpeg'),
            'reference': 'EARN123',
            'financial_year': self.financial_year,
        }

        self.expense_data = {
            'description': 'Office rent',
            'amount': 800.00,
            'purchase_date': timezone.now(),
            'attachment': SimpleUploadedFile('rent_receipt.pdf', b'file_content', content_type='application/pdf'),
            'reference': 'EXP456',
            'financial_year': self.financial_year,
        }

        self.personal_detail_data = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'gst_registered': True,
            'email': 'jane@gmail.com',
            'phone': '0271000762',
            'permanent_income': 1000000

        }

    def test_create_earning(self):
        """Test creating an earning record."""
        earning = Earning.objects.create(**self.earning_data)
        self.assertEqual(earning.description, 'Freelance project')
        self.assertEqual(earning.amount, 1500.00)
        self.assertEqual(earning.reference, 'EARN123')
        self.assertEqual(earning.financial_year.year, 2024)  # Compare the year attribute


    def test_create_expense(self):
        """Test creating an expense record."""
        expense = Expense.objects.create(**self.expense_data)
        self.assertEqual(expense.description, 'Office rent')
        self.assertEqual(expense.amount, 800.00)
        self.assertEqual(expense.reference, 'EXP456')
        self.assertEqual(expense.financial_year.year, 2024)

    def test_create_personal_detail(self):
        """Test creating personal detail record."""
        personal_detail = PersonalDetails.objects.create(**self.personal_detail_data)
        self.assertEqual(personal_detail.first_name, 'Jane')  # Check name attribute for PersonalDetail
        self.assertEqual(personal_detail.last_name, 'Doe') 
        self.assertTrue(personal_detail.gst_registered)
        self.assertEqual(personal_detail.email, "jane@gmail.com")
        self.assertEqual(personal_detail.phone, "0271000762")  # Check the financial year
        self.assertEqual(personal_detail.permanent_income, 1000000)


    def test_invalid_reference_field(self):
        """Test that invalid reference field raises error."""
        invalid_data = self.earning_data.copy()
        invalid_data['reference'] = 'X' * 21  # Invalid: longer than 20 characters

        with self.assertRaises(ValidationError):
            earning = Earning(**invalid_data)
            earning.full_clean()  # This triggers the validation manually


    def test_attachment_field(self):
        """Test that the attachment field is saved correctly."""
        expense = Expense.objects.create(**self.expense_data)
        self.assertTrue(expense.attachment.name.endswith('.pdf'))

    def test_gst_registration(self):
        """Test GST registered field works correctly."""
        personal_detail = PersonalDetails.objects.create(**self.personal_detail_data)
        self.assertTrue(personal_detail.gst_registered)