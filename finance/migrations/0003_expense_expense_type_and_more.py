# Generated by Django 5.1.2 on 2024-10-18 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0002_alter_financialyear_year'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='expense_type',
            field=models.CharField(choices=[('office_supplies', 'Office Supplies'), ('travel', 'Travel'), ('equipment', 'Equipment'), ('utilities', 'Utilities'), ('marketing', 'Marketing'), ('insurance', 'Insurance'), ('salaries', 'Salaries'), ('rent', 'Rent'), ('professional_services', 'Professional Services')], default='travel', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='expense',
            name='depreciation_years',
            field=models.IntegerField(blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='expense',
            name='is_depreciating',
            field=models.BooleanField(default=False, editable=False),
        ),
    ]
