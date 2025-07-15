function createQuote() {
    const $submitBtn = $('#quoteForm button[type="submit"]');
    showLoading($submitBtn);
    
    const formData = {
        customer_id: $('#customerId').val(),
        job_name: $('#jobName').val(),
        job_address: $('#jobAddress').val(),
        hire_start_date: $('#hireStartDate').val(),
        hire_end_date: $('#hireEndDate').val(),
        items: selectedEquipment,
        subtotal: selectedEquipment.reduce((sum, item) => sum + item.total_amount, 0),
        discount: parseFloat($('#discount').val()) || 0,
        gst: (selectedEquipment.reduce((sum, item) => sum + item.total_amount, 0) - (parseFloat($('#discount').val()) || 0)) * 0.1,
        total: selectedEquipment.reduce((sum, item) => sum + item.total_amount, 0) - (parseFloat($('#discount').val()) || 0) + ((selectedEquipment.reduce((sum, item) => sum + item.total_amount, 0) - (parseFloat($('#discount').val()) || 0)) * 0.1)
    };
    
    apiCall('/api/quote', 'POST', formData)
        .done(function(response) {
            if (response.success) {
                showToast('Success', `Quote ${response.quote_number} created successfully!`, 'success');
                
                // Clear auto-save data
                clearAutoSave();
                
                // Check if we should create booking after quote
                if (window.createBookingAfterQuote) {
                    setTimeout(() => {
                        window.location.href = `/booking?quote_id=${response.quote_id}`;
                    }, 1500);
                } else {
                    // Redirect or show options
                    setTimeout(() => {
                        if (confirm('Quote created successfully! Would you like to convert it to a booking?')) {
                            window.location.href = `/booking?quote_id=${response.quote_id}`;
                        } else {
                            window.location.href = '/dashboard';
                        }
                    }, 1500);
                }
            } else {
                showToast('Error', response.error || 'Failed to create quote', 'danger');
            }
        })
        .fail(function(xhr) {
            let errorMessage = 'Failed to create quote. Please try again.';
            
            if (xhr.responseJSON && xhr.responseJSON.error) {
                errorMessage = xhr.responseJSON.error;
            }
            
            showToast('Error', errorMessage, 'danger');
        })
        .always(function() {
            hideLoading($submitBtn);
            // Reset the flag
            window.createBookingAfterQuote = false;
        });
}