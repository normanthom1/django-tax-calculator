from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from .models import FinancialYear, Earning, Expense, get_current_financial_year, PersonalDetails
from .forms import EarningForm, ExpenseForm, PersonalDetailsForm
from django.utils import timezone
from django.db.models import Avg, Count, Min, Sum
from django.views.generic import DetailView, UpdateView
from django.urls import reverse_lazy
from decimal import Decimal
from django.shortcuts import render
from .models import FinancialYear, Earning, Expense, BusinessCost

def dashboard(request):
    # Get the current financial year
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

    # Use the model's calculate_tax method to get the correct tax owed
    tax_owed_permanent_income, tax_owed_earnings = financial_year.calculate_tax(total_earnings)

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
    }

    return render(request, 'dashboard.html', context)

# Add earning
def add_earning(request):
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

# Add expense
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.financial_year = FinancialYear.objects.get_or_create(year=get_current_financial_year())[0]
            expense.save()
            return redirect('dashboard')
    else:
        form = ExpenseForm()
    return render(request, 'add_expense.html', {'form': form})

# Delete earning
def delete_earning(request, pk):
    earning = get_object_or_404(Earning, pk=pk)
    earning.delete()
    return redirect('dashboard')

# Delete expense
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    expense.delete()
    return redirect('dashboard')

# Financial year details
def financial_year_detail(request, pk):
    # financial_year = get_object_or_404(FinancialYear, pk=pk)
    financial_year = FinancialYear.objects.get(current=True)
    earnings = Earning.objects.filter(financial_year=financial_year)
    expenses = Expense.objects.filter(financial_year=financial_year)
    # total_earnings = earnings.aggregate(total=models.Sum('amount'))['total'] or 0
    total_earnings = sum(earning.amount for earning in financial_year.earnings.all())
    # total_expenses = expenses.aggregate(total=models.Sum('amount'))['total'] or 0
    total_expenses = sum(expense.amount for expense in financial_year.expenses.all())
    # tax_owed = total_earnings * 0.33 - total_expenses
    tax_owed = financial_year.calculate_tax(total_earnings)

    return render(request, 'financial_year_detail.html', {
        'financial_year': financial_year,
        'earnings': earnings,
        'expenses': expenses,
        'total_earnings': total_earnings,
        'total_expenses': total_expenses,
        'tax_owed': tax_owed,
    })

def update_personal_details(request):
    # Get the existing instance or create one
    personal_details, created = PersonalDetails.objects.get_or_create()

    if request.method == 'POST':
        form = PersonalDetailsForm(request.POST, instance=personal_details)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # Redirect to the dashboard or desired page
    else:
        form = PersonalDetailsForm(instance=personal_details)

    return render(request, 'update_personal_details.html', {'form': form})


class EarningDetailView(DetailView):
    model = Earning
    template_name = 'earning_detail.html'  # You need to create this template
    context_object_name = 'earning'

class ExpenseDetailView(DetailView):
    model = Expense
    template_name = 'expense_detail.html'  # You need to create this template
    context_object_name = 'expense'

class EarningUpdateView(UpdateView):
    model = Earning
    form_class = EarningForm
    template_name = 'earning_update.html'
    success_url = reverse_lazy('dashboard')  # Redirect back to the dashboard after updating

class ExpenseUpdateView(UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expense_update.html'
    success_url = reverse_lazy('dashboard')  # Redirect back to the dashboard after updating
