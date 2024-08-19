function confirmCancellation(event) {
    event.preventDefault();

    if (confirm('Are you sure you want to cancel this booking?')) {
        event.target.submit();
    } else {
        return false;
    }
}