// Main JavaScript for Expiry Tracker

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Price input formatting
    const priceInputs = document.querySelectorAll('input[name="price"]');
    priceInputs.forEach(input => {
        input.addEventListener('blur', function() {
            let value = parseFloat(this.value);
            if (!isNaN(value)) {
                this.value = value.toFixed(2);
            }
        });
    });

    // Date input validation
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        input.addEventListener('change', function() {
            const today = new Date().toISOString().split('T')[0];
            if (this.name === 'purchaseDate' && this.value > today) {
                this.setCustomValidity('Purchase date cannot be in the future');
            } else if (this.name === 'expirationDate' && this.value < today) {
                this.setCustomValidity('Expiration date cannot be in the past');
            } else {
                this.setCustomValidity('');
            }
        });
    });

    // Auto-fill expiration date based on product name
    const productNameInput = document.getElementById('productName');
    const expirationDateInput = document.getElementById('expirationDate');
    
    if (productNameInput && expirationDateInput) {
        const productExpirationMap = {
            'milk': 7,
            'bread': 5,
            'eggs': 14,
            'cheese': 10,
            'yogurt': 7,
            'butter': 14,
            'chicken': 3,
            'beef': 3,
            'fish': 2,
            'lettuce': 7,
            'tomatoes': 5,
            'bananas': 5,
            'apples': 14,
            'oranges': 14
        };

        productNameInput.addEventListener('blur', function() {
            const productName = this.value.toLowerCase();
            const purchaseDate = document.getElementById('purchaseDate').value;
            
            if (purchaseDate && !expirationDateInput.value) {
                for (const [product, days] of Object.entries(productExpirationMap)) {
                    if (productName.includes(product)) {
                        const purchaseDateObj = new Date(purchaseDate);
                        const expirationDateObj = new Date(purchaseDateObj.getTime() + (days * 24 * 60 * 60 * 1000));
                        expirationDateInput.value = expirationDateObj.toISOString().split('T')[0];
                        break;
                    }
                }
            }
        });
    }

    // Search functionality
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const tableRows = document.querySelectorAll('tbody tr');
            
            tableRows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }

    // Confirmation for delete actions
    const deleteButtons = document.querySelectorAll('[onclick*="deleteItem"]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const itemName = this.getAttribute('data-item-name') || 'this item';
            if (confirm(`Are you sure you want to delete ${itemName}?`)) {
                this.closest('form').submit();
            }
        });
    });

    // Refresh data every 5 minutes
    setInterval(() => {
        if (window.location.pathname === '/') {
            fetch('/api/items')
                .then(response => response.json())
                .then(data => {
                    // Update the page with fresh data if needed
                    console.log('Data refreshed:', data.length, 'items');
                })
                .catch(error => {
                    console.error('Error refreshing data:', error);
                });
        }
    }, 300000); // 5 minutes

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + N to add new item
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            const addButton = document.querySelector('a[href*="add_item"]');
            if (addButton) {
                addButton.click();
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(modal => {
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) {
                    bsModal.hide();
                }
            });
        }
    });

    // Add loading states to buttons
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (this.closest('form').checkValidity()) {
                this.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
                this.disabled = true;
            }
        });
    });

    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function calculateDaysUntilExpiration(expirationDate) {
    const today = new Date();
    const expDate = new Date(expirationDate);
    const diffTime = expDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
}

// Export functions for use in templates
window.ExpiryTracker = {
    formatCurrency,
    formatDate,
    calculateDaysUntilExpiration
};
