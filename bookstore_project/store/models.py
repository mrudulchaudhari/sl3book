from django.db import models


class Book(models.Model):
    """Represents a book in the store."""
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    
    cover_image = models.ImageField(
        upload_to='book_covers/',
        blank=True,
        null=True
    )
    
    def __str__(self):
        return self.title

    def is_in_stock(self):
        """Check if the book is available."""
        return self.stock > 0

    