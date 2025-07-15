// Coates Hire - Dashboard JavaScript
$(document).ready(function() {
    initializeDashboard();
});

function initializeDashboard() {
    // Animate statistics cards
    animateCounters();
    
    // Setup dashboard interactions
    setupDashboardInteractions();
}

function animateCounters() {
    $('.stats-number').each(function() {
        const $counter = $(this);
        const finalValue = parseInt($counter.text().replace(/[,$]/g, ''));
        
        if (isNaN(finalValue)) return;
        
        $counter.text('0');
        
        // Simple counter animation
        let currentValue = 0;
        const increment = finalValue / 30;
        const timer = setInterval(() => {
            currentValue += increment;
            if (currentValue >= finalValue) {
                currentValue = finalValue;
                clearInterval(timer);
            }
            $counter.text(Math.round(currentValue));
        }, 50);
    });
}

function setupDashboardInteractions() {
    // Quick action buttons hover effects
    $('.quick-actions .btn').hover(
        function() {
            $(this).addClass('hover-lift');
        },
        function() {
            $(this).removeClass('hover-lift');
        }
    );
    
    // Stats cards hover effects
    $('.stats-card, .equipment-category-card').hover(
        function() {
            $(this).addClass('hover-lift');
        },
        function() {
            $(this).removeClass('hover-lift');
        }
    );
    
    // Quote items click handlers
    $('.quote-item').click(function() {
        const quoteId = $(this).data('quote-id');
        if (quoteId) {
            viewQuoteDetails(quoteId);
        }
    });
}

function viewQuoteDetails(quoteId) {
    // Navigate to quote details
    window.location.href = `/quote/${quoteId}`;
}

// Export functions for global access
window.dashboardFunctions = {
    animateCounters,
    viewQuoteDetails
};