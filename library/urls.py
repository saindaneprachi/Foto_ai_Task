# URL Configuration
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from library.views import UserViewSet, BookViewSet, BorrowRequestViewSet, BorrowRequestView
from .views import *
# from rest_framework.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'users', UserViewSet)   #users CRUD
router.register(r'books', BookViewSet)    #book CRUD
router.register(r'borrow-requests', BorrowRequestViewSet)   

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/user-borrow-history/', UserBorrowHistoryView.as_view(), name='user-borrow-history'),
    path('api/download-borrow-history/', DownloadBorrowHistory.as_view(), name='download-borrow-history'),
    # path('api/token/', ObtainTokenPairWithUsernameView.as_view(), name='token_obtain_pair'),
    path('api/borrow-requests/', BorrowRequestView.as_view(), name='borrow-requests'),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]





