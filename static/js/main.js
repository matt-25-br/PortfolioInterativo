/**
 * Main JavaScript file for the portfolio application
 * Handles interactive features and UI enhancements
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    initializeTooltips();
    initializePopovers();
    initializeImagePreview();
    initializeFormValidation();
    initializeSmoothScrolling();
    initializeBackToTop();
    initializeSearchFilters();
    
    console.log('Portfolio application initialized');
});

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize Bootstrap popovers
 */
function initializePopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Image preview functionality for file uploads
 */
function initializeImagePreview() {
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    
    imageInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    // Find or create preview element
                    let preview = input.parentNode.querySelector('.image-preview');
                    if (!preview) {
                        preview = document.createElement('img');
                        preview.className = 'image-preview img-thumbnail mt-2';
                        preview.style.maxWidth = '200px';
                        preview.style.maxHeight = '200px';
                        input.parentNode.appendChild(preview);
                    }
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });
    });
}

/**
 * Enhanced form validation
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Focus on first invalid field
                const firstInvalid = form.querySelector(':invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                    firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Real-time validation for specific fields
    const emailFields = document.querySelectorAll('input[type="email"]');
    emailFields.forEach(function(field) {
        field.addEventListener('blur', function() {
            validateEmail(field);
        });
    });
    
    const passwordFields = document.querySelectorAll('input[type="password"]');
    passwordFields.forEach(function(field) {
        if (field.name === 'password2' || field.name === 'confirm_password') {
            field.addEventListener('input', function() {
                validatePasswordConfirmation(field);
            });
        }
    });
}

/**
 * Validate email field
 */
function validateEmail(field) {
    const email = field.value.trim();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (email && !emailRegex.test(email)) {
        field.setCustomValidity('Por favor, insira um email válido.');
    } else {
        field.setCustomValidity('');
    }
}

/**
 * Validate password confirmation
 */
function validatePasswordConfirmation(confirmField) {
    const passwordField = document.querySelector('input[name="password"]');
    if (passwordField && confirmField.value !== passwordField.value) {
        confirmField.setCustomValidity('As senhas não coincidem.');
    } else {
        confirmField.setCustomValidity('');
    }
}

/**
 * Smooth scrolling for anchor links
 */
function initializeSmoothScrolling() {
    const anchors = document.querySelectorAll('a[href^="#"]');
    
    anchors.forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/**
 * Back to top button functionality
 */
function initializeBackToTop() {
    // Create back to top button if it doesn't exist
    let backToTopBtn = document.getElementById('backToTopBtn');
    if (!backToTopBtn) {
        backToTopBtn = document.createElement('button');
        backToTopBtn.id = 'backToTopBtn';
        backToTopBtn.className = 'btn btn-primary position-fixed';
        backToTopBtn.style.cssText = 'bottom: 20px; right: 20px; z-index: 1000; display: none; border-radius: 50%; width: 50px; height: 50px;';
        backToTopBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
        backToTopBtn.title = 'Voltar ao topo';
        document.body.appendChild(backToTopBtn);
    }
    
    // Show/hide button based on scroll position
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTopBtn.style.display = 'block';
        } else {
            backToTopBtn.style.display = 'none';
        }
    });
    
    // Scroll to top when clicked
    backToTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

/**
 * Search and filter functionality
 */
function initializeSearchFilters() {
    const searchInput = document.querySelector('input[type="search"]');
    if (searchInput) {
        // Add search icon animation
        searchInput.addEventListener('focus', function() {
            const icon = this.parentNode.querySelector('.fas');
            if (icon) {
                icon.style.transform = 'scale(1.1)';
            }
        });
        
        searchInput.addEventListener('blur', function() {
            const icon = this.parentNode.querySelector('.fas');
            if (icon) {
                icon.style.transform = 'scale(1)';
            }
        });
    }
    
    // Filter cards based on search term
    const filterCards = document.querySelectorAll('[data-filter]');
    if (searchInput && filterCards.length > 0) {
        searchInput.addEventListener('input', debounce(function() {
            const searchTerm = this.value.toLowerCase();
            
            filterCards.forEach(function(card) {
                const filterText = card.dataset.filter.toLowerCase();
                const cardElement = card.closest('.col-lg-4, .col-md-6, .col-12');
                
                if (filterText.includes(searchTerm)) {
                    cardElement.style.display = 'block';
                    cardElement.classList.add('fade-in');
                } else {
                    cardElement.style.display = 'none';
                    cardElement.classList.remove('fade-in');
                }
            });
        }, 300));
    }
}

