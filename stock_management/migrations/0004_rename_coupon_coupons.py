# Generated by Django 5.0.6 on 2024-07-10 19:21

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("stock_management", "0003_coupon_valid_until"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Coupon",
            new_name="Coupons",
        ),
    ]
