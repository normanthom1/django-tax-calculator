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
        fields = ['reference', 'description', 'amount', 'date', 'expense_type', 'attachment']  # Removed is_depreciating and depreciation_years
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
        }
        initial = {
            'date': timezone.now
        }

class PersonalDetailsForm(forms.ModelForm):
    class Meta:
        model = PersonalDetails
        fields = ['gst_registered', 'first_name', 'last_name', 'email', 'phone', 'permanent_income']

# class EarningForm(forms.ModelForm):
#     class Meta:
#         model = Earning
#         fields = ['description', 'amount', 'date', 'reference', 'attachment']

# class ExpenseForm(forms.ModelForm):
#     class Meta:
#         model = Expense
#         fields = ['description', 'amount', 'date', 'reference', 'expense_type', 'attachment']