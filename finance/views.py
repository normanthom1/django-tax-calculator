from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from .models import FinancialYear, Earning, Expense, get_current_financial_year, PersonalDetails
from .forms import EarningForm, ExpenseForm, PersonalDetailsForm
from django.utils import timezone
from django.db.models import Avg, Count, Min, Sum
from django.views.generic import DetailView, UpdateView
from django.urls import reverse_lazy
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.template.loader import get_template

GST_RATE = Decimal(0.15)

def dashboard(request):
    """
    Render the dashboard showing the current financial year, total earnings,
    expenses, and tax owed based on personal details.
    """
    current_financial_year = get_current_financial_year()
    financial_year, created = FinancialYear.objects.get_or_create(year=current_financial_year)

    # Get personal details
    personal_details = PersonalDetails.objects.first()

    # Retrieve earnings and expenses for the current financial year
    earnings = Earning.objects.filter(financial_year=financial_year)
    expenses = Expense.objects.filter(financial_year=financial_year)

    # Calculate totals
    total_earnings = earnings.aggregate(total=Sum('amount'))['total'] or Decimal(0)
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or Decimal(0)

    # Calculate adjusted earnings
    adjusted_earnings = total_earnings - total_expenses

    # Calculate tax owed
    tax_owed_permanent_income, tax_owed_earnings = financial_year.calculate_tax(adjusted_earnings, personal_details.gst_registered)

    # Calculate GST if registered
    gst_to_pay = total_earnings * GST_RATE if personal_details.gst_registered else Decimal(0)
    gst_to_claim = total_expenses * GST_RATE if personal_details.gst_registered else Decimal(0)

    # Prepare the context
    context = {
        'financial_year': financial_year,
        'earnings': earnings,
        'expenses': expenses,
        'personal_details': personal_details,
        'total_earnings': total_earnings,
        'total_expenses': total_expenses,
        'tax_owed_permanent_income': tax_owed_permanent_income,
        'tax_owed_earnings': tax_owed_earnings,
        'gst_registered': personal_details.gst_registered,
        'gst_to_pay': gst_to_pay,
        'gst_to_claim': gst_to_claim,
    }

    return render(request, 'dashboard.html', context)

def dashboard_pdf(request):
    """
    Generate a PDF version of the dashboard without buttons like 'Add' and 'Update'.
    """
    current_financial_year = get_current_financial_year()
    financial_year, created = FinancialYear.objects.get_or_create(year=current_financial_year)

    # Get personal details
    personal_details = PersonalDetails.objects.first()

    # Retrieve earnings and expenses for the current financial year
    earnings = Earning.objects.filter(financial_year=financial_year)
    expenses = Expense.objects.filter(financial_year=financial_year)

    # Calculate totals
    total_earnings = earnings.aggregate(total=Sum('amount'))['total'] or Decimal(0)
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or Decimal(0)

    # Calculate adjusted earnings
    adjusted_earnings = total_earnings - total_expenses

    # Calculate tax owed
    tax_owed_permanent_income, tax_owed_earnings = financial_year.calculate_tax(adjusted_earnings, personal_details.gst_registered)

    # Calculate GST if registered
    gst_to_pay = total_earnings * GST_RATE if personal_details.gst_registered else Decimal(0)
    earnings_plus_gst = total_earnings + (total_earnings * GST_RATE)
    gst_to_claim = total_expenses * GST_RATE if personal_details.gst_registered else Decimal(0)

    # Prepare the context
    context = {
        'financial_year': financial_year,
        'earnings': earnings,
        'expenses': expenses,
        'personal_details': personal_details,
        'total_earnings': total_earnings,
        'total_expenses': total_expenses,
        'tax_owed_permanent_income': tax_owed_permanent_income,
        'tax_owed_earnings': tax_owed_earnings,
        'gst_registered': personal_details.gst_registered,
        'gst_to_pay': gst_to_pay,
        'gst_to_claim': gst_to_claim,
    }
    template_path = 'dashboard_pdf.html'  # A template without buttons

    # Render the HTML template into PDF
    template = get_template(template_path)
    html = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="dashboard.pdf"'

    # Create PDF from HTML
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

