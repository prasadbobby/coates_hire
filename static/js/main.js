// Coates Hire - Main JavaScript
$(document).ready(function() {
    // Initialize basic functionality
    initializeBasicFeatures();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize form validation
    initializeFormValidation();
    
    // Auto-dismiss alerts
    autoHideAlerts();
});

// Basic features without GSAP dependencies
function initializeBasicFeatures() {
    // Simple fade-in for elements
    $('.fade-in').css('opacity', '0').animate({'opacity': '1'}, 500);
    
    // Add hover effects to cards
    $('.stats-card, .kpi-card, .equipment-category-card').hover(
        function() { $(this).addClass('hover-lift'); },
        function() { $(this).removeClass('hover-lift'); }
    );
}

// Tooltips
function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Form Validation
function initializeFormValidation() {
    // Bootstrap validation
    var forms = document.querySelectorAll('.needs-validation');
    
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Real-time validation
    $('input[required], select[required], textarea[required]').on('blur', function() {
        validateField(this);
    });
}

function validateField(field) {
    const $field = $(field);
    const value = $field.val().trim();
    const isValid = field.checkValidity();
    
    $field.removeClass('is-valid is-invalid');
    
    if (value && isValid) {
        $field.addClass('is-valid');
    } else if (value && !isValid) {
        $field.addClass('is-invalid');
    }
}

function showToast(title, message, type = 'info') {
    const toastHtml = `
        <div class="toast align-items-center text-white bg-${type} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    <strong>${title}</strong><br>${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    // Add toast container if it doesn't exist
    if (!$('#toast-container').length) {
        $('body').append('<div id="toast-container" class="toast-container position-fixed top-0 end-0 p-3"></div>');
    }
    
    const $toast = $(toastHtml);
    $('#toast-container').append($toast);
    
    const toast = new bootstrap.Toast($toast[0]);
    toast.show();
    
    // Remove toast from DOM after it's hidden
    $toast.on('hidden.bs.toast', function() {
        $(this).remove();
    });
}

// Auto-hide alerts
function autoHideAlerts() {
    $('.alert:not(.alert-permanent)').each(function() {
        const $alert = $(this);
        setTimeout(() => {
            $alert.fadeOut(500, function() {
                $(this).remove();
            });
        }, 5000);
    });
}

// Loading states
function showLoading(element) {
    const $element = $(element);
    $element.addClass('btn-loading').prop('disabled', true);
    
    const originalText = $element.text();
    $element.data('original-text', originalText);
    $element.text('Loading...');
}

function hideLoading(element) {
    const $element = $(element);
    $element.removeClass('btn-loading').prop('disabled', false);
    
    const originalText = $element.data('original-text');
    if (originalText) {
        $element.text(originalText);
    }
}

// API Helper functions
function apiCall(url, method = 'GET', data = null) {
    const config = {
        url: url,
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    };
    
    if (data) {
        config.data = JSON.stringify(data);
    }
    
    return $.ajax(config);
}

// Number formatting
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-AU', {
        style: 'currency',
        currency: 'AUD'
    }).format(amount);
}

function formatNumber(number) {
    return new Intl.NumberFormat('en-AU').format(number);
}

// Date formatting
function formatDate(dateString) {
    return new Intl.DateTimeFormat('en-AU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    }).format(new Date(dateString));
}

function formatDateTime(dateString) {
    return new Intl.DateTimeFormat('en-AU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(new Date(dateString));
}

// Local Storage helpers
function saveToStorage(key, data) {
    try {
        localStorage.setItem(key, JSON.stringify(data));
    } catch (e) {
        console.warn('Unable to save to localStorage:', e);
    }
}

function loadFromStorage(key) {
    try {
        const data = localStorage.getItem(key);
        return data ? JSON.parse(data) : null;
    } catch (e) {
        console.warn('Unable to load from localStorage:', e);
        return null;
    }
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    if (e.error) {
        showToast('Error', 'Something went wrong. Please try again.', 'danger');
    }
});

// AJAX error handling
$(document).ajaxError(function(event, xhr, settings, thrownError) {
    console.error('AJAX error:', thrownError);
    
    if (xhr.status === 401) {
        window.location.href = '/login';
    } else if (xhr.status === 403) {
        showToast('Access Denied', 'You do not have permission to perform this action.', 'danger');
    } else if (xhr.status >= 500) {
        showToast('Server Error', 'A server error occurred. Please try again later.', 'danger');
    } else if (xhr.status !== 404) { // Don't show error for 404s (missing API endpoints)
        showToast('Error', 'An error occurred. Please try again.', 'warning');
    }
});