from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.db import models

GST_RATE = Decimal('0.15')

# Helper function to calculate NZ financial year
def get_current_financial_year():
    today = timezone.now().date()
    # NZ financial year runs from 1st April to 31st March
    if today.month >= 4:
        return today.year
    else:
        return today.year - 1


class FinancialYear(models.Model):
    year = models.IntegerField()

    def calculate_tax(self, earnings):
        personal_details = PersonalDetails.objects.first()  # Assuming only one row
        permanent_income = personal_details.permanent_income

        # New Zealand tax brackets as of 2023
        tax_brackets = [
            (0, 14000, 0.105),     # 10.5% on income up to $14,000
            (14001, 48000, 0.175), # 17.5% on income over $14,000 up to $48,000
            (48001, 70000, 0.30),  # 30% on income over $48,000 up to $70,000
            (70001, 180000, 0.33), # 33% on income over $70,000 up to $180,000
            (180001, float('inf'), 0.39),  # 39% on income over $180,000
        ]

        def calculate_tax_for_income(income):
            tax_owed = Decimal(0)
            remaining_income = income

            for lower, upper, rate in tax_brackets:
                if remaining_income > lower:
                    taxable_income_in_bracket = min(remaining_income, upper) - lower
                    
                    if taxable_income_in_bracket > 0:
                        tax_owed += Decimal(taxable_income_in_bracket) * Decimal(rate)
                        # remaining_income -= taxable_income_in_bracket

                    # if remaining_income <= 0:
                        # break
            
            return tax_owed

        # Calculate taxes separately for permanent income and earnings
        tax_owed_permanent_income = calculate_tax_for_income(permanent_income)
        tax_owed_earnings = calculate_tax_for_income(earnings)

        return round(tax_owed_permanent_income, 2), round(tax_owed_earnings, 2)


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
    ]

    reference = models.CharField(max_length=20, blank=True, null=True)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_good = models.BooleanField(default=False)
    financial_year = models.ForeignKey(FinancialYear, on_delete=models.CASCADE, related_name='expenses')
    depreciation_rate = models.FloatField(null=True, blank=True)
    expense_type = models.CharField(max_length=50, choices=EXPENSE_TYPES)
    attachment = models.FileField(upload_to='earnings_attachments/', blank=True, null=True)
    gst = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    # date = models.DateField()
    purchase_date = models.DateField()  # Ensure this field exists

    def should_depreciate(self):
        return self.is_good and self.amount > 500

    def depreciation_years(self):
        if self.depreciation_rate is not None and self.depreciation_rate > 0:
            depreciation_rate_decimal = Decimal(self.depreciation_rate) / Decimal(100)
            return int(self.amount / (self.amount * depreciation_rate_decimal))
        return 0  # Default if no depreciation rate

    def calculate_depreciation(self):
        if self.is_good and self.depreciation_rate:
            depreciation_rate_decimal = Decimal(self.depreciation_rate) / Decimal(100)
            return round(self.amount * depreciation_rate_decimal, 2)
        return 0

    def tax_impact(self):
        total_earnings = sum(exp.amount for exp in self.financial_year.expenses.all() if exp.is_good)
        tax_owed_permanent_income, tax_owed_earnings = self.financial_year.calculate_tax(total_earnings)
        adjusted_earnings = total_earnings - self.amount
        adjusted_tax_owed = self.financial_year.calculate_tax(adjusted_earnings)
        return {
            'tax_owed_permanent_income': tax_owed_permanent_income,
            'tax_owed_earnings': tax_owed_earnings,
            'adjusted_tax_owed': adjusted_tax_owed,
        }

    def calculate_depreciation_for_year(self, year):
        current_value = self.amount - self.calculate_depreciation()
        tax_write_off = self.calculate_depreciation()
        return current_value, tax_write_off

    def save(self, *args, **kwargs):
        # Calculate GST as the portion of total amount
        self.gst = self.amount - (self.amount / (1 + GST_RATE))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Expense: {self.description} - Amount: {self.amount}"

class Earning(models.Model):
    reference = models.CharField(max_length=20, blank=True, null=True)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    financial_year = models.ForeignKey(FinancialYear, on_delete=models.CASCADE, related_name='earnings')
    attachment = models.FileField(upload_to='earnings_attachments/', blank=True, null=True)
    gst = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        # Calculate GST as 15% of the amount for earnings
        self.gst = self.amount * GST_RATE
        super().save(*args, **kwargs)

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


class Depreciation(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    financial_year = models.ForeignKey('FinancialYear', on_delete=models.CASCADE)
    current_value = models.DecimalField(max_digits=10, decimal_places=2)
    tax_write_off = models.DecimalField(max_digits=10, decimal_places=2)
    years_to_zero = models.IntegerField()

class BusinessCost(models.Model):
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    depreciation_rate = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 0.20 for 20% depreciation rate
    financial_year = models.ForeignKey(FinancialYear, on_delete=models.CASCADE, related_name='business_costs')

    def __str__(self):
        return self.description
