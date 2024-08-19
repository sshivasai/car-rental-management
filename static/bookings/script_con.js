document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('confirmBookingForm').addEventListener('submit', function(event) {
        event.preventDefault();
    

        var formData = new FormData(this);

        // Send request to confirm_booking view
        fetch(this.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            // Extract booking details from JSON response
            var bookingDetails = data.booking_details;

            document.getElementById('popupCarImage').src = bookingDetails.car_image; 
            document.getElementById('popupCarName').innerHTML  = '<b>Car Name: </b>' + bookingDetails.car_name;
            document.getElementById('popupPickupLocation').innerHTML = '<b>Pickup Location: </b>' + bookingDetails.pickup_location;
            document.getElementById('popupDropoffLocation').innerHTML = '<b>Dropoff Location: </b>' + bookingDetails.dropoff_location;
            document.getElementById('popupPickupDate').innerHTML = '<b>Pickup Date: </b>' + bookingDetails.pickup_date;
            document.getElementById('popupPickupTime').innerHTML = '<b>Pickup Time: </b>' + bookingDetails.pickup_time;
            document.getElementById('popupDropoffDate').innerHTML = '<b>Dropoff Date: </b>' + bookingDetails.dropoff_date;
            document.getElementById('popupDropoffTime').innerHTML = '<b>Dropoff Time: </b>' + bookingDetails.dropoff_time;
            document.getElementById('popupTotalPrice').innerHTML = '<b>Total Price: </b>$' + bookingDetails.total_price;
            document.getElementById('popupDiscountAmount').innerHTML = '<b>Discount: </b>-$' + bookingDetails.discount_amount;
            document.getElementById('popupFinalPrice').innerHTML = '<b>Price After Discount: </b> $' + bookingDetails.final_price;
            document.getElementById('popupTaxAmount').innerHTML = '<b>Tax (18% GST): </b>$' + bookingDetails.tax_amount;
            document.getElementById('popupFinalPriceWithTax').innerHTML = '<b>Final Price: $' + bookingDetails.final_price_with_tax;

            // Show the popup
            document.getElementById('confirmPopup').style.display = 'block';
        })
        .catch(error => {
            console.log('Error:', error);
            
        });
    });

    // Close popup 
    document.getElementById('closePopupBtn').addEventListener('click', function() {
        document.getElementById('confirmPopup').style.display = 'none';
    });

   
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('popup_con')) {
            document.getElementById('confirmPopup').style.display = 'none';
        }
    });

    
    document.querySelector('.popup_con-content').addEventListener('click', function(event) {
        event.stopPropagation();
    });
});

// Function to get cookie to use as csrf token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}