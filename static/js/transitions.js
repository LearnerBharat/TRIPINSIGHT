// Enhanced Page Transition Handling with Preloading
document.addEventListener('DOMContentLoaded', function() {
    // Cache for preloaded pages
    const pageCache = {};
    
    // Remove any transition classes that might be left from previous page
    document.body.classList.remove('page-transition');
    
    // Add fade-in class to body when page loads
    document.body.classList.add('fade-in');
    
    // Add stagger animation class to cards and list items with optimized timing
    const staggerItems = document.querySelectorAll('.card, .place-card, .review-card, .list-item, .experience-card');
    staggerItems.forEach((item, index) => {
        item.classList.add('stagger-item');
        // Limit animation delay to prevent too long animations
        const delay = Math.min(index, 9) * 0.03;
        item.style.animationDelay = `${delay}s`;
    });
    
    // Create page loader element if it doesn't exist
    let loader = document.querySelector('.page-loader');
    if (!loader) {
        loader = document.createElement('div');
        loader.className = 'page-loader';
        loader.innerHTML = '<div class="loader-spinner"></div>';
        document.body.appendChild(loader);
    }
    
    // Store the current page URL for back button handling
    if (window.history && window.history.replaceState) {
        const currentState = {
            url: window.location.href,
            title: document.title,
            wasBackButton: false
        };
        window.history.replaceState(currentState, document.title, window.location.href);
    }
    
    // Preload pages when hovering over links
    const preloadLinks = () => {
        const links = document.querySelectorAll('a:not([href^="#"]):not([href^="javascript:"]):not([download]):not([target])');
        
        links.forEach(link => {
            if (link.href && link.href.indexOf(window.location.origin) === 0) {
                link.addEventListener('mouseenter', () => {
                    const url = link.href;
                    
                    // Only preload if not already in cache
                    if (!pageCache[url]) {
                        const xhr = new XMLHttpRequest();
                        xhr.open('GET', url, true);
                        xhr.onload = function() {
                            if (xhr.status >= 200 && xhr.status < 400) {
                                pageCache[url] = xhr.responseText;
                                console.log('Preloaded:', url);
                            }
                        };
                        xhr.send();
                    }
                });
            }
        });
    };
    
    // Initialize preloading
    preloadLinks();
    
    // Refresh preload links when content changes (for dynamic content)
    const observer = new MutationObserver(preloadLinks);
    observer.observe(document.body, { childList: true, subtree: true });
    
    // Handle all internal link clicks for smooth transitions
    document.addEventListener('click', function(e) {
        // Find closest anchor tag if the click was on a child element
        const link = e.target.closest('a');
        
        // If it's an internal link (not external, not anchor, not javascript, not download)
        if (link && 
            link.href && 
            link.href.indexOf(window.location.origin) === 0 && 
            !link.href.includes('#') && 
            !link.href.includes('javascript:') &&
            !link.hasAttribute('download') &&
            !link.hasAttribute('target')) {
            
            e.preventDefault();
            
            // Get the target URL
            const targetUrl = link.href;
            
            // Store the current URL in history state
            if (window.history && window.history.pushState) {
                const state = {
                    url: targetUrl,
                    title: document.title,
                    wasBackButton: false
                };
                window.history.pushState(state, document.title, targetUrl);
            }
            
            // Show transition effect with transform for smoother animation
            document.body.classList.add('page-transition');
            
            // Check if the page is already in cache
            if (pageCache[targetUrl]) {
                // Use a shorter transition for cached pages
                setTimeout(() => {
                    window.location.href = targetUrl;
                }, 180);
            } else {
                // Only show loader for transitions that take longer than 120ms
                const loaderTimeout = setTimeout(function() {
                    loader.classList.add('active');
                }, 120);
                
                // Navigate after a short delay
                setTimeout(function() {
                    clearTimeout(loaderTimeout); // Clear the loader timeout
                    window.location.href = targetUrl;
                }, 250);
            }
        }
    });
    
    // Handle browser back/forward buttons with improved transitions
    window.addEventListener('popstate', function(event) {
        if (event.state) {
            // Mark this as a back button navigation
            event.state.wasBackButton = true;
            
            // Show a faster, smoother transition for back button
            document.body.classList.add('page-transition');
            
            // Check if the page is in cache for faster navigation
            const targetUrl = event.state.url;
            if (pageCache[targetUrl]) {
                // Ultra-fast transition for cached back navigation
                setTimeout(function() {
                    window.location.href = targetUrl;
                }, 80);
            } else {
                // Navigate to the previous page with a short delay
                setTimeout(function() {
                    window.location.href = targetUrl;
                }, 120);
            }
        }
    });
    
    // Handle form submissions with improved transitions
    document.querySelectorAll('form').forEach(form => {
        // Skip search forms and forms marked with data-no-transition
        if (!form.hasAttribute('data-no-transition') && 
            form.id !== 'searchForm' && 
            !form.classList.contains('search-form')) {
            
            form.addEventListener('submit', function(e) {
                // Don't apply transition to forms with AJAX submission
                if (!form.hasAttribute('data-ajax-submit')) {
                    // Add transition class for smooth fade-out
                    document.body.classList.add('page-transition');
                    
                    // Add a subtle transform effect during form submission
                    document.body.style.transform = 'translateY(-5px)';
                    
                    // Only show loader for submissions that take longer than 120ms
                    setTimeout(function() {
                        loader.classList.add('active');
                    }, 120);
                    
                    // Reset transform after transition completes
                    setTimeout(function() {
                        document.body.style.transform = '';
                    }, 300);
                }
            });
        }
    });
    
    // Apply enhanced staggered animation to items when they enter viewport
    if ('IntersectionObserver' in window) {
        const appearOptions = {
            threshold: 0.05,  // Trigger earlier
            rootMargin: "0px 0px -30px 0px" // Reduced margin for earlier animation
        };
        
        const appearOnScroll = new IntersectionObserver(function(entries, observer) {
            entries.forEach((entry, index) => {
                if (entry.isIntersecting) {
                    // Add a small random delay for more natural appearance
                    const randomDelay = Math.random() * 0.1;
                    setTimeout(() => {
                        entry.target.classList.add('stagger-item');
                        // Add subtle scale effect for more polish
                        entry.target.style.transition = 'transform 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94), opacity 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
                    }, randomDelay * 1000);
                    observer.unobserve(entry.target);
                }
            });
        }, appearOptions);
        
        // Observe all elements that should animate on scroll
        document.querySelectorAll('.appear-on-scroll, .section, .destination-card, .experience-card').forEach(item => {
            appearOnScroll.observe(item);
        });
        
        // Add smooth scroll behavior for anchor links
        document.querySelectorAll('a[href^="#"]:not([href="#"])').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const targetId = this.getAttribute('href');
                const targetElement = document.querySelector(targetId);
                
                if (targetElement) {
                    e.preventDefault();
                    window.scrollTo({
                        top: targetElement.offsetTop - 80, // Offset for fixed header
                        behavior: 'smooth'
                    });
                }
            });
        });
    }
});