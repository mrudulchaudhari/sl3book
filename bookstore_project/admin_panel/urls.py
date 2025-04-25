from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Custom admin dashboard
    path('', views.AdminDashboardView.as_view(), name='dashboard'),

    # --- Book Management URLs ---
    path('books/', views.AdminBookListView.as_view(), name='admin_book_list'), # List books
    path('books/add/', views.AdminBookCreateView.as_view(), name='admin_book_add'), # Add book form/handler
    path('books/edit/<int:pk>/', views.AdminBookUpdateView.as_view(), name='admin_book_edit'), # Edit book form/handler
    path('books/delete/<int:pk>/', views.AdminBookDeleteView.as_view(), name='admin_book_delete'), # Delete book confirmation/handler

]