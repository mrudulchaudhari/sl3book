from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import HttpResponseBadRequest 
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Book
from decimal import Decimal 

# --- Book List View ---
class BookListView(View):
    def get(self, request, *args, **kwargs):
        books = Book.objects.all().order_by('title')
        context = { 'books': books }
        return render(request, 'store/book_list.html', context)

# --- Registration View (Full Code) ---
class RegistrationView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('store:book_list')
        return render(request, 'store/registration.html')

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        error_occurred = False
        context_data = {'username': username, 'email': email}
        errors = {}

        if not username or not password or not password_confirm:
            errors['general'] = 'Please fill in all required fields.'
            error_occurred = True
        if password != password_confirm:
            errors['passwords_mismatch'] = 'Passwords do not match.'
            error_occurred = True
        if User.objects.filter(username=username).exists():
            errors['general'] = 'Username already taken.'
            context_data.pop('username', None)
            error_occurred = True
        if email and '@' not in email:
             errors['general'] = 'Please enter a valid email address.'
             error_occurred = True
        elif email and User.objects.filter(email=email).exists():
             errors['general'] = 'Email address already registered.'
             context_data.pop('email', None)
             error_occurred = True

        if error_occurred:
            context_data['errors'] = errors
            return render(request, 'store/registration.html', context_data)
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            return redirect('store:login')
        except Exception as e:
            context_data['errors'] = {'general': f'An error occurred: {e}'}
            return render(request, 'store/registration.html', context_data)

# --- Login View (Full Code) ---
class LoginView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('store:book_list')
        return render(request, 'store/login.html')

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password')
        context_data = {'username': username}

        if not username or not password:
            context_data['error_message'] = 'Please provide both username and password.'
            return render(request, 'store/login.html', context_data)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            else:
                return redirect('store:book_list')
        else:
            context_data['error_message'] = 'Invalid username or password.'
            return render(request, 'store/login.html', context_data)

# --- Logout View (Full Code) ---
class LogoutView(View):
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
        return redirect('store:book_list')

# --- Book Detail View ---
class BookDetailView(View):
    def get(self, request, pk, *args, **kwargs):
        book = get_object_or_404(Book, pk=pk)
        context = { 'book': book }
        return render(request, 'store/book_detail.html', context)

# --- Add To Cart View ---
class AddToCartView(View):
    def post(self, request, *args, **kwargs):
        book_id = request.POST.get('book_id')
        quantity_str = request.POST.get('quantity', '1')

        if not book_id:
            return redirect(request.META.get('HTTP_REFERER', 'store:book_list'))
        try:
            quantity = int(quantity_str)
            if quantity <= 0:
                return redirect(request.META.get('HTTP_REFERER', 'store:book_list'))
        except ValueError:
            return redirect(request.META.get('HTTP_REFERER', 'store:book_list'))
        try:
            book = Book.objects.get(pk=book_id)
        except Book.DoesNotExist:
            return redirect(request.META.get('HTTP_REFERER', 'store:book_list'))
        if not book.is_in_stock():
            return redirect(request.META.get('HTTP_REFERER', 'store:book_list'))

        cart = request.session.get('cart', {})
        book_id_str = str(book.id)
        current_quantity_in_cart = cart.get(book_id_str, 0)
        desired_quantity = current_quantity_in_cart + quantity
        # Cap quantity at available stock
        final_quantity = min(desired_quantity, book.stock)

        if final_quantity > 0 :
             cart[book_id_str] = final_quantity
        elif book_id_str in cart: # If capping results in 0 or less, remove
             del cart[book_id_str]

        request.session['cart'] = cart
        request.session.modified = True

        return redirect(request.META.get('HTTP_REFERER', 'store:book_list'))

# --- Cart View ---
class CartView(View):
    template_name = 'store/cart.html'

    def get(self, request, *args, **kwargs):
        cart_session_data = request.session.get('cart', {})
        cart_items = []
        total_cart_price = Decimal('0.00')

        book_ids = cart_session_data.keys()
        books_in_cart = Book.objects.filter(pk__in=book_ids)
        book_dict = {str(book.pk): book for book in books_in_cart}

        items_to_remove = []

        for book_id_str, quantity in list(cart_session_data.items()): # Use list() for safe iteration while potentially modifying
            book = book_dict.get(book_id_str)

            if book and quantity > 0:
                 actual_quantity = min(quantity, book.stock) # Re-check stock
                 if actual_quantity <= 0:
                      items_to_remove.append(book_id_str)
                      continue

                 item_subtotal = book.price * Decimal(actual_quantity)
                 cart_items.append({
                     'book': book,
                     'quantity': actual_quantity,
                     'subtotal': item_subtotal,
                 })
                 total_cart_price += item_subtotal

                 if actual_quantity != quantity: # Update session if quantity was adjusted
                     cart_session_data[book_id_str] = actual_quantity

            else: # Book not found in DB or quantity <= 0 in session
                items_to_remove.append(book_id_str)

        # Clean up session
        if items_to_remove:
            for item_id in items_to_remove:
                if item_id in cart_session_data:
                    del cart_session_data[item_id]
            request.session['cart'] = cart_session_data
            request.session.modified = True

        context = {
            'cart_items': cart_items,
            'total_cart_price': total_cart_price,
        }
        return render(request, self.template_name, context)
    
class RemoveCartItemView(View):
    # This view only handles POST requests for safety
    def post(self, request, *args, **kwargs):
        book_id = request.POST.get('book_id')

        # Basic validation: Check if book_id was provided
        if not book_id:
            
            return redirect('store:cart')

        # Get the current cart from session
        cart = request.session.get('cart', {})
        book_id_str = str(book_id) # Convert to string as session keys are strings

        # Remove the item from the cart dictionary if it exists
        if book_id_str in cart:
            del cart[book_id_str]
            # Save the updated cart back into the session
            request.session['cart'] = cart
            request.session.modified = True
            
        return redirect('store:cart')


class UpdateCartItemView(View):
    # This view only handles POST requests
    def post(self, request, *args, **kwargs):
        book_id = request.POST.get('book_id')
        quantity_str = request.POST.get('quantity', '1') # Default to 1

        
        if not book_id:
            return redirect('store:cart') # Redirect back to cart on error

        try:
            
            quantity = int(quantity_str)
            if quantity < 0:
                 return redirect('store:cart')
        except ValueError:
            return redirect('store:cart') # Not an integer

        try:
            book = Book.objects.get(pk=book_id) 
        except Book.DoesNotExist:
             return redirect('store:cart') 

        # --- Session Logic ---
        cart = request.session.get('cart', {})
        book_id_str = str(book.id)

        if book_id_str not in cart:
             return redirect('store:cart') # Item not in cart

        if quantity == 0:
             final_quantity = 0
        else:
             final_quantity = min(quantity, book.stock)
             if final_quantity <= 0 and book.stock <= 0: # If stock is 0, ensure removal
                 final_quantity = 0


        
        if final_quantity > 0:
            cart[book_id_str] = final_quantity
        else:
            
            if book_id_str in cart: 
                 del cart[book_id_str]

        request.session['cart'] = cart
        request.session.modified = True


        return redirect('store:cart')

    def get(self, request, *args, **kwargs):
         return redirect('store:cart')