from django.contrib import admin



from admin_utils import register_all_models

register_all_models('users')  
register_all_models('cars')
register_all_models('bookings')
register_all_models('payments')
register_all_models('stock_management')
register_all_models('homepage')