    // Handle both desktop clicks and mobile taps reliably
    document.body.addEventListener('click', (e) => {
        const btn = e.target.closest('.wish-btn');
        if (btn) {
            e.preventDefault(); 
            e.stopPropagation(); // Crucial: stops the card link from triggering
            
            const slug = btn.dataset.slug;
            
            const formData = new FormData();
            formData.append('slug', slug);
            
            fetch('/products/api/wishlist/toggle/', {
                method: 'POST',
                headers: { 'X-CSRFToken': getCsrfToken() },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.ok) {
                    updateBadges(data.wishlist_count);
                    btn.classList.toggle('active', data.active);
                    // Update icon color
                    if(data.active) {
                        btn.style.color = 'var(--orange)';
                    } else {
                        btn.style.color = 'var(--navy)';
                    }
                }
            });
        }
    });