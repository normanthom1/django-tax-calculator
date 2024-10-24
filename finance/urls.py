from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/pdf/', views.dashboard_pdf, name='dashboard_pdf'),
    path('add-earning/', views.add_earning, name='add_earning'),
    path('add-expense/', views.add_expense, name='add_expense'),
    path('financial-year/<int:pk>/', views.financial_year_detail, name='financial_year_detail'),
    path('delete-earning/<int:pk>/', views.delete_earning, name='delete_earning'),
    path('delete-expense/<int:pk>/', views.delete_expense, name='delete_expense'),
    path('update-personal-details/', views.update_personal_details, name='update_personal_details'),
    path('earning/<int:earnings_id>/', views.earnings_detail, name='earning_detail'),
    path('expense/<int:expense_id>/', views.expense_detail, name='expense_detail'),
    path('earning/update/<int:pk>/', views.EarningUpdateView.as_view(), name='earning_update'),
    path('expense/update/<int:pk>/', views.update_expense, name='update_expense'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
