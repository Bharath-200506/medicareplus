// ─── MediCarePlus Main JavaScript ──────────────────────────────

// Auto-dismiss toasts
document.addEventListener('DOMContentLoaded', function () {
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(function (toastEl) {
        const toast = new bootstrap.Toast(toastEl, { delay: 4000 });
        toast.show();
    });
});

// Quantity controls for cart
document.querySelectorAll('.qty-btn').forEach(btn => {
    btn.addEventListener('click', function () {
        const input = this.parentElement.querySelector('input[name="quantity"]');
        const current = parseInt(input.value) || 1;
        const max = parseInt(input.max) || 99;
        if (this.dataset.action === 'increase' && current < max) input.value = current + 1;
        if (this.dataset.action === 'decrease' && current > 1) input.value = current - 1;
    });
});

// Confirm modals
document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', function (e) {
        if (!confirm(this.dataset.confirm)) e.preventDefault();
    });
});