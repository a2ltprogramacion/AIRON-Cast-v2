/**
 * A2LT Pro Smart Navbar - Logic
 * Features:
 * 1. Auto-hide on scroll down, Show on scroll up
 * 2. Glassmorphism injection after threshold
 * 3. Total hide when reaching the Footer (Captación Zone)
 */

function initA2LTProNavbar() {
    const header = document.getElementById('main-header');
    const footer = document.getElementById('contacto');
    if (!header) return;

    let lastScrollY = window.scrollY;
    const hideThreshold = 50;
    const scrollDelta = 10;

    window.addEventListener('scroll', () => {
        const currentScrollY = window.scrollY;

        // 1. Threshold & Glassmorphism
        if (currentScrollY > hideThreshold) {
            header.classList.add('bg-background/70', 'backdrop-blur-xl', 'border-b', 'border-white/10');
            header.classList.remove('bg-transparent', 'border-transparent');
        } else {
            header.classList.remove('bg-background/70', 'backdrop-blur-xl', 'border-b', 'border-white/10');
            header.classList.add('bg-transparent', 'border-transparent');
        }

        // 2. Auto-hide/Show Logic
        if (Math.abs(currentScrollY - lastScrollY) <= scrollDelta) return;

        if (currentScrollY > lastScrollY && currentScrollY > 100) {
            // Scrolling down - Hide
            header.style.transform = 'translateY(-110%)';
        } else {
            // Scrolling up - Show
            header.style.transform = 'translateY(0)';
        }

        // 3. Footer Awareness (Absolute Hide)
        if (footer) {
            const footerRect = footer.getBoundingClientRect();
            if (footerRect.top <= 100) {
                header.style.opacity = '0';
                header.style.pointerEvents = 'none';
            } else {
                header.style.opacity = '1';
                header.style.pointerEvents = 'auto';
            }
        }

        lastScrollY = currentScrollY;
    }, { passive: true });
}

document.addEventListener('DOMContentLoaded', initA2LTProNavbar);
