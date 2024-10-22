from django.contrib import admin
from .models import FinancialYear, Earning, Expense, BusinessCost, Depreciation, PersonalDetails

class FinancialYearAdmin(admin.ModelAdmin):
    #list_display = ['year', 'total_earnings', 'total_expenses']
    list_display = ['year']
    search_fields = ['year']

class EarningAdmin(admin.ModelAdmin):
    list_display = ['description', 'amount', 'date', 'financial_year', 'gst']
    search_fields = ['description']
    list_filter = ['financial_year']

class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['description', 'amount', 'purchase_date', 'financial_year', 'gst']
    search_fields = ['description']
    list_filter = ['financial_year']

class BusinessCostAdmin(admin.ModelAdmin):
    list_display = ['description', 'amount', 'date', 'depreciation_rate', 'financial_year']
    search_fields = ['description']
    list_filter = ['financial_year']

class DepreciationAdmin(admin.ModelAdmin):
    list_display = ['expense', 'financial_year', 'current_value', 'tax_write_off', 'years_to_zero']
    search_fields = ['expense']
    list_filter = ['expense']

class PersonalDetailsAdmin(admin.ModelAdmin):
    list_display = ['gst_registered', 'first_name', 'last_name', 'email', 'phone', 'permanent_income']
    search_fields = ['first_name']
    list_filter = ['last_name']


# Register the models with the admin site
admin.site.register(FinancialYear, FinancialYearAdmin)
admin.site.register(Earning, EarningAdmin)
admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Depreciation, DepreciationAdmin)
admin.site.register(BusinessCost, BusinessCostAdmin)
admin.site.register(PersonalDetails, PersonalDetailsAdmin)