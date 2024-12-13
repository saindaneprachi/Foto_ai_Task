from rest_framework import serializers
from .models import Users, Book, BorrowRequest

#serializers
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'username', 'email', 'is_librarian']

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'book_unique_code']

class BorrowRequestSerializer(serializers.ModelSerializer):

    user = serializers.SlugRelatedField(
        queryset=Users.objects.all(),
        slug_field='username',  # Match username instead of ID
    
        error_messages={
            'does_not_exist': 'User with username "{value}" was not found.',
            'invalid': 'Invalid value for user.'
        }
    )
    book = serializers.SlugRelatedField(
        queryset=Book.objects.all(),
        slug_field='title',  # Match book title instead of ID
    
        error_messages={
            'does_not_exist': 'Book with title "{value}" was not found.',
            'invalid': 'Invalid value for book.'
        }
    )
    
    class Meta:
        model = BorrowRequest
        fields = ['id', 'user', 'book', 'date_from', 'date_to', 'status']

