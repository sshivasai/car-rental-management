from django.db import models
from django.utils import timezone
from cars.models import Car, ServiceLocations

class StockManagement(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    current_location = models.ForeignKey(ServiceLocations, on_delete=models.CASCADE)
    latest_available_date = models.DateTimeField()
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Stock {self.id} for Car {self.car.id}"

    def availability_status(self):
        if self.quantity <= 0:
            return 'Unavailable'
        elif self.latest_available_date <= timezone.now():
            return 'Available Now'
        else:
            return self.latest_available_date

class Coupons(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    max_limit = models.DecimalField(max_digits=10, decimal_places=2)
    min_price = models.DecimalField(max_digits=10, decimal_places=2)
    min_hours = models.IntegerField()
    valid_until = models.DateTimeField()

    def is_valid(self):
        return self.valid_until >= timezone.now()

    def __str__(self):
        return self.code