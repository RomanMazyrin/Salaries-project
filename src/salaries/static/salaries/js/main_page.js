document.querySelectorAll('form.show-loader').forEach(function(form) {
    form.addEventListener('submit', function(e) {
        document.getElementById('modal-activator').click();
        var button = form.querySelector('button[type="submit"]');
        button.setAttribute('disabled', true);
        button.querySelector('.spinner-border').classList.remove('hidden');
    });
});