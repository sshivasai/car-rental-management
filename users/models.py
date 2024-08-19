from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, fname, lname, gender, phone, license_no, password=None, license_front_image=None, license_back_image=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not license_no:
            raise ValueError('Users must have a license number')
        if not license_front_image or not license_back_image:
            raise ValueError('Users must provide license images')
        
        user = self.model(
            email=self.normalize_email(email),
            fname=fname,
            lname=lname,
            gender=gender,
            phone=phone,
            license_no=license_no,
        )
        user.set_password(password)
        user.license_front_image = license_front_image
        user.license_back_image = license_back_image
        user.save(using=self._db)
        return user

    def create_superuser(self, email, fname, lname, gender, phone, license_no=None, password=None, license_front_image=None, license_back_image=None):
        user = self.create_user(
            email,
            fname,
            lname,
            gender,
            phone,
            license_no,
            password=password,
            license_front_image=license_front_image,
            license_back_image=license_back_image,
        )
        user.is_superuser = True
        user.is_staff = True  # Staff status is necessary for accessing admin
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True)
    fname = models.CharField(max_length=255)
    lname = models.CharField(max_length=255)
    gender = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")])
    password = models.CharField(max_length=255)
    license_no = models.CharField(max_length=50)
    license_front_image = models.ImageField(upload_to='licenses/')
    license_back_image = models.ImageField(upload_to='licenses/')
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['fname', 'lname', 'gender', 'phone', 'license_no', 'license_front_image', 'license_back_image']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser
