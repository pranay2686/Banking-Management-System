// ── Auto-hide flash messages after 4 seconds ──
document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(function () {
                alert.remove();
            }, 500);
        }, 4000);
    });
});

// ── Confirm before destructive actions ────────
document.addEventListener('DOMContentLoaded', function () {
    const dangerForms = document.querySelectorAll('form[data-confirm]');
    dangerForms.forEach(function (form) {
        form.addEventListener('submit', function (e) {
            const message = form.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
});