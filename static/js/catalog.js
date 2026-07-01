(function () {
    var searchInput = document.getElementById('food-search');
    var cards = document.querySelectorAll('.food-card');
    var pills = document.querySelectorAll('.filter-pill');
    var grid = document.querySelector('.catalog-grid');
    var activeCategory = '';
    var sortKey = '';
    var sortAsc = false;

    if (!searchInput || !cards.length) return;

    function normalize(str) {
        return str.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    }

    // --- URL state ---
    function pushState() {
        var params = new URLSearchParams();
        var q = searchInput.value.trim();
        if (q) params.set('q', q);
        if (activeCategory) params.set('cat', activeCategory);
        if (sortKey) {
            params.set('sort', sortKey);
            if (sortAsc) params.set('asc', '1');
        }
        var str = params.toString();
        var url = window.location.pathname + (str ? '?' + str : '');
        history.replaceState(null, '', url);
    }

    function readState() {
        var params = new URLSearchParams(window.location.search);
        var q = params.get('q') || '';
        searchInput.value = q;

        activeCategory = params.get('cat') || '';
        pills.forEach(function (p) {
            var cat = p.getAttribute('data-category');
            p.classList.toggle('active', cat === activeCategory);
        });
        if (activeCategory && filtersEl) {
            filtersEl.style.display = '';
            filterToggle.classList.add('active');
        }

        sortKey = params.get('sort') || '';
        sortAsc = params.get('asc') === '1';
        updateOptions();
        updateToggleLabel();
    }

    // --- Filter & Sort ---
    function filterCards() {
        var query = normalize(searchInput.value.trim());

        cards.forEach(function (card) {
            var searchText = normalize(card.getAttribute('data-search') || '');
            var category = card.getAttribute('data-category') || '';

            var matchesSearch = !query || searchText.indexOf(query) !== -1;
            var matchesCategory = !activeCategory || category === activeCategory;

            card.style.display = (matchesSearch && matchesCategory) ? '' : 'none';
        });

        pushState();
    }

    function sortCards() {
        if (!sortKey || !grid) return;
        var arr = Array.prototype.slice.call(cards);
        arr.sort(function (a, b) {
            var va = parseFloat(a.getAttribute('data-' + sortKey)) || 0;
            var vb = parseFloat(b.getAttribute('data-' + sortKey)) || 0;
            return sortAsc ? va - vb : vb - va;
        });
        arr.forEach(function (card) { grid.appendChild(card); });
    }

    // Filter toggle
    var filterToggle = document.getElementById('filter-toggle');
    var filtersEl = document.getElementById('catalog-filters');

    if (filterToggle && filtersEl) {
        filterToggle.addEventListener('click', function () {
            var open = filtersEl.style.display !== 'none';
            filtersEl.style.display = open ? 'none' : '';
            filterToggle.classList.toggle('active', !open);
        });
    }

    // Sort dropdown
    var sortToggle = document.getElementById('sort-toggle');
    var sortMenu = document.getElementById('sort-menu');
    var sortOptions = document.querySelectorAll('.sort-option');
    var sortLabels = { kcal: 'kcal', bilk: 'bílk.', sach: 'sach.', tuky: 'tuky' };

    function updateToggleLabel() {
        if (!sortKey) {
            sortToggle.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M7 4v16m0 0l-3-3m3 3l3-3M17 20V4m0 0l3 3m-3-3l-3 3"/></svg>';
            sortToggle.classList.remove('active');
        } else {
            var arrow = sortAsc ? '↑' : '↓';
            sortToggle.innerHTML = '<span class="sort-label">' + sortLabels[sortKey] + ' ' + arrow + '</span>';
            sortToggle.classList.add('active');
        }
    }

    function updateOptions() {
        sortOptions.forEach(function (opt) {
            var key = opt.getAttribute('data-sort');
            var label = opt.textContent.replace(/ [↑↓]$/, '');
            if (key === sortKey) {
                opt.classList.add('active');
                opt.innerHTML = label + ' <span class="sort-arrow">' + (sortAsc ? '↑' : '↓') + '</span>';
            } else {
                opt.classList.remove('active');
                opt.textContent = label;
            }
        });
    }

    if (sortToggle && sortMenu) {
        sortToggle.addEventListener('click', function (e) {
            e.stopPropagation();
            sortMenu.classList.toggle('open');
        });

        document.addEventListener('click', function () {
            sortMenu.classList.remove('open');
        });

        sortMenu.addEventListener('click', function (e) {
            e.stopPropagation();
        });
    }

    sortOptions.forEach(function (opt) {
        opt.addEventListener('click', function () {
            var key = this.getAttribute('data-sort');

            if (sortKey === key) {
                if (sortAsc) {
                    sortKey = '';
                    sortAsc = false;
                } else {
                    sortAsc = true;
                }
            } else {
                sortKey = key;
                sortAsc = false;
            }

            updateOptions();
            updateToggleLabel();

            if (sortKey) {
                sortCards();
            }

            pushState();
            sortMenu.classList.remove('open');
        });
    });

    searchInput.addEventListener('input', filterCards);

    pills.forEach(function (pill) {
        pill.addEventListener('click', function () {
            pills.forEach(function (p) { p.classList.remove('active'); });
            this.classList.add('active');
            activeCategory = this.getAttribute('data-category');
            filterCards();
        });
    });

    // Restore state from URL on load
    readState();
    filterCards();
    if (sortKey) sortCards();
})();
