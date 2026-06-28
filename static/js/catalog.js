(function () {
    var searchInput = document.getElementById('food-search');
    var cards = document.querySelectorAll('.food-card');
    var pills = document.querySelectorAll('.filter-pill');
    var activeCategory = '';

    if (!searchInput || !cards.length) return;

    function normalize(str) {
        return str.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    }

    function filterCards() {
        var query = normalize(searchInput.value.trim());

        cards.forEach(function (card) {
            var title = normalize(card.querySelector('.food-card-title').textContent);
            var brand = card.querySelector('.food-card-brand');
            brand = brand ? normalize(brand.textContent) : '';
            var category = card.getAttribute('data-category') || '';

            var matchesSearch = !query || title.indexOf(query) !== -1 || brand.indexOf(query) !== -1;
            var matchesCategory = !activeCategory || category === activeCategory;

            card.style.display = (matchesSearch && matchesCategory) ? '' : 'none';
        });
    }

    searchInput.addEventListener('input', filterCards);

    pills.forEach(function (pill) {
        pill.addEventListener('click', function () {
            pills.forEach(function (p) { p.classList.remove('active'); });
            this.classList.add('active');
            activeCategory = this.getAttribute('data-category');
            filterCards();
        });
    });
})();
