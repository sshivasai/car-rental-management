from django.urls import path
from .views import *

urlpatterns = [
    path('booking/book/<int:stock_id>/', booking_view, name='booking_view'),
    path('confirm-booking/', confirm_booking, name='confirm_booking'),
    path('fetch_coupons/', fetch_coupons, name='fetch_coupons'),
    path('bookings/cancel_booking/<int:booking_id>/',cancel_booking, name='cancel_booking'),
    path('orders/', orders_list, name='orders_list'),
    
]