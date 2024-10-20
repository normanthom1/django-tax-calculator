from django.contrib import admin
from .models import FinancialYear, Earning, Expense, BusinessCost

class FinancialYearAdmin(admin.ModelAdmin):
    #list_display = ['year', 'total_earnings', 'total_expenses']
    list_display = ['year']
    search_fields = ['year']

class EarningAdmin(admin.ModelAdmin):
    list_display = ['description', 'amount', 'date', 'financial_year']
    search_fields = ['description']
    list_filter = ['financial_year']

class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['description', 'amount', 'date', 'financial_year', 'is_depreciating']
    search_fields = ['description']
    list_filter = ['financial_year', 'is_depreciating']

class BusinessCostAdmin(admin.ModelAdmin):
    list_display = ['description', 'amount', 'date', 'depreciation_rate', 'financial_year']
    search_fields = ['description']
    list_filter = ['financial_year']

# Register the models with the admin site
admin.site.register(FinancialYear, FinancialYearAdmin)
admin.site.register(Earning, EarningAdmin)
admin.site.register(Expense, ExpenseAdmin)
admin.site.register(BusinessCost, BusinessCostAdmin)
