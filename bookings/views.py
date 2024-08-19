from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import BookingForm
from .models import Booking
from stock_management.models import Coupons, StockManagement
from cars.models import ServiceLocations
from django.utils import timezone
from decimal import Decimal
from django.conf import settings
import stripe
import datetime
from django.urls import reverse
from cars.models import Car
from stock_management.models import ServiceLocations, StockManagement, Coupons
import logging
from cars.views import cars_list
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def booking_view(request, stock_id):
    
    car_stock = get_object_or_404(StockManagement, pk=stock_id)
    
    # Assinging Default pickup location to the location of the car
    pickup_location = car_stock.current_location
    
    # Seting default pickup and drop-off times for the form
    default_pickup_time = datetime.time(hour=10, minute=0)  # 10:00 AM
    default_dropoff_time = datetime.time(hour=11, minute=0)  # 11:00 AM

    # Calculating default pickup and drop-off dates based on current time
    now = timezone.now()
    if now.hour >= 10:
        today = datetime.date.today()
        def_pickupday = today + datetime.timedelta(days=1)
        def_dropoffday = today + datetime.timedelta(days=2)
    else:
        today = datetime.date.today()
        def_pickupday = today
        def_dropoffday = today + datetime.timedelta(days=1)

    form = BookingForm(request.POST or None, initial={
        'pickup_location': pickup_location,
        'pickup_date': def_pickupday,
        'pickup_time': default_pickup_time,
        'dropoff_date': def_dropoffday,
        'dropoff_time': default_dropoff_time,
    })
    pricing_details = {}

    if request.method == 'POST' and form.is_valid():
        pickup_date = form.cleaned_data['pickup_date']
        dropoff_date = form.cleaned_data['dropoff_date']
        pickup_time = form.cleaned_data['pickup_time']
        dropoff_time = form.cleaned_data['dropoff_time']
        coupon_code = form.cleaned_data['coupon_code']
        
        pickup_datetime = datetime.datetime.combine(pickup_date, pickup_time)
        dropoff_datetime = datetime.datetime.combine(dropoff_date, dropoff_time)

        # Checking if pickup date is valid (not older than the latest available date)
        if pickup_date < car_stock.latest_available_date.date():
            
                messages.error(request, "Pickup date cannot be older than the latest available date.")
                return render(request, 'bookings/booking.html', {
                    'form': form,
                    'car_data': car_stock,
                    'pricing_details': pricing_details,
                })
        if pickup_date == car_stock.latest_available_date.date():
            if pickup_time < car_stock.latest_available_date.time():
                messages.error(request, "Pickup time cannot be older than the latest available time.")
                return render(request, 'bookings/booking.html', {
                    'form': form,
                    'car_data': car_stock,
                    'pricing_details': pricing_details,
                })
        

        # Calculating booking duration in hours
        pickup_datetime = datetime.datetime.combine(pickup_date, pickup_time)
        dropoff_datetime = datetime.datetime.combine(dropoff_date, dropoff_time)
        booking_duration = (dropoff_datetime - pickup_datetime).total_seconds() / 3600

        # price_per_hour to Decimal
        price_per_hour = Decimal(str(car_stock.car.price_per_hour))

        # total price
        total_price = Decimal(booking_duration) * price_per_hour

        #discount and coupon info
        discount_amount = Decimal('0.00')
        coupon_info = None

        # Validating coupon
        if coupon_code:
            try:
                coupon = Coupons.objects.get(code=coupon_code, valid_until__gte=timezone.now().date())
                if total_price >= coupon.min_price and booking_duration >= coupon.min_hours:
                    if coupon.discount_percentage:
                        discount_amount = total_price * (coupon.discount_percentage / Decimal('100.0'))
                        if discount_amount > coupon.max_limit:
                            discount_amount = coupon.max_limit
                        messages.success(request, f"Coupon applied successfully. You saved ${discount_amount:.2f}.")
                    else:
                        discount_amount = coupon.max_limit
                        messages.success(request, f"Coupon applied successfully. You saved ${discount_amount:.2f}.")
                    coupon_info = coupon
                else:
                    messages.error(request, "Coupon does not meet the requirements.")
            except Coupons.DoesNotExist:
                messages.error(request, "Invalid coupon code.")

        #final price and taxes
        final_price = total_price - discount_amount
        tax_amount = final_price * Decimal('0.18')
        final_price_with_tax = final_price + tax_amount

        final_price = round(final_price, 2)
        tax_amount = round(tax_amount, 2)
        final_price_with_tax = round(final_price_with_tax, 2)
        total_price = round(total_price,2)
        final_price_with_tax = round(final_price_with_tax,2)
        

        #pricing details
        pricing_details = {
            'total_price': total_price,
            'discount_amount': discount_amount,
            'final_price': final_price,
            'tax_amount': tax_amount,
            'final_price_with_tax': final_price_with_tax,
            'coupon_info': coupon_info,
            'booking_duration': booking_duration,
        }

        # Saving booking details in session
        request.session['booking_details'] = {
            'car_id': car_stock.car.id,
            'pickup_location_id': pickup_location.id,
            'dropoff_location_id': form.cleaned_data['dropoff_location'].id,
            'pickup_date': pickup_date.strftime('%Y-%m-%d'),
            'pickup_time': pickup_time.strftime('%H:%M:%S'),
            'dropoff_date': dropoff_date.strftime('%Y-%m-%d'),
            'dropoff_time': dropoff_time.strftime('%H:%M:%S'),
            'total_price': str(total_price),
            'discount_amount': str(discount_amount),
            'final_price_with_tax': str(final_price_with_tax),
            'coupon_code': coupon_code,
        }

        #booking page with form and pricing details
        return render(request, 'bookings/booking.html', {
            'form': form,
            'car_data': car_stock,
            'pricing_details': pricing_details,
        })
    

    # initial booking page with form
    return render(request, 'bookings/booking.html', {
        'form': form,
        'car_data': car_stock,
        'pricing_details': pricing_details,
    })


