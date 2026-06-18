// ============================================
// ADMIN PANEL JAVASCRIPT
// White/Black Theme | Responsive Sidebar
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('Admin panel initialized');

    // ========== SIDEBAR TOGGLE FOR MOBILE ==========
    const sidebarToggle = document.getElementById('sidebarToggle');
    const adminSidebar = document.querySelector('.admin-sidebar');
    
    if (sidebarToggle && adminSidebar) {
        sidebarToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            adminSidebar.classList.toggle('open');
        });
        
        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function(e) {
            if (window.innerWidth <= 768) {
                if (adminSidebar && !adminSidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                    adminSidebar.classList.remove('open');
                }
            }
        });
    }

    // ========== ACTIVE NAVIGATION HIGHLIGHT ==========
    const currentPath = window.location.pathname;
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(function(item) {
        const href = item.getAttribute('href');
        if (href === currentPath) {
            item.classList.add('active');
        } else if (href !== '/' && currentPath.startsWith(href)) {
            item.classList.add('active');
        } else if (href === '/' && currentPath === '/') {
            item.classList.add('active');
        }
    });

    // ========== AUTO-HIDE FLASH MESSAGES ==========
    const alerts = document.querySelectorAll('.alert');
    if (alerts.length > 0) {
        setTimeout(function() {
            alerts.forEach(function(alert) {
                alert.style.transition = 'opacity 0.5s ease';
                alert.style.opacity = '0';
                setTimeout(function() {
                    if (alert.parentNode) {
                        alert.remove();
                    }
                }, 500);
            });
        }, 5000);
    }

    // ========== CONFIRM DELETE ACTIONS ==========
    const deleteButtons = document.querySelectorAll('.btn-delete, .delete-btn');
    deleteButtons.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            const itemName = this.getAttribute('data-name') || 'this item';
            if (!confirm('Are you sure you want to delete ' + itemName + '? This action cannot be undone.')) {
                e.preventDefault();
                return false;
            }
        });
    });

    // ========== TABLE ROW CLICK (optional) ==========
    const clickableRows = document.querySelectorAll('.clickable-row');
    clickableRows.forEach(function(row) {
        row.addEventListener('click', function() {
            const link = this.getAttribute('data-href');
            if (link) {
                window.location.href = link;
            }
        });
    });

    // ========== SEARCH FILTER FOR TABLES ==========
    const searchInput = document.getElementById('tableSearch');
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            const searchTerm = this.value.toLowerCase();
            const tableRows = document.querySelectorAll('.admin-table-full tbody tr');
            
            tableRows.forEach(function(row) {
                const text = row.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }

    // ========== TOOLTIP INITIALIZATION ==========
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(function(el) {
        el.addEventListener('mouseenter', function(e) {
            const tooltipText = this.getAttribute('data-tooltip');
            const tooltip = document.createElement('div');
            tooltip.className = 'custom-tooltip';
            tooltip.textContent = tooltipText;
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.top = (rect.top - tooltip.offsetHeight - 5) + 'px';
            tooltip.style.left = (rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2)) + 'px';
            
            this.addEventListener('mouseleave', function() {
                tooltip.remove();
            }, { once: true });
        });
    });

    // ========== FORM VALIDATION ==========
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // ========== PRICE FORMATTING ==========
    const priceInputs = document.querySelectorAll('.price-input');
    priceInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            let value = parseFloat(this.value);
            if (!isNaN(value)) {
                this.value = value.toFixed(2);
            }
        });
    });

    // ========== SLUG AUTO-GENERATION ==========
    const nameInput = document.getElementById('productName');
    const slugInput = document.getElementById('productSlug');
    
    if (nameInput && slugInput) {
        nameInput.addEventListener('input', function() {
            if (!slugInput.value || slugInput.value === '') {
                let slug = this.value.toLowerCase()
                    .replace(/[^a-z0-9]+/g, '-')
                    .replace(/^-|-$/g, '');
                slugInput.value = slug;
            }
        });
    }

    // ========== CONFIRM BULK ACTIONS ==========
    const bulkActionBtn = document.getElementById('bulkActionBtn');
    if (bulkActionBtn) {
        bulkActionBtn.addEventListener('click', function() {
            const selected = document.querySelectorAll('.select-checkbox:checked');
            if (selected.length === 0) {
                alert('Please select at least one item');
                return;
            }
            if (confirm('Are you sure you want to perform this action on ' + selected.length + ' items?')) {
                document.getElementById('bulkActionForm').submit();
            }
        });
    }

    // ========== SELECT ALL CHECKBOXES ==========
    const selectAllCheckbox = document.getElementById('selectAll');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('.select-checkbox');
            checkboxes.forEach(function(cb) {
                cb.checked = selectAllCheckbox.checked;
            });
        });
    }
});

// ========== ADD CUSTOM CSS FOR TOOLTIPS ==========
const tooltipStyle = document.createElement('style');
tooltipStyle.textContent = `
    .custom-tooltip {
        position: fixed;
        background: #1a1a1a;
        color: white;
        padding: 5px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        z-index: 1000;
        white-space: nowrap;
        pointer-events: none;
    }
    
    .clickable-row {
        cursor: pointer;
    }
    
    .was-validated .form-control:invalid {
        border-color: #f44336;
    }
    
    .select-checkbox {
        cursor: pointer;
    }
`;
document.head.appendChild(tooltipStyle);

// ========== TOAST NOTIFICATION FUNCTION ==========
function showToast(message, type) {
    const toast = document.createElement('div');
    toast.className = 'toast-notification toast-' + (type || 'success');
    toast.innerHTML = '<i class="fas ' + (type === 'error' ? 'fa-exclamation-circle' : 'fa-check-circle') + '"></i> ' + message;
    document.body.appendChild(toast);
    
    setTimeout(function() {
        toast.classList.add('show');
    }, 100);
    
    setTimeout(function() {
        toast.classList.remove('show');
        setTimeout(function() {
            toast.remove();
        }, 300);
    }, 3000);
}

// ========== TOAST STYLES ==========
const toastStyle = document.createElement('style');
toastStyle.textContent = `
    .toast-notification {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #1a1a1a;
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        font-size: 0.85rem;
        z-index: 1000;
        transform: translateX(400px);
        transition: transform 0.3s ease;
        display: flex;
        align-items: center;
        gap: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .toast-notification.show {
        transform: translateX(0);
    }
    
    .toast-notification.toast-success {
        background: #4CAF50;
    }
    
    .toast-notification.toast-error {
        background: #f44336;
    }
    
    @media (max-width: 768px) {
        .toast-notification {
            bottom: 10px;
            right: 10px;
            left: 10px;
            transform: translateY(100px);
            text-align: center;
            justify-content: center;
        }
        
        .toast-notification.show {
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(toastStyle);

console.log('✅ admin.js loaded successfully');


