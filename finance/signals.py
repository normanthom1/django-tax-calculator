# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Expense, Depreciation, FinancialYear

@receiver(post_save, sender=Expense)
def create_depreciation(sender, instance, created, **kwargs):
    if created and instance.should_depreciate():
        years = instance.depreciation_years()
        for year in range(instance.purchase_date.year, instance.purchase_date.year + years):
            financial_year, _ = FinancialYear.objects.get_or_create(year=year)
            current_value, tax_write_off = instance.calculate_depreciation_for_year(year)
            years_to_zero = years - (year - instance.purchase_date.year)
            Depreciation.objects.create(
                expense=instance,
                financial_year=financial_year,
                current_value=current_value,
                tax_write_off=tax_write_off,
                years_to_zero=years_to_zero
            )
