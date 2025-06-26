// # ===== static/js/main.js =====
// Enhanced functionality for Lab Simulation Quiz
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Image zoom functionality
    const images = document.querySelectorAll('.network-topology-img');
    images.forEach(function(img) {
        img.addEventListener('click', function() {
            // Create modal for image zoom
            const modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.innerHTML = `
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Network Topology - Full Size</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body text-center">
                            <img src="${this.src}" class="img-fluid" alt="Network Topology">
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
            
            // Remove modal from DOM when hidden
            modal.addEventListener('hidden.bs.modal', function() {
                document.body.removeChild(modal);
            });
        });
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const textareas = form.querySelectorAll('textarea[required]');
            let hasError = false;
            
            textareas.forEach(function(textarea) {
                if (textarea.value.trim() === '') {
                    textarea.classList.add('is-invalid');
                    hasError = true;
                } else {
                    textarea.classList.remove('is-invalid');
                }
            });
            
            if (hasError) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    });

    // Character counter for textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(function(textarea) {
        const counter = document.createElement('small');
        counter.className = 'form-text text-muted';
        counter.textContent = `Characters: ${textarea.value.length}`;
        textarea.parentNode.appendChild(counter);
        
        textarea.addEventListener('input', function() {
            counter.textContent = `Characters: ${this.value.length}`;
        });
    });

    // Smooth scrolling for internal links
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(function(link) {
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

    // Quiz timer (optional feature)
    const quizForms = document.querySelectorAll('form[action*="submit"]');
    quizForms.forEach(function(form) {
        let startTime = Date.now();
        const timer = document.createElement('div');
        timer.className = 'alert alert-info position-fixed top-0 end-0 m-3';
        timer.style.zIndex = '1050';
        timer.innerHTML = '<strong>Time:</strong> <span id="timer">00:00</span>';
        document.body.appendChild(timer);
        
        const timerSpan = timer.querySelector('#timer');
        const interval = setInterval(function() {
            const elapsed = Math.floor((Date.now() - startTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;
            timerSpan.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }, 1000);
        
        form.addEventListener('submit', function() {
            clearInterval(interval);
            timer.remove();
        });
    });
});