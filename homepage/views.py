from django.shortcuts import render
from cars.views import fetch_servicelocations
# Create your views here.



def home(request):
    locations = fetch_servicelocations()
    context = {
        'locations': locations
    }
    return render(request, 'homepage/home.html', context)