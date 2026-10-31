document.addEventListener('DOMContentLoaded', () => {
    const cartDrawer = document.getElementById('cart-drawer');
    const cartOverlay = document.getElementById('cart-overlay');
    const cartToggles = [document.getElementById('cart-toggle'), document.getElementById('mobile-cart-toggle')];
    const cartClose = document.getElementById('cart-close');
    const cartBody = document.getElementById('cart-drawer-body');
    const cartBadges = [document.getElementById('cart-badge'), document.getElementById('mobile-cart-badge')];

    function openCart() {
        fetchCart();
        cartDrawer.classList.add('open');
        cartOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeCart() {
        cartDrawer.classList.remove('open');
        cartOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    cartToggles.forEach(btn => btn?.addEventListener('click', openCart));
    cartClose?.addEventListener('click', closeCart);
    cartOverlay?.addEventListener('click', closeCart);

    // Fetch and render cart drawer
    function fetchCart() {
        fetch('/products/api/cart/drawer/')
            .then(res => res.text())
            .then(html => {
                cartBody.innerHTML = html;
                attachCartEvents();
                // Re-initialize icons for the newly loaded HTML
                if (typeof lucide !== 'undefined') {
                    lucide.createIcons();
                }
            });
    }

    // Handle qty updates inside drawer
    function attachCartEvents() {
        document.querySelectorAll('.cart-qty-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation(); // Stop event bubbling
                
                const slug = e.target.closest('button').dataset.slug;
                const action = e.target.closest('button').dataset.action;
                const input = document.getElementById(`qty-${slug}`);
                let qty = parseInt(input.value);
                
                if (action === 'inc') qty++;
                if (action === 'dec') qty--;

                updateCart(slug, qty);
            });
        });
    }

    function updateCart(slug, qty) {
        const formData = new FormData();
        formData.append('slug', slug);
        formData.append('qty', qty);
        
        fetch('/products/api/cart/update/', {
            method: 'POST',
            headers: { 
                'X-CSRFToken': getCsrfToken() 
            },
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.ok) {
                updateBadges(data.cart_count);
                fetchCart(); // Re-render drawer
            }
        });
    }

    // Global Add to Cart buttons (Handles both desktop & mobile taps)
    document.body.addEventListener('click', (e) => {
        const btn = e.target.closest('.add-to-cart');
        
        if (btn) {
            // Crucial for mobile: Stop the click from triggering the parent link
            e.preventDefault(); 
            e.stopPropagation(); 
            
            const slug = btn.dataset.slug;
            const qtySource = btn.dataset.qtySource; // For detail page quantity selector
            let qty = 1;
            
            if (qtySource) {
                const qtyInput = document.querySelector(qtySource);
                if (qtyInput) qty = parseInt(qtyInput.value) || 1;
            }

            // Add a visual "loading" state so the user knows the tap worked
            const originalContent = btn.innerHTML;
            btn.innerHTML = '<i data-lucide="loader-2" class="spin"></i>';
            if (typeof lucide !== 'undefined') lucide.createIcons();

            const formData = new FormData();
            formData.append('slug', slug);
            formData.append('qty', qty);

            fetch('/products/api/cart/add/', {
                method: 'POST',
                headers: { 'X-CSRFToken': getCsrfToken() },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                // Restore button text
                btn.innerHTML = originalContent;
                if (typeof lucide !== 'undefined') lucide.createIcons();

                if (data.ok) {
                    updateBadges(data.cart_count);
                    openCart(); // Automatically open drawer on add
                } else {
                    alert('Error adding to cart. Please try again.');
                }
            })
            .catch(err => {
                btn.innerHTML = originalContent;
                if (typeof lucide !== 'undefined') lucide.createIcons();
                console.error('Cart Error:', err);
            });
        }
    });

    function updateBadges(count) {
        cartBadges.forEach(badge => {
            if (!badge) return;
            badge.textContent = count;
            badge.style.display = count > 0 ? 'inline-block' : 'none';
        });
    }

    // Get CSRF Token from Cookie OR Meta Tag
    function getCsrfToken() {
        // First try cookie
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
        // Fallback to meta tag
        if (!cookieValue) {
            const meta = document.querySelector('meta[name="csrf-token"]');
            if (meta) cookieValue = meta.getAttribute('content');
        }
        return cookieValue;
    }
});