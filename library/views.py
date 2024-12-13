from django.shortcuts import render
from rest_framework import serializers, permissions, status
from library.models import Users, Book, BorrowRequest
from rest_framework import viewsets
from rest_framework.views import APIView
from .permissions import IsLibrarian, IsAuthenticatedUser
from .serializers import UserSerializer, BookSerializer, BorrowRequestSerializer
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from datetime import date
from pandas import read_csv
import csv
from django.db.models import Case, When, Value, IntegerField

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsLibrarian]

    '''creating user'''

    def create(self, request, *args, **kwargs):
        data = request.data
        data['is_librarian'] = False        #modify incoming data default=false
        serializer = self.get_serializer(data=data)   #initializing serializer data
        serializer.is_valid(raise_exception=True)     #raising exception if occurs
        # Create the user instance but do not save it yet
        user = serializer.save()
        
        # Hash the password
        password = data.get('password')
        if password:
            user.set_password(password)
            user.save()
        
        # Save the user instance to the database
        

        return Response(serializer.data, status=status.HTTP_201_CREATED)


        # self.perform_create(serializer)                #save validated data to db
        # return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedUser,IsLibrarian]


class BorrowRequestViewSet(viewsets.ModelViewSet):
    queryset = BorrowRequest.objects.all()
    serializer_class = BorrowRequestSerializer

    def get_permissions(self):
        if self.action in ['approve', 'deny']:
            return [IsLibrarian()]
        return [IsAuthenticatedUser()]
    
    
    '''Here creating borrow requests for users by ensuring from date is either today or 
    in future, checing for existing borrow requests and overlapping requests'''
    
    def perform_create(self, serializer):
        data = serializer.validated_data
        if data['date_from'] < date.today():              # Ensure 'date_from' is today or in the future
            raise serializers.ValidationError("The start date cannot be in the past.")
        
        # Check if the user already has a borrow request for the same book
        existing_request = BorrowRequest.objects.filter(
            book=data['book'],
            user=self.request.user             
        ).exclude(status='Denied')  # Exclude denied requests 

        if existing_request.exists():
            raise serializers.ValidationError("You already have a borrow request for this book.")

        # Check for overlapping requests with 'Approved' status
        overlapping_requests = BorrowRequest.objects.filter(
            book=data['book'],
            date_from__lt=data['date_to'],
            date_to__gt=data['date_from'],
            status='Approved'
        )
        if overlapping_requests.exists():
            raise serializers.ValidationError("Book is already borrowed for the selected period.")
        serializer.save(user=self.request.user)


    '''Here approving borrow requests by ensuring is book already borrowed, 
    is dates overlapping'''

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self,request,pk=None):
        borrow_request = self.get_object()
    
    # Check if the book is already borrowed during the requested period
        overlapping_requests = BorrowRequest.objects.filter(
            book=borrow_request.book,
            date_from__lt=borrow_request.date_to,  # Overlaps with the current request
            date_to__gt=borrow_request.date_from,
            status='Approved'  # Only consider approved requests
        ).exclude(pk=borrow_request.pk)  # Exclude the current request
        
        if overlapping_requests.exists():
            raise ValidationError({
                "detail": "Cannot approve this request as the book is already borrowed for the selected period."
            })
    
        borrow_request.status = 'Approved'      # Approve the borrow request
        borrow_request.save()
        message = (
            f"Your request for the book '{borrow_request.book.title}' is approved "
        )
        return Response({'message':message}, status=status.HTTP_200_OK)
    

    '''Here deneid borrow request'''
    @action(detail=True, methods=['post'], url_path='deny')
    def deny(self, request, pk=None):
        borrow_request = self.get_object()
        borrow_request.status = 'Denied'
        borrow_request.save()
        message = (
            f"Your request for the book '{borrow_request.book.title}' is Denied "
        )
        return Response({'message':message}, status=status.HTTP_200_OK)
    

'''Here view for borrow history of users'''
    
class UserBorrowHistoryView(APIView):
    permission_classes = [IsAuthenticatedUser]

    def get(self, request):
        borrow_requests = BorrowRequest.objects.filter(user=request.user)
        serializer = BorrowRequestSerializer(borrow_requests, many=True)
        return Response(serializer.data)


'''Here view for downloading borrow histoy of user'''
class DownloadBorrowHistory(APIView):
    permission_classes = [IsAuthenticatedUser]

    def get(self, request):
        borrow_requests = BorrowRequest.objects.filter(user=request.user)  # Fetch borrow requests for the authenticated user
        response = HttpResponse(content_type='')
        response['Content-Disposition'] = 'attachment; filename="borrow_history.csv"'
        writer = csv.writer(response)   # Create a CSV writer object
        writer.writerow(['Book Title', 'Date From', 'Date To', 'Status'])     # Write header row to CSV
        # Loop through the borrow requests and write each row to the CSV file
        for borrow_request in borrow_requests:                           
            writer.writerow([borrow_request.book.title, borrow_request.date_from, borrow_request.date_to, borrow_request.status])

        return response


'''Here borrow request view for librarian to get list of borrow requests'''
class BorrowRequestView(APIView):
    queryset = BorrowRequest.objects.all()  # Fetch all borrow requests
    serializer_class = BorrowRequestSerializer
    permission_classes = [IsAuthenticatedUser, IsLibrarian]  # Restrict access to authenticated librarians

    def get_queryset(self):
       return BorrowRequest.objects.all().order_by('-date_from')  # Latest requests first



