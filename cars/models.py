from django.db import models

from django.db import models

class ServiceLocations(models.Model):
    location_city = models.CharField(max_length=255)
    address = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.location_city

class Car(models.Model):
    make = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    capacity = models.IntegerField()
    availability = models.BooleanField(default=True)
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    car_type = models.CharField(max_length=50)
    car_image = models.CharField(max_length=255)
    default_location = models.ForeignKey('ServiceLocations', on_delete=models.CASCADE, related_name='cars')

    def __str__(self):
        return f"{self.make} {self.model}"



