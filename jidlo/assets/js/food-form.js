(function () {
    var form = document.getElementById('food-form');
    if (!form) return;

    var preview = document.getElementById('photo-preview');
    var photoInput = document.getElementById('food-photo');
    var submitBtn = document.getElementById('submit-btn');
    var messageEl = document.getElementById('form-message');

    photoInput.addEventListener('change', function () {
        var file = this.files[0];
        if (file) {
            var reader = new FileReader();
            reader.onload = function (e) {
                preview.src = e.target.result;
                preview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        } else {
            preview.style.display = 'none';
        }
    });

    form.addEventListener('submit', function (e) {
        e.preventDefault();

        var title = document.getElementById('food-title').value.trim();
        if (!title) {
            showMessage('Vyplňte název potraviny.', 'error');
            return;
        }

        submitBtn.disabled = true;
        submitBtn.textContent = 'Ukládám...';
        messageEl.style.display = 'none';

        var data = new FormData(form);
        data.append('action', 'jidlo_add_food');
        data.append('nonce', jidloAjax.nonce);

        var xhr = new XMLHttpRequest();
        xhr.open('POST', jidloAjax.url);
        xhr.onload = function () {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Uložit potravinu';

            try {
                var response = JSON.parse(xhr.responseText);
                if (response.success) {
                    showMessage(
                        response.data.message +
                        ' <a href="' + response.data.url + '">Zobrazit &rarr;</a>',
                        'success'
                    );
                    form.reset();
                    preview.style.display = 'none';
                } else {
                    showMessage(response.data.message || 'Chyba při ukládání.', 'error');
                }
            } catch (err) {
                showMessage('Chyba při komunikaci se serverem.', 'error');
            }
        };
        xhr.onerror = function () {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Uložit potravinu';
            showMessage('Chyba sítě.', 'error');
        };
        xhr.send(data);
    });

    function showMessage(text, type) {
        messageEl.innerHTML = text;
        messageEl.className = 'form-message ' + type;
    }
})();
