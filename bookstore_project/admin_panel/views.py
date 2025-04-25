from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import UserPassesTestMixin
from store.models import Book 
from decimal import Decimal, InvalidOperation 


class StaffRequiredMixin(UserPassesTestMixin):
    login_url = 'store:login' 

    def test_func(self):

        return self.request.user.is_authenticated and self.request.user.is_staff


class AdminDashboardView(StaffRequiredMixin, View):
     def get(self, request, *args, **kwargs):
         context = {
             'book_count': Book.objects.count(),
             # Add more context like user count, order count later if needed
         }
         return render(request, 'admin_panel/dashboard.html', context)

# --- Admin Book List View ---
class AdminBookListView(StaffRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        books = Book.objects.all().order_by('title')
        context = {
            'books': books,
        }
        return render(request, 'admin_panel/book_management.html', context)

# --- Admin Book Create View (Handles Image Upload) ---
class AdminBookCreateView(StaffRequiredMixin, View):
    template_name = 'admin_panel/book_form.html'
    form_title = "Add New Book"

    def get(self, request, *args, **kwargs):
        # Display an empty form
        context = {
            'form_title': self.form_title,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # Get text data
        title = request.POST.get('title', '').strip()
        author = request.POST.get('author', '').strip()
        description = request.POST.get('description', '').strip()
        price_str = request.POST.get('price', '').strip()
        stock_str = request.POST.get('stock', '').strip()
        # Get file data
        cover_image_file = request.FILES.get('cover_image') # Use request.FILES

        errors = {}
        # Store submitted text data for repopulating form on error
        book_data = { 'title': title, 'author': author, 'description': description, 'price': price_str, 'stock': stock_str }

        # --- Manual Validation (Text/Number fields) ---
        if not title: errors['title'] = 'Title is required.'
        if not author: errors['author'] = 'Author is required.'

        validated_price = None
        if not price_str: errors['price'] = 'Price is required.'
        else:
            try:
                validated_price = Decimal(price_str)
                if validated_price < 0: errors['price'] = 'Price cannot be negative.'
            except InvalidOperation: errors['price'] = 'Please enter a valid decimal number for the price.'

        validated_stock = None
        if not stock_str: errors['stock'] = 'Stock is required.'
        else:
            try:
                validated_stock = int(stock_str)
                if validated_stock < 0: errors['stock'] = 'Stock cannot be negative.'
            except ValueError: errors['stock'] = 'Please enter a valid whole number for the stock.'
        


        if errors: # If any validation errors occurred
            context = {
                'form_title': self.form_title,
                'errors': errors,
                'book_data': book_data,
            }
            return render(request, self.template_name, context)

        # --- If valid, create the book ---
        try:
            # Create book instance
            new_book = Book(
                title=title,
                author=author,
                description=description,
                price=validated_price,
                stock=validated_stock
            )
            
            if cover_image_file:
                new_book.cover_image = cover_image_file

            new_book.save() 

            return redirect('admin_panel:admin_book_list') 

        except Exception as e:
            errors['general'] = f"An unexpected error occurred: {e}"
            context = {
                'form_title': self.form_title,
                'errors': errors,
                'book_data': book_data,
            }
            return render(request, self.template_name, context)


# --- Admin Book Update View (Handles Image Upload/Clear) ---
class AdminBookUpdateView(StaffRequiredMixin, View):
    template_name = 'admin_panel/book_form.html'

    def get(self, request, pk, *args, **kwargs):
        # Retrieve the book object or return 404
        book = get_object_or_404(Book, pk=pk)
        context = {
            'form_title': f'Edit Book: {book.title}',
            'book': book, # Pass the existing book object to the template
        }
        return render(request, self.template_name, context)

    def post(self, request, pk, *args, **kwargs):
        # Retrieve the existing book object
        book = get_object_or_404(Book, pk=pk)

        # Get text data
        title = request.POST.get('title', '').strip()
        author = request.POST.get('author', '').strip()
        description = request.POST.get('description', '').strip()
        price_str = request.POST.get('price', '').strip()
        stock_str = request.POST.get('stock', '').strip()
        # Get file data
        cover_image_file = request.FILES.get('cover_image')

        clear_image = request.POST.get('clear_cover_image') == 'on'

        errors = {}

        submitted_data = { 'title': title, 'author': author, 'description': description, 'price': price_str, 'stock': stock_str }

        if not title: errors['title'] = 'Title is required.'
        if not author: errors['author'] = 'Author is required.'
        validated_price = None
        if not price_str: errors['price'] = 'Price is required.'
        else:
            try:
                validated_price = Decimal(price_str)
                if validated_price < 0: errors['price'] = 'Price cannot be negative.'
            except InvalidOperation: errors['price'] = 'Please enter a valid decimal number for the price.'
        validated_stock = None
        if not stock_str: errors['stock'] = 'Stock is required.'
        else:
            try:
                validated_stock = int(stock_str)
                if validated_stock < 0: errors['stock'] = 'Stock cannot be negative.'
            except ValueError: errors['stock'] = 'Please enter a valid whole number for the stock.'
        

        if errors: # If any validation errors occurred
            context = {
                'form_title': f'Edit Book: {book.title}',
                'errors': errors,
                'book': book, 
                'book_data': submitted_data, 
            }
            return render(request, self.template_name, context)

        # --- If valid, update the book ---
        try:
            # Update text/number fields
            book.title = title
            book.author = author
            book.description = description
            book.price = validated_price
            book.stock = validated_stock

            # --- Handle image update/clear ---
            if clear_image:
                
                if book.cover_image:
                    book.cover_image.delete(save=False) 
                book.cover_image = None 
            elif cover_image_file:
                if book.cover_image:
                     book.cover_image.delete(save=False) 
                book.cover_image = cover_image_file 
            book.save() 


            return redirect('admin_panel:admin_book_list') # Redirect after successful update

        except Exception as e:
            errors['general'] = f"An unexpected error occurred during update: {e}"
            context = {
                 'form_title': f'Edit Book: {book.title}',
                 'errors': errors,
                 'book': book,
                 'book_data': submitted_data,
             }
            return render(request, self.template_name, context)


# --- Admin Book Delete View (Unchanged) ---
class AdminBookDeleteView(StaffRequiredMixin, View):
    template_name = 'admin_panel/book_confirm_delete.html'

    def get(self, request, pk, *args, **kwargs):
        book = get_object_or_404(Book, pk=pk)
        context = { 'book': book }
        return render(request, self.template_name, context)

    def post(self, request, pk, *args, **kwargs):
        book = get_object_or_404(Book, pk=pk)
        try:
            book.delete() 
            return redirect('admin_panel:admin_book_list')
        except Exception as e:
            
            return redirect('admin_panel:admin_book_list')