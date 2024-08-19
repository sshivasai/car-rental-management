from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
import stripe
from bookings.models import Booking
from payments.models import Payment
from stock_management.models import StockManagement, Coupons
from cars.models import Car, ServiceLocations
from users.models import User
stripe.api_key = settings.STRIPE_SECRET_KEY
from datetime import datetime

from datetime import datetime

def parse_date(date_string):
    date_string = date_string.strip()
    month_abbreviation = date_string.split()[0][:3]
    formatted_date_string = date_string.replace(date_string.split()[0], month_abbreviation)
    formats_to_try = ['%b %d, %Y']
    for format_str in formats_to_try:
        try:
            return datetime.strptime(formatted_date_string, format_str).date()
        except ValueError:
            continue
    raise ValueError(f"Could not parse date: {date_string}")

@login_required
def create_checkout_session(request):
    booking_details = request.session.get('booking_details')

    request.session['booking_details'] = booking_details

    if not booking_details:
        messages.error(request, "No booking details found.")
        return redirect('cars_list')

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': (
                                f"{booking_details['car_name']} - "
                                f"Rental: {booking_details['pickup_location']} to {booking_details['dropoff_location']}"
                            ),
                            'description': (
                                f"Rental Period: {booking_details['pickup_date']} to {booking_details['dropoff_date']}\n"
                                f"Pickup: {booking_details['pickup_location']} on {booking_details['pickup_date']}\n"
                                f"Dropoff: {booking_details['dropoff_location']} on {booking_details['dropoff_date']} at {booking_details['dropoff_time']}\n"
                                f"Total: ${booking_details['final_price_with_tax']}\n"
                            ),
                    },
                    'unit_amount': int(float(booking_details['final_price_with_tax']) * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('payment_success')) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri(reverse('confirm_booking')),
        )
        return redirect(checkout_session.url)
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('confirm_booking')

@login_required
def payment_success(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        messages.error(request, "No session ID found.")
        return redirect('cars_list')

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        payment_intent_id = session.payment_intent
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

        payment = Payment.objects.filter(payment_reference = payment_intent_id).first()
        # Checking if the booking already exists 
        booking = Booking.objects.filter(payment=payment).first()
        if booking:
            receipt_url = stripe.Charge.retrieve(payment_intent.latest_charge).receipt_url
            return render(request, 'payments/payment_success.html', {
                'booking': booking,
                'payment': booking.payment,
                'receipt_url': receipt_url
            })

        # Retrieving necessary data from booking_details
        booking_details = request.session.pop('booking_details', None)
        if not booking_details:
            messages.error(request, "No booking details found.")
            return redirect('cars_list')

        car = get_object_or_404(Car, id=booking_details['car_id'])
        user = request.user
        pickup_location = get_object_or_404(ServiceLocations, location_city=booking_details['pickup_location'])
        dropoff_location = get_object_or_404(ServiceLocations, location_city=booking_details['dropoff_location'])

        # Calculating taxes and final_price if not present
        if 'tax_amount' not in booking_details or 'final_price_with_tax' not in booking_details:
            booking_details['tax_amount'] = (booking_details['total_price'] - booking_details['discount_amount']) * 0.18
            booking_details['final_price_with_tax'] = booking_details['total_price'] + booking_details['tax_amount'] - booking_details['discount_amount']

        charge = stripe.Charge.retrieve(payment_intent.latest_charge)
        receipt_url = charge.receipt_url

        coupon = get_object_or_404(Coupons, code=booking_details['coupon_code']) if booking_details['coupon_code'] != "NULL" else None

        payment = Payment.objects.create(
            payment_reference=payment_intent_id,
            billing_name=charge.billing_details.name if charge.billing_details.name else "N/A",
            billing_address=charge.billing_details.address.line1 if charge.billing_details.address else "N/A",
            zip_code=charge.billing_details.address.postal_code if charge.billing_details.address else "N/A",
            amount=float(payment_intent.amount / 100),  # Amount in stripe is in cents, convert to dollars
            status='Success',
            user=user,
            card_last4=charge.payment_method_details.card.last4,
            card_type=charge.payment_method_details.card.brand.capitalize()
        )

        stock = StockManagement.objects.get(id=booking_details['stock_id'])

        
        pickup_date = parse_date(booking_details['pickup_date'])
        dropoff_date = parse_date(booking_details['dropoff_date'])

        if booking_details['pickup_time'] == 'noon':
            booking_details['pickup_time'] = '12 p.m.'
        elif booking_details['pickup_time'] == 'midnight':
            booking_details['pickup_time'] = '12 a.m.'
        if booking_details['dropoff_time'] == 'noon':
            booking_details['dropoff_time'] = '12 p.m.'
        elif booking_details['dropoff_time'] == 'midnight':
            booking_details['dropoff_time'] = '12 a.m.'

        
        pickup_time_str = booking_details['pickup_time'].replace('.', '')
        dropoff_time_str = booking_details['dropoff_time'].replace('.', '')

        try:
            pickup_time = datetime.strptime(pickup_time_str, '%I %p').time()
        except:
            pickup_time = datetime.strptime(pickup_time_str, '%I:%M %p').time()
        try:
            dropoff_time = datetime.strptime(dropoff_time_str, '%I %p').time()
        except:
            dropoff_time = datetime.strptime(dropoff_time_str, '%I:%M %p').time
        
        pickup_datetime = datetime.combine(pickup_date, pickup_time)
        dropoff_datetime = datetime.combine(dropoff_date, dropoff_time)

        booking = Booking.objects.create(
            car=car,
            user=user,
            pickup_location=pickup_location,
            dropoff_location=dropoff_location,
            pickup_datetime=pickup_datetime,
            dropoff_datetime=dropoff_datetime,
            actual_price=float(booking_details['total_price']),
            discount=float(booking_details['discount_amount']),
            taxes=booking_details['tax_amount'],
            final_price=booking_details['final_price_with_tax'],
            payment=payment,
            coupon=coupon,
            stock_id=stock,
            booking_status = True #means Success False means Cancelled
        )

        if stock.quantity > 1:
            stock.quantity -= 1
            stock.save()
            StockManagement.objects.create(
                car=car,
                current_location=dropoff_location,
                latest_available_date=dropoff_datetime,
                quantity=1
            )
        else:
            stock.latest_available_date = dropoff_datetime
            stock.current_location = dropoff_location
            stock.save()

        try:
            send_booking_email(request.user.email, booking, payment, receipt_url)
        except e:
            print(e)

        return render(request, 'payments/payment_success.html', {
            'booking': booking,
            'payment': payment,
            'receipt_url': receipt_url
        })

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('confirm_booking')


from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_booking_email(email, booking, payment, receipt_url):
    subject = 'Booking Confirmation - Direct Rental Limited'
    context = {
        'booking': booking,
        'payment': payment,
        'receipt_url': receipt_url,
        'company_name': 'Direct Rental Limited'
    }
    html_message = render_to_string('payments/booking_confirmation.html', context)
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, plain_message, from_email, [email], html_message=html_message)