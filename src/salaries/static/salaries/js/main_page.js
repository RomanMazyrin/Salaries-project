document.querySelectorAll('form.show-loader').forEach(function(form) {
    form.addEventListener('submit', function(e) {
        console.log('submitted');
        document.getElementById('modal-activator').click();
        form.querySelector('button[type="submit"]').setAttribute('disabled', true);
    });
});