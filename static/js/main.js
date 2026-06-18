// ============================================
// MAIN.JS - Monochrome Affiliate Theme
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('Monochrome theme initialized');

    // ========== THEME TOGGLE (Dark/Light) ==========
    const themeToggle = document.getElementById('themeToggleBtn');
    const body = document.body;

    function setTheme(theme) {
        if (theme === 'dark') {
            body.classList.remove('light');
            body.classList.add('dark');
            localStorage.setItem('theme', 'dark');
            if (themeToggle) {
                themeToggle.innerHTML = '<i class="fas fa-sun"></i> <span>Light</span>';
            }
            const metaThemeColor = document.querySelector('meta[name="theme-color"]');
            if (metaThemeColor) {
                metaThemeColor.setAttribute('content', '#0a0a0f');
            }
        } else {
            body.classList.remove('dark');
            body.classList.add('light');
            localStorage.setItem('theme', 'light');
            if (themeToggle) {
                themeToggle.innerHTML = '<i class="fas fa-moon"></i> <span>Dark</span>';
            }
            const metaThemeColor = document.querySelector('meta[name="theme-color"]');
            if (metaThemeColor) {
                metaThemeColor.setAttribute('content', '#ffffff');
            }
        }
    }

    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            var newTheme = body.classList.contains('light') ? 'dark' : 'light';
            setTheme(newTheme);
        });
    }

    var savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);

    // ========== AFFILIATE LINK CLICK TRACKING ==========
    var affiliateBtns = document.querySelectorAll('.affiliate-btn, .aff-link-h, .btn-primary');
    affiliateBtns.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            var link = btn.closest('a');
            if (link && link.href && link.href !== '#' && link.href !== 'javascript:void(0)') {
                e.preventDefault();
                
                var productId = link.getAttribute('data-product-id');
                if (!productId) {
                    var parts = link.href.split('/product/');
                    productId = parts.length > 1 ? parts.pop() : link.href.split('/').pop();
                }
                
                fetch('/api/click/' + productId, { 
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(function(response) {
                    return response.json();
                })
                .then(function(data) {
                    if (data.success) {
                        window.open(data.affiliate_link || link.href, '_blank');
                    } else {
                        window.open(link.href, '_blank');
                    }
                })
                .catch(function(error) {
                    console.error('Tracking error:', error);
                    window.open(link.href, '_blank');
                });
            } else if (link && (link.href === '#' || link.href === 'javascript:void(0)')) {
                e.preventDefault();
                console.log('Placeholder link - add proper URL');
            }
        });
    });

    // ========== SCROLL ANIMATIONS ==========
    var observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    var observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    var elementsToAnimate = document.querySelectorAll('.product-card, .category-card, .blog-card, .blog-card-h, .product-card-h, .review-card');
    elementsToAnimate.forEach(function(el) {
        if (el) {
            el.style.opacity = '0';
            el.style.transform = 'translateY(20px)';
            el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            observer.observe(el);
        }
    });

    // ========== SMOOTH SCROLL FOR ANCHOR LINKS ==========
    var anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            var targetId = this.getAttribute('href');
            if (targetId && targetId !== '#') {
                var target = document.querySelector(targetId);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });

    // ========== SEARCH FUNCTIONALITY ==========
    var searchInput = document.querySelector('.search-input');
    if (searchInput) {
        var searchForm = searchInput.closest('form');
        if (searchForm) {
            searchForm.addEventListener('submit', function(e) {
                var query = searchInput.value;
                if (!query.trim()) {
                    e.preventDefault();
                    alert('Please enter a search term');
                }
            });
        }
        
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                var query = this.value;
                if (query.trim()) {
                    window.location.href = '/search?q=' + encodeURIComponent(query.trim());
                } else {
                    e.preventDefault();
                    alert('Please enter a search term');
                }
            }
        });
    }

    // ========== HELPFUL REVIEW BUTTONS ==========
    var helpfulBtns = document.querySelectorAll('.helpful-btn');
    helpfulBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            var reviewId = this.getAttribute('data-id');
            if (reviewId) {
                fetch('/api/review/helpful/' + reviewId, { 
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(function(response) {
                    return response.json();
                })
                .then(function(data) {
                    if (data.success) {
                        btn.innerHTML = '<i class="fas fa-thumbs-up"></i> Helpful (' + data.count + ')';
                    }
                })
                .catch(function(error) {
                    console.error('Error:', error);
                });
            }
        });
    });

    // ========== FLASH MESSAGES AUTO-HIDE ==========
    var alerts = document.querySelectorAll('.alert');
    if (alerts.length > 0) {
        setTimeout(function() {
            alerts.forEach(function(alert) {
                alert.style.transition = 'opacity 0.5s';
                alert.style.opacity = '0';
                setTimeout(function() {
                    if (alert.parentNode) {
                        alert.remove();
                    }
                }, 500);
            });
        }, 5000);
    }

    // ========== PRODUCT PRICE FORMATTING ==========
    var prices = document.querySelectorAll('.product-price, .price-h');
    prices.forEach(function(price) {
        var value = price.innerText;
        if (value && !value.includes('$')) {
            var num = parseFloat(value);
            if (!isNaN(num)) {
                price.innerText = '$' + num.toFixed(2);
            }
        }
    });

    // ========== ADD HOVER EFFECT FOR CARDS ==========
    var cards = document.querySelectorAll('.product-card, .category-card, .blog-card');
    cards.forEach(function(card) {
        card.addEventListener('mouseenter', function() {
            this.style.transition = 'all 0.3s ease';
        });
    });

    // ========== LAZY LOADING FOR IMAGES ==========
    var lazyImages = document.querySelectorAll('img[data-src]');
    if ('IntersectionObserver' in window) {
        var imageObserver = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    var img = entry.target;
                    var src = img.getAttribute('data-src');
                    if (src) {
                        img.src = src;
                        img.removeAttribute('data-src');
                    }
                    img.classList.add('loaded');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        lazyImages.forEach(function(img) {
            imageObserver.observe(img);
        });
    } else {
        lazyImages.forEach(function(img) {
            var src = img.getAttribute('data-src');
            if (src) {
                img.src = src;
            }
        });
    }

    // ========== BACK TO TOP BUTTON ==========
    const backToTop = document.createElement('div');
    backToTop.className = 'back-to-top';
    backToTop.innerHTML = '<i class="fas fa-chevron-up"></i>';
    document.body.appendChild(backToTop);
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            backToTop.classList.add('show');
        } else {
            backToTop.classList.remove('show');
        }
    });
    
    backToTop.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // ========== GO BACK FUNCTION (Global) ==========
    window.goBack = function() {
        if (document.referrer && document.referrer.indexOf(window.location.hostname) !== -1) {
            window.history.back();
        } else {
            window.location.href = '/';
        }
    };
});

console.log('✅ main.js loaded successfully - Monochrome theme ready');


