from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.BookListView.as_view(), name='book_list'),
    # Authentication URLs
    path('register/', views.RegistrationView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    path('book/<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    
    path('add-to-cart/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/remove/', views.RemoveCartItemView.as_view(), name='remove_cart_item'),
    
    path('cart/update/', views.UpdateCartItemView.as_view(), name='update_cart_item'),
]