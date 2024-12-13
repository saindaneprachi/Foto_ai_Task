from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

# Models
class Users(AbstractUser):
    is_librarian = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username}"

    
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    book_unique_code = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return f"{self.title} by {self.author}"

    
class BorrowRequest(models.Model):
    STATUS = (('Pending', 'Pending'), 
              ('Approved', 'Approved'), 
              ('Denied', 'Denied'))
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    date_from = models.DateField()
    date_to = models.DateField()
    status = models.CharField(max_length=10, choices= STATUS, default='Pending')

    def __str__(self):
        return f"Request by {self.user.username} for '{self.book.title}' - {self.status}"

