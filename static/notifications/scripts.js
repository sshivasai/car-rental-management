document.addEventListener('DOMContentLoaded', function() {
    const notifications = document.querySelectorAll('.notification');

    notifications.forEach(notification => {
        
        const closeBtn = notification.querySelector('.close-btn');
        closeBtn.addEventListener('click', () => {
            closeNotification(notification);
        });

    
        setTimeout(() => {
            closeNotification(notification);
        }, 5000);
    });

    function closeNotification(notification) {
        notification.style.animation = 'slideOut 0.5s ease-out forwards';
        setTimeout(() => {
            notification.remove();
        }, 500);
    }
});
