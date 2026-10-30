document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const resultsBox = document.getElementById('search-results');
    
    if (!searchInput) return;

    let timeout = null;

    searchInput.addEventListener('input', (e) => {
        clearTimeout(timeout);
        const query = e.target.value.trim();

        if (query.length < 2) {
            resultsBox.style.display = 'none';
            resultsBox.innerHTML = '';
            return;
        }

        // Debounce API call (wait 300ms after user stops typing)
        timeout = setTimeout(() => {
            fetch(`/products/api/live-search/?q=${encodeURIComponent(query)}`)
                .then(res => res.json())
                .then(data => {
                    if (data.results.length > 0) {
                        let html = '';
                        data.results.forEach(item => {
                            html += `
                                <a href="/products/p/${item.slug}/" class="search-result-item">
                                    <img src="${item.image}" alt="${item.name}">
                                    <div>
                                        <div class="sr-name">${item.name}</div>
                                        <div class="sr-price">KSh ${item.price}</div>
                                    </div>
                                </a>
                            `;
                        });
                        resultsBox.innerHTML = html;
                        resultsBox.style.display = 'block';
                    } else {
                        resultsBox.innerHTML = '<div class="sr-empty">No results found</div>';
                        resultsBox.style.display = 'block';
                    }
                });
        }, 300);
    });

    // Hide results when clicking outside
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !resultsBox.contains(e.target)) {
            resultsBox.style.display = 'none';
        }
    });
});