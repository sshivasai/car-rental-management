# car rental management
 
Commands to Run:

pip install -r requirements.txt


django-admin startproject car_rental_project

cd car_rental_project

python manage.py startapp users

python manage.py startapp cars

python manage.py startapp bookings

python manage.py startapp payments

python manage.py startapp stock_management

python manage.py makemigrations

python manage.py migrate

python manage.py createsuperuser




http://127.0.0.1:8000/admin/login/?next=/admin/

Username (leave blank to use 'sanko'): superuser
Email address: superuser@gmail.com
Password:Super@123
Password (again): Super@123
Superuser created successfully.




python manage.py runserver
