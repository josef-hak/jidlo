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
        if (rozpisItems.length) {
            var r = rozpisItems.map(function (item) {
                return item.slug + ':' + item.grams + 'g';
            }).join(',');
            params.set('r', r);
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

        // Restore rozpis from URL
        var r = params.get('r');
        if (r) {
            r.split(',').forEach(function (part) {
                var match = part.match(/^(.+):(\d+(?:\.\d+)?)g$/);
                if (!match) return;
                var slug = match[1];
                var grams = parseFloat(match[2]);
                // Find card by slug
                var card = grid.querySelector('.food-card[data-slug="' + slug + '"]');
                if (card && grams > 0) {
                    addRozpisItem(card, grams);
                }
            });
        }
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
    var sortLabels = { kcal: 'kcal', bilk: 'b', sach: 's', tuky: 't' };

    function updateToggleLabel() {
        if (!sortKey) {
            sortToggle.innerHTML = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M7 4v16m0 0l-3-3m3 3l3-3M17 20V4m0 0l3 3m-3-3l-3 3"/></svg>';
            sortToggle.classList.remove('active');
            sortToggle.classList.remove('has-label');
        } else {
            var arrow = sortAsc ? '↑' : '↓';
            sortToggle.innerHTML = '<span class="sort-label">' + sortLabels[sortKey] + ' ' + arrow + '</span>';
            sortToggle.classList.add('active');
            sortToggle.classList.add('has-label');
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

    // --- Rozpis ---
    var rozpisToggle = document.getElementById('rozpis-toggle');
    var rozpisPanel = document.getElementById('rozpis-panel');
    var rozpisItemsEl = document.getElementById('rozpis-items');
    var rozpisSummaryEl = document.getElementById('rozpis-summary');
    var rozpisActive = false;
    var rozpisItems = [];
    var nutKeys = ['kcal', 'kj', 'bilk', 'sach', 'tuky', 'vlaknina', 'sul'];

    function toggleRozpis() {
        rozpisActive = !rozpisActive;
        grid.classList.toggle('rozpis-active', rozpisActive);
        rozpisToggle.classList.toggle('active', rozpisActive);
    }

    function macroCell(val, color) {
        return '<td class="rozpis-macro" style="background:' + color + '15"><span class="rozpis-macro-val">' + val + '</span></td>';
    }

    function donutSvg(bilk, sach, tuky, size) {
        var total = bilk + sach + tuky;
        if (total <= 0) return '';
        var pB = bilk / total * 100, pS = sach / total * 100, pT = tuky / total * 100;
        var segs = [
            [pB, '#e05555', 0],
            [pS, '#5588dd', pB],
            [pT, '#eebb44', pB + pS]
        ];
        var circles = segs.map(function (s) {
            if (s[0] < 0.5) return '';
            return '<circle cx="21" cy="21" r="15.9" fill="none" stroke="' + s[1] + '" stroke-width="5" ' +
                'stroke-dasharray="' + s[0].toFixed(1) + ' ' + (100 - s[0]).toFixed(1) + '" ' +
                'stroke-dashoffset="' + (100 - s[2] + 25).toFixed(1) + '"/>';
        }).join('');
        return '<svg viewBox="0 0 42 42" width="' + size + '" height="' + size + '" style="transform:rotate(-90deg)">' +
            '<circle cx="21" cy="21" r="15.9" fill="none" stroke="#e8e8e8" stroke-width="5"/>' +
            circles + '</svg>';
    }

    function renderRozpis() {
        if (!rozpisItems.length) {
            rozpisPanel.style.display = 'none';
            return;
        }
        rozpisPanel.style.display = '';

        var totals = {};
        nutKeys.forEach(function (k) { totals[k] = 0; });
        rozpisItems.forEach(function (item) {
            nutKeys.forEach(function (k) { totals[k] += item[k] || 0; });
        });

        var html = '<table class="rozpis-table"><thead><tr>' +
            '<th></th><th></th><th class="rozpis-th-g">g</th>' +
            '<th class="rozpis-th-macro">kcal</th>' +
            '<th class="rozpis-th-macro" style="color:#e05555">b</th>' +
            '<th class="rozpis-th-macro" style="color:#5588dd">s</th>' +
            '<th class="rozpis-th-macro" style="color:#eebb44">t</th>' +
            '<th></th></tr></thead><tbody>';

        rozpisItems.forEach(function (item, i) {
            html += '<tr class="rozpis-row">' +
                '<td class="rozpis-td-thumb"><img src="' + item.thumb + '" alt=""></td>' +
                '<td class="rozpis-td-name">' + item.title + '</td>' +
                '<td class="rozpis-td-g">' + item.grams + '</td>' +
                macroCell(Math.round(item.kcal), '#ffffff') +
                macroCell(item.bilk.toFixed(1), '#e05555') +
                macroCell(item.sach.toFixed(1), '#5588dd') +
                macroCell(item.tuky.toFixed(1), '#eebb44') +
                '<td><button class="rozpis-item-remove" data-idx="' + i + '">×</button></td>' +
                '</tr>';
        });

        // Summary row
        html += '<tr class="rozpis-row rozpis-total">' +
            '<td class="rozpis-td-thumb">' + donutSvg(totals.bilk, totals.sach, totals.tuky, 28) + '</td>' +
            '<td class="rozpis-td-name"><strong>Celkem</strong></td>' +
            '<td class="rozpis-td-g"></td>' +
            macroCell(Math.round(totals.kcal), '#ffffff') +
            macroCell(totals.bilk.toFixed(1), '#e05555') +
            macroCell(totals.sach.toFixed(1), '#5588dd') +
            macroCell(totals.tuky.toFixed(1), '#eebb44') +
            '<td></td></tr>';

        html += '</tbody></table>';

        rozpisPanel.innerHTML = html;

        rozpisPanel.querySelectorAll('.rozpis-item-remove').forEach(function (btn) {
            btn.addEventListener('click', function () {
                rozpisItems.splice(parseInt(this.getAttribute('data-idx')), 1);
                renderRozpis();
                pushState();
            });
        });
    }

    function addRozpisItem(card, grams) {
        if (!grams || grams <= 0) return;
        var title = card.getAttribute('data-title');
        var slug = card.getAttribute('data-slug');
        var thumb = card.getAttribute('data-thumb');
        var item = { title: title, slug: slug, grams: grams, thumb: thumb };
        nutKeys.forEach(function (k) {
            item[k] = (parseFloat(card.getAttribute('data-' + k)) || 0) * grams / 100;
        });
        rozpisItems.push(item);
        renderRozpis();
        pushState();
    }

    if (rozpisToggle) {
        rozpisToggle.addEventListener('click', function () {
            toggleRozpis();
        });
    }

    grid.addEventListener('click', function (e) {
        var addBtn = e.target.closest('.rozpis-add');
        if (!addBtn) return;
        e.preventDefault();
        e.stopPropagation();
        var card = addBtn.closest('.food-card');
        var input = card.querySelector('.rozpis-input');
        var grams = parseFloat(input.value);
        if (grams > 0) {
            addRozpisItem(card, grams);
            input.value = '';
        }
    });

    grid.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && e.target.classList.contains('rozpis-input')) {
            e.preventDefault();
            var card = e.target.closest('.food-card');
            var grams = parseFloat(e.target.value);
            if (grams > 0) {
                addRozpisItem(card, grams);
                e.target.value = '';
            }
        }
    });

    // Prevent link navigation when clicking rozpis input area
    grid.addEventListener('click', function (e) {
        if (e.target.closest('.food-card-rozpis')) {
            e.preventDefault();
            e.stopPropagation();
        }
    });

    // Restore state from URL on load
    readState();
    filterCards();
    if (sortKey) sortCards();
})();
