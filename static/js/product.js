// product.js - All JavaScript for product page

// Go back function
function goBack() {
    if (document.referrer && document.referrer.indexOf(window.location.hostname) !== -1) {
        window.history.back();
    } else {
        window.location.href = '/';
    }
}

// Track affiliate click
function trackAffiliateClick(productId) {
    fetch('/api/click/' + productId, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    }).catch(err => console.log('Tracking error:', err));
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Find product ID from data attribute
    const buyButton = document.querySelector('.buy-now');
    if (buyButton) {
        const productId = buyButton.getAttribute('data-product-id');
        if (buyButton.hasAttribute('onclick')) {
            buyButton.removeAttribute('onclick');
        }
        buyButton.addEventListener('click', function(e) {
            if (productId) {
                trackAffiliateClick(productId);
            }
        });
    }
});