@login_required
def confirm_booking(request):
    if request.method == 'POST':
        stock_id = request.POST.get('stock_id')
        pickup_location = request.POST.get('pickup_location')
        dropoff_location = request.POST.get('dropoff_location')
        pickup_date = request.POST.get('pickup_date')
        pickup_time = request.POST.get('pickup_time')
        dropoff_date = request.POST.get('dropoff_date')
        dropoff_time = request.POST.get('dropoff_time')
        total_price = request.POST.get('total_price')
        discount_amount = request.POST.get('discount_amount')
        final_price = request.POST.get('final_price')
        tax_amount = request.POST.get('tax_amount')
        final_price_with_tax = request.POST.get('final_price_with_tax')
        coupon_code = request.POST.get('coupon_code')
        stock = get_object_or_404(StockManagement, pk=stock_id)
        car = stock.car


        booking_details = {
            'stock_id': stock_id,
            'coupon_code':coupon_code,
            'car_id': car.id,
            'car_image':car.car_image,
            'car_name': f"{car.make} {car.model}",
            'pickup_location': pickup_location,
            'dropoff_location': dropoff_location,
            'pickup_date': pickup_date,
            'pickup_time': pickup_time,
            'dropoff_date': dropoff_date,
            'dropoff_time': dropoff_time,
            'total_price': total_price,
            'discount_amount': discount_amount,
            'final_price': final_price,
            'tax_amount': tax_amount,
            'final_price_with_tax': final_price_with_tax,
        }

        

        request.session['booking_details'] = booking_details

        # JSON response with booking details
        return JsonResponse({'booking_details': booking_details})
    
    elif request.method == 'GET':
        booking_details = request.session.get('booking_details')
        if not booking_details:
            messages.error(request, "Booking can't be confirmed right now. Please try again later.")
            return redirect('cars_list')
        else:
            return render(request, 'bookings/booking.html', {'booking_details': booking_details})
    


from django.http import JsonResponse
def fetch_coupons(request):
    
    coupons = Coupons.objects.filter(valid_until__gte=timezone.now())
    coupons_data = [
        {
            'code': coupon.code,
            'discount_percentage': coupon.discount_percentage,
            'description': f"Applicable on all bookings above {coupon.min_hours} hours and minimum booking values should be ${coupon.min_price} USD. Max Discount of ${coupon.max_limit} USD.",
            'min_hours': coupon.min_hours,
            'min_price': coupon.min_price,
            'max_limit': coupon.max_limit,
            'valid_until': coupon.valid_until.strftime('%Y-%m-%d'),
        } for coupon in coupons
    ]
    return JsonResponse({'coupons': coupons_data})



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Booking, StockManagement

from django.shortcuts import render
from .models import Booking

def orders_list(request):
    bookings = Booking.objects.filter(user=request.user)

    # filter and sorting parameters
    status = request.GET.get('status')
    sort_by = request.GET.get('sort_by')

    # Applying status filter
    if status:
        bookings = bookings.filter(booking_status=status)

    # Applying sorting to the bookings
    if sort_by == 'booking_date_asc':
        bookings = bookings.order_by('booking_time')
    elif sort_by == 'booking_date_desc':
        bookings = bookings.order_by('-booking_time')
    if sort_by == 'pickup_date_asc':
        bookings = bookings.order_by('pickup_datetime')
    elif sort_by == 'pickup_date_desc':
        bookings = bookings.order_by('-pickup_datetime')
    elif sort_by == 'dropoff_date_asc':
        bookings = bookings.order_by('dropoff_datetime')
    elif sort_by == 'dropoff_date_desc':
        bookings = bookings.order_by('-dropoff_datetime')
    elif sort_by == 'price_asc':
        bookings = bookings.order_by('final_price')
    elif sort_by == 'price_desc':
        bookings = bookings.order_by('-final_price')
    elif sort_by == 'status':
        bookings = bookings.order_by('booking_status')

    return render(request, 'bookings/orders.html', {'bookings': bookings})


def cancel_booking(request, booking_id):
    print("cancel")
    booking = get_object_or_404(Booking, pk=booking_id)
    
    if booking.pickup_datetime <= timezone.now():
        messages.error(request, 'Cannot cancel after pickup time.')
    else:

        booking.booking_status = False
        booking.save()

        stock = booking.stock_id


        if stock.current_location == booking.dropoff_location and stock.latest_available_date == booking.dropoff_datetime:
            stock.latest_available_date = timezone.now()
            stock.current_location = booking.pickup_location  
            stock.save()
        else:
            StockManagement.objects.create(
                car=booking.car,
                quantity=1,
                current_location=booking.pickup_location,
                latest_available_date=timezone.now()
            )

        booking.cancellation_time = timezone.now()
        booking.save()
        # Updating payment status
        booking.payment.status = 'Refund Initiated'
        booking.payment.save()
        #sending email
        send_cancellation_email(request.user.email, booking,request.user)

        messages.success(request, 'Booking cancelled successfully.')

    return redirect('orders_list')


def send_cancellation_email(email, booking,user):
    subject = 'Booking Cancellation - Direct Rental Limited'
    context = {
        'booking': booking,
        'company_name': 'Direct Rental Limited',
        'user':user
    }
    html_message = render_to_string('bookings/booking_cancellation_email.html', context)
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, plain_message, from_email, [email], html_message=html_message)