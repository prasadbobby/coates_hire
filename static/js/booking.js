// Coates Hire - Booking Management JavaScript
let assignedAssets = {};
let bookingValidation = {
    customer: false,
    delivery: false,
    schedule: false,
    equipment: false
};

$(document).ready(function() {
    initializeBookingForm();
    loadAvailableAssets();
});

function initializeBookingForm() {
    // Set default dates
    setDefaultDates();
    
    // Setup event handlers
    setupEventHandlers();
    
    // If converting from quote, load quote data
    const quoteId = $('#quoteId').val();
    if (quoteId) {
        loadQuoteData(quoteId);
    }
    
    // Initialize validation
    updateBookingValidation();
}

function setDefaultDates() {
    // Set delivery date to tomorrow 9 AM
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(9, 0, 0, 0);
    $('#deliveryDate').val(tomorrow.toISOString().slice(0, 16));
    
    // Set pickup date to 7 days later at 5 PM
    const pickupDate = new Date(tomorrow);
    pickupDate.setDate(pickupDate.getDate() + 6);
    pickupDate.setHours(17, 0, 0, 0);
    $('#pickupDate').val(pickupDate.toISOString().slice(0, 16));
    
    validateSchedule();
}

function setupEventHandlers() {
    // Customer selection
    $('#customerId').change(function() {
        const customerId = $(this).val();
        if (customerId) {
            loadCustomerDetails(customerId);
            bookingValidation.customer = true;
        } else {
            bookingValidation.customer = false;
        }
        updateBookingValidation();
    });
    
    // Delivery details
    $('#deliveryAddress').on('input', function() {
        bookingValidation.delivery = $(this).val().trim().length > 0;
        updateBookingValidation();
    });
    
    // Schedule validation
    $('#deliveryDate, #pickupDate').change(function() {
        validateSchedule();
        updateBookingValidation();
    });
    
    // Form submission
    $('#bookingForm').on('submit', function(e) {
        e.preventDefault();
        if (validateBookingForm()) {
            createBooking();
        }
    });
}

function loadAvailableAssets() {
    // Load available assets for each equipment type
    $('#equipmentAssignmentBody tr').each(function() {
        const equipmentId = $(this).data('equipment-id');
        if (equipmentId) {
            loadAssetsForEquipment(equipmentId);
        }
    });
}

function loadAssetsForEquipment(equipmentId) {
    const selectElement = $(`#availableAssets_${equipmentId}`);
    selectElement.empty().append('<option value="">Select asset...</option>');
    
    // Generate dummy assets for demonstration
    for (let i = 1; i <= 5; i++) {
        selectElement.append(`
            <option value="${equipmentId}_${i}">
                ASSET-${i.toString().padStart(3, '0')} - Sydney (Good)
            </option>
        `);
    }
}

function validateSchedule() {
    const deliveryDate = new Date($('#deliveryDate').val());
    const pickupDate = new Date($('#pickupDate').val());
    const now = new Date();
    
    let isValid = true;
    const errors = [];
    
    // Check if delivery date is in the future
    if (deliveryDate <= now) {
        errors.push('Delivery date must be in the future');
        isValid = false;
    }
    
    // Check if pickup is after delivery
    if (pickupDate <= deliveryDate) {
        errors.push('Pickup date must be after delivery date');
        isValid = false;
    }
    
    // Check minimum hire period (1 day)
    const hireDuration = (pickupDate - deliveryDate) / (1000 * 60 * 60 * 24);
    if (hireDuration < 1) {
        errors.push('Minimum hire period is 1 day');
        isValid = false;
    }
    
    // Update validation status
    bookingValidation.schedule = isValid;
    
    // Show/hide error messages
    const errorContainer = $('#scheduleErrors');
    if (errors.length > 0) {
        if (!errorContainer.length) {
            $('#pickupDate').after('<div id="scheduleErrors"></div>');
        }
        $('#scheduleErrors').html(`
            <div class="alert alert-danger alert-sm mt-2">
                <ul class="mb-0">
                    ${errors.map(error => `<li>${error}</li>`).join('')}
                </ul>
            </div>
        `).show();
    } else {
        errorContainer.hide();
    }
    
    return isValid;
}

function updateBookingValidation() {
    // Check equipment assignment status
    let allEquipmentAssigned = true;
    Object.keys(assignedAssets).forEach(equipmentId => {
        const required = assignedAssets[equipmentId].required || 1;
        const assigned = assignedAssets[equipmentId].assigned ? assignedAssets[equipmentId].assigned.length : 0;
        if (assigned < required) {
            allEquipmentAssigned = false;
        }
    });
    
    bookingValidation.equipment = allEquipmentAssigned;
    
    // Update submit button
    updateSubmitButton();
}

function updateSubmitButton() {
    const allValid = Object.values(bookingValidation).every(Boolean);
    const $submitBtn = $('#bookingForm button[type="submit"]');
    
    $submitBtn.prop('disabled', !allValid);
    
    if (allValid) {
        $submitBtn.removeClass('btn-secondary').addClass('btn-primary');
    } else {
        $submitBtn.removeClass('btn-primary').addClass('btn-secondary');
    }
}

function validateBookingForm() {
    const errors = [];
    
    // Validate all sections
    if (!bookingValidation.customer) {
        errors.push('Please select a customer');
    }
    
    if (!bookingValidation.delivery) {
        errors.push('Please enter delivery address');
    }
    
    if (!bookingValidation.schedule) {
        errors.push('Please fix schedule errors');
    }
    
    // Additional validations
    const totalAmount = parseFloat($('#totalAmount').val());
    if (!totalAmount || totalAmount <= 0) {
        errors.push('Invalid total amount');
    }
    
    if (errors.length > 0) {
        showToast('Validation Error', errors.join('<br>'), 'danger');
        return false;
    }
    
    return true;
}

function createBooking() {
    const $submitBtn = $('#bookingForm button[type="submit"]');
    showLoading($submitBtn);
    
    // Prepare booking data
    const bookingData = {
        quote_id: $('#quoteId').val() || null,
        customer_id: $('#customerId').val(),
        job_name: $('#jobName').val(),
        delivery_address: $('#deliveryAddress').val(),
        delivery_date: $('#deliveryDate').val(),
        pickup_date: $('#pickupDate').val(),
        total_amount: parseFloat($('#totalAmount').val()),
        deposit_amount: parseFloat($('#depositAmount').val()) || 0,
        items: []
    };
    
    // Submit booking
    apiCall('/api/booking', 'POST', bookingData)
        .done(function(response) {
            if (response.success) {
                showToast('Success', `Booking ${response.booking_number} created successfully!`, 'success');
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 2000);
            } else {
                showToast('Error', response.error || 'Failed to create booking', 'danger');
            }
        })
        .fail(function(xhr) {
            let errorMessage = 'Failed to create booking. Please try again.';
            if (xhr.responseJSON && xhr.responseJSON.error) {
                errorMessage = xhr.responseJSON.error;
            }
            showToast('Error', errorMessage, 'danger');
        })
        .always(function() {
            hideLoading($submitBtn);
        });
}

function loadCustomerDetails(customerId) {
    // Simulate loading customer details
    showToast('Customer Loaded', 'Customer details loaded successfully', 'info');
}

function loadQuoteData(quoteId) {
    // Simulate loading quote data
    showToast('Quote Loaded', 'Quote data loaded for booking', 'info');
}