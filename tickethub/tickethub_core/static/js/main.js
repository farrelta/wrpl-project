/* ==========================================================================
   TicketHub — Client-side JavaScript
   Toast management, nav toggle, animations, star rating
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    initToasts();
    initNavToggle();
    initStaggerAnimations();
    initStarRating();
});

/* ---- Toast Auto-dismiss ---- */
function initToasts() {
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach((toast, index) => {
        // Auto-dismiss after 5s
        setTimeout(() => {
            dismissToast(toast);
        }, 5000 + index * 300);

        // Close button
        const closeBtn = toast.querySelector('.toast-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => dismissToast(toast));
        }
    });
}

function dismissToast(toast) {
    toast.classList.add('toast-exit');
    setTimeout(() => toast.remove(), 300);
}

/* ---- Mobile Nav Toggle ---- */
function initNavToggle() {
    const toggle = document.querySelector('.nav-toggle');
    const nav = document.querySelector('.navbar-nav');
    if (toggle && nav) {
        toggle.addEventListener('click', () => {
            nav.classList.toggle('show');
        });
    }
}

/* ---- Stagger Animations (Intersection Observer) ---- */
function initStaggerAnimations() {
    const cards = document.querySelectorAll('.card[data-animate]');
    if (!cards.length) return;

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry, i) => {
                if (entry.isIntersecting) {
                    entry.target.style.animationDelay = `${i * 0.06}s`;
                    entry.target.classList.add('fade-in-up');
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.1 }
    );

    cards.forEach((card) => {
        card.style.opacity = '0';
        observer.observe(card);
    });
}

/* ---- Star Rating Input ---- */
function initStarRating() {
    const ratingInputs = document.querySelectorAll('.star-rating-input');
    ratingInputs.forEach((container) => {
        const labels = container.querySelectorAll('label');
        const inputs = container.querySelectorAll('input[type="radio"]');

        // Ensure the default (5 stars) is checked
        if (inputs.length && !container.querySelector('input:checked')) {
            inputs[0].checked = true;
        }
    });
}

/* ---- Confirm Dialogs ---- */
function confirmCancel(bookingId) {
    if (confirm('Are you sure you want to cancel this booking? A refund will be issued.')) {
        document.getElementById('cancel-form-' + bookingId).submit();
    }
}

function confirmDelete(eventId) {
    if (confirm('Are you sure you want to delete this event? This action cannot be undone.')) {
        document.getElementById('delete-form-' + eventId).submit();
    }
}
