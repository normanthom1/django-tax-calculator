from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal

# Helper function to calculate NZ financial year
def get_current_financial_year():
    today = timezone.now().date()
    # NZ financial year runs from 1st April to 31st March
    if today.month >= 4:
        return today.year
    else:
        return today.year - 1

# class FinancialYear(models.Model):
#     year = models.CharField(max_length=9)  # e.g., "2023-2024"
#     # Other fields for the FinancialYear model

#     def __str__(self):
#         return self.year
from django.db import models

from decimal import Decimal

class FinancialYear(models.Model):
    year = models.IntegerField()

    def calculate_tax(self, earnings):
        # Fetch the permanent income from PersonalDetails
        personal_details = PersonalDetails.objects.first()  # Assuming only one row
        permanent_income = personal_details.permanent_income

        # New Zealand tax brackets as of 2023 (adjust as needed)
        tax_brackets = [
            (0, 14000, 0.105),     # 10.5% on income up to $14,000
            (14001, 48000, 0.175), # 17.5% on income over $14,000 up to $48,000
            (48001, 70000, 0.30),  # 30% on income over $48,000 up to $70,000
            (70001, 180000, 0.33), # 33% on income over $70,000 up to $180,000
            (180001, float('inf'), 0.39),  # 39% on income over $180,000
        ]

        def calculate_tax_for_income(income):
            tax_owed = 0
            remaining_income = income  # Remaining income to be taxed

            # Calculate tax progressively through the tax brackets
            for lower, upper, rate in tax_brackets:
                if remaining_income > lower:
                    # The income to tax in this bracket
                    taxable_income_in_bracket = min(remaining_income, upper - lower)
                    
                    # Apply the tax rate to the income in this bracket
                    tax_owed += Decimal(taxable_income_in_bracket) * Decimal(rate)
                    
                    # Deduct the taxed portion from remaining income
                    remaining_income -= taxable_income_in_bracket

                    # If there's no more remaining income to tax, stop
                    if remaining_income <= 0:
                        break

            return max(tax_owed, 0)  # Ensure tax owed is never negative

        # Calculate taxes separately
        tax_owed_permanent_income = calculate_tax_for_income(permanent_income)
        tax_owed_earnings = calculate_tax_for_income(earnings)

        return tax_owed_permanent_income, tax_owed_earnings

    def get_next_year(self):
        return self.year + 1

    def __str__(self):
        return f"Financial Year: {str(self.year)}"



class Earning(models.Model):
    reference = models.CharField(max_length=20, blank=True, null=True)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    financial_year = models.ForeignKey(FinancialYear, on_delete=models.CASCADE, related_name='earnings')
    attachment = models.FileField(upload_to='earnings_attachments/', blank=True, null=True)

    def __str__(self):
        return self.description

class PersonalDetails(models.Model):
    gst_registered = models.BooleanField(default=False)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    permanent_income = models.FloatField(default=0)

    def clean(self):
        """Override clean method to ensure only one instance of PersonalDetails."""
        if PersonalDetails.objects.exists() and not self.pk:
            raise ValidationError('Only one instance of PersonalDetails can exist.')

    def save(self, *args, **kwargs):
        """Override save method to ensure only one instance of PersonalDetails."""
        self.full_clean()  # Call clean to enforce the unique instance
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"



class Expense(models.Model):
    EXPENSE_TYPES = [
        ('office_supplies', 'Office Supplies'),
        ('travel', 'Travel'),
        ('equipment', 'Equipment'),
        ('utilities', 'Utilities'),
        ('marketing', 'Marketing'),
        ('insurance', 'Insurance'),
        ('salaries', 'Salaries'),
        ('rent', 'Rent'),
        ('professional_services', 'Professional Services'),
        # Add more types as needed
    ]

    reference = models.CharField(max_length=20, blank=True, null=True)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    financial_year = models.ForeignKey(FinancialYear, on_delete=models.CASCADE, related_name='expenses')
    expense_type = models.CharField(max_length=50, choices=EXPENSE_TYPES)
    is_depreciating = models.BooleanField(default=False, editable=False)  # Make non-editable
    depreciation_years = models.IntegerField(null=True, blank=True, editable=False)  # Make non-editable
    attachment = models.FileField(upload_to='earnings_attachments/', blank=True, null=True)

    def calculate_depreciation_years(self):
        """Calculate depreciation years based on the amount."""
        if self.amount < 500:
            return None  # No depreciation for items under $500
        elif self.amount < 1000:
            return 5
        elif self.amount < 5000:
            return 10
        else:
            return 15

    def save(self, *args, **kwargs):
        """Override save method to calculate depreciation years automatically."""
        if self.amount >= 500:  # Automatically set is_depreciating if amount is $500 or more
            self.is_depreciating = True
            self.depreciation_years = self.calculate_depreciation_years()
        else:
            self.is_depreciating = False  # Set to False if amount is less than $500
            self.depreciation_years = None  # Reset if not depreciating
        super().save(*args, **kwargs)

    def __str__(self):
        return self.description

class BusinessCost(models.Model):
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    depreciation_rate = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 0.20 for 20% depreciation rate
    financial_year = models.ForeignKey(FinancialYear, on_delete=models.CASCADE, related_name='business_costs')

    def __str__(self):
        return self.description
