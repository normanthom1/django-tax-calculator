from django import forms
from .models import Earning, Expense, PersonalDetails
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
        fields = ['reference', 'description', 'amount', 'is_good', 'financial_year', 'depreciation_rate', 'expense_type', 'attachment', 'purchase_date']
        widgets = {
            # 'date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'purchase_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
        }
        initial = {
            # 'date': timezone.now,
            'purchase_date': timezone.now
        }

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get("amount")
        is_good = cleaned_data.get("is_good")
        depreciation_rate = cleaned_data.get("depreciation_rate")

        if is_good and (amount <= 500) and depreciation_rate is not None:
            raise forms.ValidationError("Depreciation can only be applied to goods costing more than $500.")


class PersonalDetailsForm(forms.ModelForm):
    class Meta:
        model = PersonalDetails
        fields = ['gst_registered', 'first_name', 'last_name', 'email', 'phone', 'permanent_income']

