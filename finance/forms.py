from django import forms
from .models import Earning, Expense, PersonalDetails, FinancialYear
from django.utils import timezone

class EarningForm(forms.ModelForm):
    class Meta:
        model = Earning
        fields = ['reference', 'description', 'amount', 'date', 'attachment']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
        }
        initial = {
            'date': timezone.now
        }

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['reference', 'description', 'amount', 'is_good', 'depreciation_rate', 'expense_type', 'attachment', 'purchase_date']
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
        }
        initial = {
            'purchase_date': timezone.now
        }

    def clean(self):
        cleaned_data = super().clean()
        purchase_date = cleaned_data.get("purchase_date")

        # Assuming the financial year runs from April 1st to March 31st
        if purchase_date:
            year = purchase_date.year
            if purchase_date.month < 4:
                # If before April, it's considered the previous financial year
                financial_year = FinancialYear.objects.get_or_create(year=year-1)[0]
            else:
                financial_year = FinancialYear.objects.get_or_create(year=year)[0]
            cleaned_data['financial_year'] = financial_year

        # Other validation rules for amount, is_good, depreciation_rate, etc.
        amount = cleaned_data.get("amount")
        is_good = cleaned_data.get("is_good")
        depreciation_rate = cleaned_data.get("depreciation_rate")

        if is_good and (amount <= 500) and depreciation_rate is not None:
            raise forms.ValidationError("Depreciation can only be applied to goods costing more than $500.")

        return cleaned_data

class PersonalDetailsForm(forms.ModelForm):
    class Meta:
        model = PersonalDetails
        fields = ['gst_registered', 'first_name', 'last_name', 'email', 'phone', 'permanent_income']

