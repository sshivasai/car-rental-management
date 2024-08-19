from django.db import models
from cars.models import Car
from users.models import User
from payments.models import Payment
from stock_management.models import StockManagement, Coupons
from cars.models import ServiceLocations  

class Booking(models.Model):
    booking_id = models.AutoField(primary_key=True)
    pickup_location = models.ForeignKey(ServiceLocations, on_delete=models.CASCADE, related_name='pickup_bookings')
    dropoff_location = models.ForeignKey(ServiceLocations, on_delete=models.CASCADE, related_name='dropoff_bookings')
    pickup_datetime = models.DateTimeField()
    dropoff_datetime = models.DateTimeField()
    actual_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    taxes = models.DecimalField(max_digits=10, decimal_places=2 )
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupons, on_delete=models.SET_NULL, null=True, blank=True) 
    stock_id = models.ForeignKey(StockManagement, on_delete=models.CASCADE)
    booking_status = models.BooleanField(default=True)
    booking_time = models.DateTimeField(auto_now=True)
    cancellation_time = models.DateTimeField(null=True)

    def save(self, *args, **kwargs):
        if not self.taxes or not self.final_price:
            self.taxes = (self.actual_price - self.discount) * 18 / 100
            self.final_price = self.actual_price + self.taxes - self.discount
        super(Booking, self).save(*args, **kwargs)

    def __str__(self):
        return f"Booking {self.booking_id} by {self.user.email}"