from django.db import models

from users.models import User


class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    payment_reference = models.CharField(max_length=100) 
    billing_name = models.CharField(max_length=255)
    billing_address = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card_last4 = models.CharField(max_length=4)  
    card_type = models.CharField(max_length=20) 
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Payment {self.payment_id} for {self.user.email}"