/**
 * Debounce function to limit function calls
 */
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

/**
 * Show loading state for buttons
 */
function showButtonLoading(button) {
    if (button) {
        const originalText = button.innerHTML;
        button.dataset.originalText = originalText;
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Carregando...';
        button.disabled = true;
    }
}

/**
 * Hide loading state for buttons
 */
function hideButtonLoading(button) {
    if (button && button.dataset.originalText) {
        button.innerHTML = button.dataset.originalText;
        button.disabled = false;
        delete button.dataset.originalText;
    }
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '1060';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Initialize and show toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast element after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showToast('Texto copiado para a área de transferência!', 'success');
    }).catch(function() {
        showToast('Erro ao copiar texto', 'error');
    });
}

/**
 * Format file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Validate file upload
 */
function validateFileUpload(input, maxSize = 16 * 1024 * 1024) {
    const file = input.files[0];
    if (!file) return true;
    
    // Check file size
    if (file.size > maxSize) {
        showToast(`Arquivo muito grande. Tamanho máximo: ${formatFileSize(maxSize)}`, 'error');
        input.value = '';
        return false;
    }
    
    // Check file type for images
    if (input.accept && input.accept.includes('image')) {
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
        if (!allowedTypes.includes(file.type)) {
            showToast('Tipo de arquivo não permitido. Use: JPG, PNG, GIF', 'error');
            input.value = '';
            return false;
        }
    }
    
    return true;
}

/**
 * Initialize file upload validation
 */
document.addEventListener('change', function(e) {
    if (e.target.type === 'file') {
        validateFileUpload(e.target);
    }
});

/**
 * Auto-resize textareas
 */
function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}

// Initialize auto-resize for all textareas
document.querySelectorAll('textarea').forEach(function(textarea) {
    textarea.addEventListener('input', function() {
        autoResizeTextarea(this);
    });
    
    // Initial resize
    autoResizeTextarea(textarea);
});

/**
 * Handle AJAX form submissions
 */
function submitFormAjax(form, callback) {
    const formData = new FormData(form);
    const submitButton = form.querySelector('[type="submit"]');
    
    showButtonLoading(submitButton);
    
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        hideButtonLoading(submitButton);
        if (callback) callback(data);
    })
    .catch(error => {
        hideButtonLoading(submitButton);
        console.error('Error:', error);
        showToast('Erro ao enviar formulário', 'error');
    });
}

/**
 * Lazy loading for images
 */
function initializeLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver(function(entries, observer) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(function(img) {
            imageObserver.observe(img);
        });
    }
}

// Initialize lazy loading
initializeLazyLoading();

/**
 * Dark mode toggle (if needed in the future)
 */
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
}

// Load dark mode preference
if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
}

/**
 * Print functionality
 */
function printPage() {
    window.print();
}

/**
 * Share functionality
 */
function shareContent(title, text, url) {
    if (navigator.share) {
        navigator.share({
            title: title,
            text: text,
            url: url
        });
    } else {
        // Fallback: copy URL to clipboard
        copyToClipboard(url);
    }
}

// Export functions for global use
window.portfolioApp = {
    showToast,
    copyToClipboard,
    validateFileUpload,
    submitFormAjax,
    toggleDarkMode,
    printPage,
    shareContent,
    showButtonLoading,
    hideButtonLoading
};