def financial_year_detail(request, pk):
    """
    Render the details of a specific financial year, including total earnings,
    expenses, and tax owed.
    """
    financial_year = get_object_or_404(FinancialYear, pk=pk)
    earnings = Earning.objects.filter(financial_year=financial_year)
    expenses = Expense.objects.filter(financial_year=financial_year)

    total_earnings = sum(earning.amount for earning in earnings)
    total_expenses = sum(expense.amount for expense in expenses)

    # Calculate tax owed using the updated model method
    tax_owed_permanent_income, tax_owed_earnings = financial_year.calculate_tax(total_earnings)

    return render(request, 'financial_year_detail.html', {
        'financial_year': financial_year,
        'earnings': earnings,
        'expenses': expenses,
        'total_earnings': total_earnings,
        'total_expenses': total_expenses,
        'tax_owed_permanent_income': tax_owed_permanent_income,
        'tax_owed_earnings': tax_owed_earnings,
    })

def delete_earning(request, pk):
    """
    Delete a specific earning entry and redirect to the dashboard.
    """
    earning = get_object_or_404(Earning, pk=pk)
    earning.delete()
    return redirect('dashboard')

def delete_expense(request, pk):
    """
    Delete a specific expense entry and redirect to the dashboard.
    """
    expense = get_object_or_404(Expense, pk=pk)
    expense.delete()
    return redirect('dashboard')


def update_personal_details(request):
    """
    Update personal details. If no instance exists, create a new one.
    Redirect to the dashboard after saving changes.
    """
    personal_details, created = PersonalDetails.objects.get_or_create()

    if request.method == 'POST':
        form = PersonalDetailsForm(request.POST, instance=personal_details)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # Redirect to the dashboard or desired page
    else:
        form = PersonalDetailsForm(instance=personal_details)

    return render(request, 'update_personal_details.html', {'form': form})

def earnings_detail(request, earnings_id):
    """
    Render the details of a specific earning, including the amount and GST
    based on personal details.
    """
    earning = Earning.objects.get(id=earnings_id)
    personal_details = PersonalDetails.objects.first()  # Assuming only one row
    including_gst = earning.amount + earning.gst

    context = {
        'earning': earning,
        'including_gst': including_gst,
        'is_gst_registered': personal_details.gst_registered,
    }
    return render(request, 'earning_detail.html', context)

def expense_detail(request, expense_id):
    """
    Render the details of a specific expense, including the amount and GST
    based on personal details.
    """
    expense = Expense.objects.get(id=expense_id)
    personal_details = PersonalDetails.objects.first()  # Assuming only one row
    total_excluding_gst = expense.amount - expense.gst

    context = {
        'expense': expense,
        'is_gst_registered': personal_details.gst_registered,
        'total_excluding_gst': total_excluding_gst
    }
    return render(request, 'expense_detail.html', context)

class EarningUpdateView(UpdateView):
    """
    Update view for Earning instances. Redirects to the dashboard after
    a successful update.
    """
    model = Earning
    form_class = EarningForm
    template_name = 'earning_update.html'
    success_url = reverse_lazy('dashboard')  # Redirect back to the dashboard after updating

    def get_context_data(self, **kwargs):
        """
        Add additional context variables to the template.
        """
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Earning'
        return context
        
def add_earning(request):
    """
    Add a new earning entry. Redirect to the dashboard upon successful addition.
    """
    if request.method == 'POST':
        form = EarningForm(request.POST, request.FILES)
        if form.is_valid():
            earning = form.save(commit=False)
            earning.financial_year = FinancialYear.objects.get_or_create(year=get_current_financial_year())[0]
            earning.save()
            return redirect('dashboard')
    else:
        form = EarningForm()
    return render(request, 'add_earning.html', {'form': form})

def add_expense(request):
    """
    Add a new expense entry. Redirect to the dashboard upon successful addition.
    """
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)  # Don't save to the database yet

            # Set the financial_year from cleaned_data
            financial_year = form.cleaned_data.get('financial_year')
            if financial_year:
                expense.financial_year = financial_year

            expense.save()  # Now save to the database
            return redirect('dashboard')
        else:
            print(form.errors)
    else:
        form = ExpenseForm()

    return render(request, 'add_expense.html', {'form': form})

def update_expense(request, pk):
    """
    Update a specific expense entry. Redirect to the dashboard upon successful update.
    """
    expense = Expense.objects.get(pk=pk)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, instance=expense)

        if form.is_valid():
            expense = form.save(commit=False)  # Don't save to the database yet

            # Set the financial_year from cleaned_data
            financial_year = form.cleaned_data.get('financial_year')
            if financial_year:
                expense.financial_year = financial_year

            expense.save()  # Now save to the database
            return redirect('dashboard')
        else:
            print(form.errors)
    else:
        form = ExpenseForm(instance=expense)

    return render(request, 'expense_update.html', {'form': form})
