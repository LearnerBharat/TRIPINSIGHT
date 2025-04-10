// Enhanced Page Transition Handling with Preloading - Optimized for Smoother Experience
// Function to normalize URLs by handling trailing slashes consistently
function normalizeUrl(url) {
    // Remove trailing slash if it exists (except for root URL)
    if (url.length > 1 && url.endsWith('/')) {
        return url.slice(0, -1);
    }
    return url;
}

document.addEventListener('DOMContentLoaded', function() {
    // Cache for preloaded pages
    const pageCache = {};
    
    // Remove any transition classes that might be left from previous page
    document.body.classList.remove('page-transition');
    
    // Add fade-in class to body when page loads with a slight delay for better rendering
    setTimeout(() => {
        document.body.classList.add('fade-in');
    }, 10);
    
    // Add stagger animation class to cards and list items with optimized timing
    const staggerItems = document.querySelectorAll('.card, .place-card, .review-card, .list-item, .experience-card, .destination-card, .attraction-card, .poi-item');
    staggerItems.forEach((item, index) => {
        item.classList.add('stagger-item');
        // Limit animation delay to prevent too long animations
        const delay = Math.min(index, 9) * 0.03;
        item.style.animationDelay = `${delay}s`;
    });
    
    // Create page loader element if it doesn't exist - improved version with better visibility
    let loader = document.querySelector('.page-loader');
    if (!loader) {
        loader = document.createElement('div');
        loader.className = 'page-loader';
        document.body.appendChild(loader);
    }
    
    // Create inline loaders for content that needs it
    document.querySelectorAll('[data-loading="true"]').forEach(el => {
        const dotLoader = document.createElement('div');
        dotLoader.className = 'dot-loader';
        dotLoader.innerHTML = '<span></span><span></span><span></span>';
        el.appendChild(dotLoader);
    });
    
    // Store the current page URL for back button handling
    if (window.history && window.history.replaceState) {
        // Normalize URL to handle trailing slash issues
        const currentUrl = window.location.href;
        const normalizedUrl = normalizeUrl(currentUrl);
        
        // Store both versions of the URL to handle trailing slash issues
        const currentState = {
            url: currentUrl,
            normalizedUrl: normalizedUrl,
            title: document.title,
            wasBackButton: false
        };
        window.history.replaceState(currentState, document.title, window.location.href);
    }
    
    // Preload pages when hovering over links - optimized to reduce unnecessary requests
    const preloadLinks = () => {
        // Only select links that are likely to be navigated to
        const links = document.querySelectorAll('a.card-link, a.nav-link, .destination-card a, .filter-item, .state-filter-btn, .breadcrumb a, .tab-button');
        
        links.forEach(link => {
            if (link.href && link.href.indexOf(window.location.origin) === 0 && 
                !link.href.includes('#') && 
                !link.hasAttribute('download') && 
                !link.hasAttribute('target')) {
                
                // Use mouseenter for desktop and touchstart for mobile
                link.addEventListener('mouseenter', () => {
                    const url = link.href;
                    
                    // Only preload if not already in cache and not the current page
                    if (!pageCache[url] && url !== window.location.href) {
                        // Use a small delay to avoid preloading links that are just being passed over
                        const preloadTimeout = setTimeout(() => {
                            const xhr = new XMLHttpRequest();
                            xhr.open('GET', url, true);
                            xhr.onload = function() {
                                if (xhr.status >= 200 && xhr.status < 400) {
                                    pageCache[url] = xhr.responseText;
                                }
                            };
                            xhr.send();
                        }, 100);
                        
                        // Cancel the preload if the mouse leaves quickly
                        link.addEventListener('mouseleave', () => {
                            clearTimeout(preloadTimeout);
                        }, { once: true });
                    }
                });
            }
        });
    };
    
    // Initialize preloading
    preloadLinks();
    
    // Refresh preload links when content changes (for dynamic content) - with throttling
    let preloadTimeout;
    const observer = new MutationObserver(() => {
        clearTimeout(preloadTimeout);
        preloadTimeout = setTimeout(preloadLinks, 500);
    });
    observer.observe(document.body, { childList: true, subtree: true });
    
    // Handle all internal link clicks for smooth transitions
    document.addEventListener('click', function(e) {
        // Find closest anchor tag if the click was on a child element
        const link = e.target.closest('a');
        
        // If it's an internal link
        if (link && 
            link.href && 
            link.href.indexOf(window.location.origin) === 0 && 
            !link.href.includes('javascript:') &&
            !link.hasAttribute('download') &&
            !link.hasAttribute('target')) {
            
            // Skip transition for logout links to ensure proper session clearing
            if (link.href.includes('/logout/') || link.classList.contains('logout-button')) {
                return; // Let the browser handle the logout link normally
            }
            
            // Handle hash links differently - let the browser handle them normally
            // This ensures proper tab switching and back button functionality
            if (link.href.includes('#')) {
                // If it's a hash link on the same page, let the browser handle it
                if (link.href.split('#')[0] === window.location.href.split('#')[0]) {
                    return;
                }
            }
            
            e.preventDefault();
            
            // Get the target URL and normalize it
            const targetUrl = link.href;
            const normalizedTargetUrl = normalizeUrl(targetUrl);
            
            // Store the current URL in history state
            if (window.history && window.history.pushState) {
                // Store both the target URL and the current URL to handle trailing slash issues
                const state = {
                    url: targetUrl,
                    normalizedUrl: normalizedTargetUrl,
                    previousUrl: window.location.href,
                    normalizedPreviousUrl: normalizeUrl(window.location.href),
                    title: document.title,
                    wasBackButton: false
                };
                window.history.pushState(state, document.title, targetUrl);
            }
            
            // Show transition effect with transform for smoother animation
            document.body.classList.add('page-transition');
            
            // Show loader immediately for better UX
            loader.classList.add('active');
            
            // Check if the page is already in cache
            if (pageCache[targetUrl]) {
                // Use a shorter transition for cached pages
                setTimeout(() => {
                    window.location.href = targetUrl;
                }, 120); // Faster for cached pages
            } else {
                // Navigate after a short delay - enough for transition but not too slow
                setTimeout(function() {
                    window.location.href = targetUrl;
                }, 180);
            }
        }
    });
    
    // Handle browser back/forward buttons with improved transitions
    window.addEventListener('popstate', function(event) {
        // Check if the URL has a hash - if so, we're just changing tabs, not pages
        if (window.location.hash) {
            // Don't reload the page for hash changes - the tab handlers will take care of this
            return;
        }
        
        // Normalize the current URL to handle trailing slash consistently
        const normalizedCurrentUrl = normalizeUrl(window.location.href);
        
        // If we're just navigating between URLs that differ only by trailing slash,
        // we should navigate to the actual previous page instead
        if (event.state) {
            // Mark this as a back button navigation
            event.state.wasBackButton = true;
            
            // Show a faster, smoother transition for back button
            document.body.classList.add('page-transition');
            
            // Show loader for consistency
            loader.classList.add('active');
            
            // Get the target URL from history state
            let targetUrl = event.state.url;
            
            // Normalize the target URL to handle trailing slash consistently
            const normalizedTargetUrl = normalizeUrl(targetUrl);
            
            // Check if we need to go back further (in case of trailing slash issue)
            if (normalizedTargetUrl === normalizedCurrentUrl) {
                // We're just toggling between slash/no-slash versions of the same URL
                // Go back one more step in history
                window.history.back();
                return;
            }
            
            // Check if the page is in cache for faster navigation
            if (pageCache[targetUrl]) {
                // Ultra-fast transition for cached back navigation
                setTimeout(function() {
                    window.location.href = targetUrl;
                }, 80); // Faster but still smooth
            } else {
                // Navigate to the previous page with a short delay
                setTimeout(function() {
                    window.location.href = targetUrl;
                }, 120); // Faster but still smooth
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
                    
                    // Show loader immediately for better feedback
                    loader.classList.add('active');
                    
                    // Add submit button feedback
                    const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
                    if (submitBtn) {
                        // Store original text
                        const originalText = submitBtn.innerHTML;
                        
                        // Add loading state
                        submitBtn.disabled = true;
                        submitBtn.classList.add('submitting');
                        
                        // If it's not an input element, we can change the content
                        if (submitBtn.tagName.toLowerCase() !== 'input') {
                            submitBtn.innerHTML = '<div class="dot-loader"><span></span><span></span><span></span></div>';
                        }
                        
                        // Reset button after timeout (in case form submission fails)
                        setTimeout(() => {
                            if (document.body.contains(submitBtn)) {
                                submitBtn.disabled = false;
                                submitBtn.classList.remove('submitting');
                                if (submitBtn.tagName.toLowerCase() !== 'input') {
                                    submitBtn.innerHTML = originalText;
                                }
                            }
                        }, 5000);
                    }
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