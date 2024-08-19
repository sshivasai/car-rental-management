from django.shortcuts import render
from .models import ServiceLocations, Car
from stock_management.models import StockManagement
from django.utils import timezone
from django.db.models import Q

def fetch_servicelocations():
    locations = ServiceLocations.objects.values_list('location_city', flat=True).distinct()
    return list(locations)

def cars_list(request):
    location = request.GET.get('location')
    
    max_price = request.GET.get('max_price')
    sort_order = request.GET.get('sort')
    availability = request.GET.get('availability')
    pickup_date = request.GET.get('pickup_date')

    cars = Car.objects.all()

    

    if max_price:
        cars = cars.filter(price_per_hour__lte=max_price)

    today = timezone.now()

    stock_management = StockManagement.objects.filter(car__in=cars).select_related('car', 'current_location')

    if availability:
        if availability == 'available':
            stock_management = stock_management.filter(quantity__gt=0, latest_available_date__lte=today)
        elif availability == 'unavailable':
            stock_management = stock_management.filter(quantity=0)
        elif availability == 'available_later':
            stock_management = stock_management.filter(quantity__gt=0, latest_available_date__gt=today)

    if pickup_date:
        pickup_date = timezone.datetime.strptime(pickup_date, '%Y-%m-%d').date()
        stock_management = stock_management.filter(Q(latest_available_date__lte=pickup_date) & ~Q(quantity=0))
    
    if location:
        stock_management = stock_management.filter(current_location__location_city=location)
    

    # Applying sorting after filtering
    if sort_order == 'price_asc':
        stock_management = stock_management.order_by('car__price_per_hour')
    elif sort_order == 'price_desc':
        stock_management = stock_management.order_by('-car__price_per_hour')

    cars_with_stock = {}

    for stock in stock_management:
        car_id = stock.car.id
        if car_id not in cars_with_stock:
            cars_with_stock[car_id] = {
                'car': stock.car,
                'stocks': []
            }
        cars_with_stock[car_id]['stocks'].append({
            'location': stock.current_location.location_city,
            'quantity': stock.quantity,
            'latest_available_date': stock.latest_available_date,
            'availability_status': stock.availability_status(),
            'stock_id': stock.id
        })

    locations = fetch_servicelocations()
    context = {
        'cars_with_stock': list(cars_with_stock.values()),  
        'locations': locations,
    }

  
    return render(request, 'cars/cars.html', context)
