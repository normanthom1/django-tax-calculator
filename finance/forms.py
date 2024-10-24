from django import forms
from .models import Earning, Expense, PersonalDetails, FinancialYear
from django.utils import timezone

class EarningForm(forms.ModelForm):
    """
    A form for creating and updating Earnings.

    Attributes:
        Meta: Defines the model and fields to include in the form.
    """
    class Meta:
        model = Earning
        fields = ['reference', 'description', 'amount', 'date', 'attachment']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')  # Use a date input widget for the date field
        }


class ExpenseForm(forms.ModelForm):
    """
    A form for creating and updating Expenses.

    This form includes validation logic to associate expenses with the correct financial year
    based on the purchase date, and to ensure depreciation is applied correctly.

    Attributes:
        Meta: Defines the model and fields to include in the form.
    """
    class Meta:
        model = Expense
        fields = ['reference', 'description', 'amount', 'is_good', 'depreciation_rate', 'expense_type', 'attachment', 'purchase_date']
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),  # Use a date input widget for the purchase date field
            'depreciation_rate': forms.NumberInput(attrs={'min': '0', 'max': '100', 'type': 'number'}),
        }
        initial = {
            'purchase_date': timezone.now  # Set the initial value of purchase_date to the current date
        }

    def clean_depreciation_rate(self):
        depreciation_rate = self.cleaned_data.get('depreciation_rate')
        
        if depreciation_rate is not None:
            if depreciation_rate < 0 or depreciation_rate > 100:
                raise forms.ValidationError("Depreciation rate must be between 0 and 100.")
        
        return depreciation_rate

    def clean(self):
        """
        Custom validation for the Expense form.

        This method ensures that the purchase date is associated with the correct financial year
        and checks if depreciation is applied to goods that cost more than $500.
        
        Returns:
            dict: The cleaned data with any added financial year information.
        """
        cleaned_data = super().clean()
        purchase_date = cleaned_data.get("purchase_date")

        # Determine the financial year based on the purchase date
        if purchase_date:
            year = purchase_date.year
            if purchase_date.month < 4:
                # If before April, it's considered the previous financial year
                financial_year = FinancialYear.objects.get_or_create(year=year - 1)[0]
            else:
                financial_year = FinancialYear.objects.get_or_create(year=year)[0]
            cleaned_data['financial_year'] = financial_year

        # Other validation rules for amount, is_good, depreciation_rate, etc.
        amount = cleaned_data.get("amount")
        is_good = cleaned_data.get("is_good")
        depreciation_rate = cleaned_data.get("depreciation_rate")

        # Raise a validation error if depreciation is incorrectly applied
        if is_good and (amount <= 500) and depreciation_rate is not None:
            raise forms.ValidationError("Depreciation can only be applied to goods costing more than $500.")

        return cleaned_data


class PersonalDetailsForm(forms.ModelForm):
    """
    A form for creating and updating Personal Details.

    Attributes:
        Meta: Defines the model and fields to include in the form.
    """
    class Meta:
        model = PersonalDetails
        fields = ['gst_registered', 'first_name', 'last_name', 'email', 'phone', 'permanent_income']
