// Page Transition Handling
document.addEventListener('DOMContentLoaded', function() {
    // Add fade-in class to body when page loads
    document.body.classList.add('fade-in');
    
    // Add stagger animation class to cards and list items
    const staggerItems = document.querySelectorAll('.card, .place-card, .review-card, .list-item');
    staggerItems.forEach(item => {
        item.classList.add('stagger-item');
    });
    
    // Create page loader element
    const loader = document.createElement('div');
    loader.className = 'page-loader';
    loader.innerHTML = '<div class="loader-spinner"></div>';
    document.body.appendChild(loader);
    
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
            
            // Show transition effect
            document.body.classList.add('page-transition');
            loader.classList.add('active');
            
            // Navigate after a short delay
            setTimeout(function() {
                window.location.href = link.href;
            }, 300);
        }
    });
    
    // Handle form submissions with transition
    document.querySelectorAll('form').forEach(form => {
        if (!form.hasAttribute('data-no-transition')) {
            form.addEventListener('submit', function(e) {
                // Don't apply transition to forms with AJAX submission
                if (!form.hasAttribute('data-ajax-submit')) {
                    document.body.classList.add('page-transition');
                    loader.classList.add('active');
                }
            });
        }
    });
    
    // Apply staggered animation to items when they enter viewport
    if ('IntersectionObserver' in window) {
        const appearOptions = {
            threshold: 0.1,
            rootMargin: "0px 0px -100px 0px"
        };
        
        const appearOnScroll = new IntersectionObserver(function(entries, observer) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('stagger-item');
                    observer.unobserve(entry.target);
                }
            });
        }, appearOptions);
        
        document.querySelectorAll('.appear-on-scroll').forEach(item => {
            appearOnScroll.observe(item);
        });
    }
});