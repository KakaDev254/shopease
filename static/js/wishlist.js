document.addEventListener('DOMContentLoaded', () => {
    const wishlistDrawer = document.getElementById('wishlist-drawer');
    const wishlistOverlay = document.getElementById('wishlist-overlay');
    const wishlistToggles = [document.getElementById('wishlist-toggle'), document.getElementById('mobile-wishlist-toggle')];
    const wishlistClose = document.getElementById('wishlist-close');
    const wishlistBody = document.getElementById('wishlist-drawer-body');
    const wishlistBadges = [document.getElementById('wishlist-badge'), document.getElementById('mobile-wishlist-badge')];

    function openWishlist() {
        fetchWishlist();
        wishlistDrawer.classList.add('open');
        wishlistOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeWishlist() {
        wishlistDrawer.classList.remove('open');
        wishlistOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    wishlistToggles.forEach(btn => btn?.addEventListener('click', openWishlist));
    wishlistClose?.addEventListener('click', closeWishlist);
    wishlistOverlay?.addEventListener('click', closeWishlist);

    function fetchWishlist() {
        fetch('/products/api/wishlist/drawer/')
            .then(res => res.text())
            .then(html => {
                wishlistBody.innerHTML = html;
                if (typeof lucide !== 'undefined') {
                    lucide.createIcons();
                }
            });
    }

    // Global Wishlist Toggle (Handles mobile & desktop)
    document.body.addEventListener('click', (e) => {
        const btn = e.target.closest('.wish-btn');
        
        if (btn) {
            e.preventDefault(); 
            e.stopPropagation(); // Stop the tap from triggering the product link
            
            const slug = btn.dataset.slug;
            
            // Visual loading state
            const originalContent = btn.innerHTML;
            btn.innerHTML = '<i data-lucide="loader-2" class="spin"></i>';
            if (typeof lucide !== 'undefined') lucide.createIcons();

            const formData = new FormData();
            formData.append('slug', slug);
            
            fetch('/products/api/wishlist/toggle/', {
                method: 'POST',
                headers: { 'X-CSRFToken': getCsrfToken() },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                // Restore icon
                btn.innerHTML = originalContent;
                if (typeof lucide !== 'undefined') lucide.createIcons();

                if (data.ok) {
                    updateBadges(data.wishlist_count);
                    btn.classList.toggle('active', data.active);
                    
                    // Change color to show it's active
                    if(data.active) {
                        btn.style.color = 'var(--orange)';
                    } else {
                        btn.style.color = 'var(--navy)';
                    }
                    
                    // If drawer is open, refresh it
                    if (wishlistDrawer.classList.contains('open')) {
                        fetchWishlist();
                    }
                }
            })
            .catch(err => {
                btn.innerHTML = originalContent;
                if (typeof lucide !== 'undefined') lucide.createIcons();
                console.error('Wishlist Error:', err);
            });
        }
    });

    function updateBadges(count) {
        wishlistBadges.forEach(badge => {
            if (!badge) return;
            badge.textContent = count;
            badge.style.display = count > 0 ? 'inline-block' : 'none';
        });
    }

    function getCsrfToken() {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, 10) === ('csrftoken=')) {
                    cookieValue = decodeURIComponent(cookie.substring(10));
                    break;
                }
            }
        }
        if (!cookieValue) {
            const meta = document.querySelector('meta[name="csrf-token"]');
            if (meta) cookieValue = meta.getAttribute('content');
        }
        return cookieValue;
    }
});