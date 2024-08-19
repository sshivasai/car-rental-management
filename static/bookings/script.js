document.addEventListener('DOMContentLoaded', function() {
    const findDealsBtn = document.getElementById('findDealsBtn');
    const couponPopup = document.getElementById('couponPopup');
    const closeCouponPopupBtn = couponPopup.querySelector('.close');
    const couponsList = document.getElementById('couponsList');

    findDealsBtn.addEventListener('click', function() {
        fetch('/booking/fetch_coupons/')
            .then(response => response.json())
            .then(data => {
                couponsList.innerHTML = '';  
                if (data.coupons && data.coupons.length > 0) {
                    data.coupons.forEach(coupon => {
                        const couponItem = document.createElement('div');
                        couponItem.classList.add('coupon-item');

                        couponItem.innerHTML = `
                            <p>Coupon Code: ${coupon.code}</p>
                            <p>Discount: ${coupon.discount_percentage}%</p>
                            <p>Description: ${coupon.description}</p>
                            <p>Date Valid: ${coupon.valid_until}</p>
                            <button class="select-coupon-btn">Select</button>
                        `;

                        couponItem.querySelector('.select-coupon-btn').addEventListener('click', function() {
                            document.getElementById('id_coupon_code').value = coupon.code;
                            couponPopup.style.display = 'none';
                        });

                        couponsList.appendChild(couponItem);
                    });
                } else {
                    const noCouponsMessage = document.createElement('p');
                    noCouponsMessage.textContent = 'No coupons available.';
                    couponsList.appendChild(noCouponsMessage);
                }

                couponPopup.style.display = 'block'; 
            })
            .catch(error => {
                console.error('Error fetching coupons:', error);
            });
    });

    closeCouponPopupBtn.addEventListener('click', function() {
        couponPopup.style.display = 'none';
    });

    // Close popup when clicking any where
    window.addEventListener('click', function(event) {
        if (event.target == couponPopup) {
            couponPopup.style.display = 'none';
        }
    });
});