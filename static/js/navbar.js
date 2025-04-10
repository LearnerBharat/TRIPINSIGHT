// Modern navbar functionality with error handling
document.addEventListener('DOMContentLoaded', function() {
    // Wait a short time to ensure authentication class is added
    // Use a longer timeout for pages that might need more time to initialize
    setTimeout(function() {
        try {
            // Insert the navbar into all pages
            const body = document.body;
            // Check for authentication in multiple ways to ensure it works
            const isAuthenticated = document.body.classList.contains('user-authenticated');
            console.log('Authentication state:', isAuthenticated);

        // Create navbar element
        const navbar = document.createElement('nav');
        navbar.className = 'navbar';

        // Set navbar HTML content
        navbar.innerHTML = `
            <div class="container">
                <a href="/" class="nav-brand">
                    <i class="fas fa-compass"></i> TripInsight
                </a>
                <div class="nav-menu">
                    <div class="nav-links">
                        <a href="/" class="nav-link">Home</a>
                        <a href="/explore/" class="nav-link">Explore</a>
                        <a href="/stories/" class="nav-link">Travel Stories</a>
                        <a href="/about/" class="nav-link">About Us</a>
                    </div>
                    <div class="nav-actions">
                        ${
                            isAuthenticated ?
                            `
                            <a href="/profile/" class="nav-button">
                                <i class="fa-solid fa-user"></i>
                                <span>Profile</span>
                            </a>
                            <a href="/logout/" class="nav-button logout-button">
                                <i class="fa-solid fa-sign-out-alt"></i>
                                <span>Logout</span>
                            </a>
                            ` :
                            `
                            <a href="/signup/" class="nav-button nav-signup-button">
                                <i class="fa-solid fa-user-plus"></i>
                                <span>Sign Up</span>
                            </a>
                            <a href="/login/" class="nav-button nav-login-button">
                                <i class="fa-solid fa-sign-in-alt"></i>
                                <span>Login</span>
                            </a>
                            `
                        }
                    </div>
                </div>
            </div>
        `;

        // Create mobile menu toggle
        const mobileMenuToggle = document.createElement('div');
        mobileMenuToggle.className = 'mobile-menu-toggle';
        mobileMenuToggle.innerHTML = '<i class="fas fa-bars"></i>';

        // Create mobile menu
        const mobileMenu = document.createElement('div');
        mobileMenu.className = 'mobile-menu';
        mobileMenu.innerHTML = `
            <div class="nav-links">
                <a href="/" class="nav-link">Home</a>
                <a href="/explore/" class="nav-link">Explore</a>
                <a href="/stories/" class="nav-link">Travel Stories</a>
                <a href="/about/" class="nav-link">About Us</a>
            </div>
            <div class="nav-actions">
                ${
                    isAuthenticated ?
                    `
                    <a href="/profile/" class="nav-button">
                        <i class="fa-solid fa-user"></i>
                        <span>Profile</span>
                    </a>
                    <a href="/logout/" class="nav-button logout-button">
                        <i class="fa-solid fa-sign-out-alt"></i>
                        <span>Logout</span>
                    </a>
                    ` :
                    `
                    <a href="/signup/" class="nav-button nav-signup-button">
                        <i class="fa-solid fa-user-plus"></i>
                        <span>Sign Up</span>
                    </a>
                    <a href="/login/" class="nav-button nav-login-button">
                        <i class="fa-solid fa-sign-in-alt"></i>
                        <span>Login</span>
                    </a>
                    `
                }
            </div>
        `;

        // Insert elements at the beginning of the body
        body.insertBefore(mobileMenu, body.firstChild);
        body.insertBefore(mobileMenuToggle, body.firstChild);
        body.insertBefore(navbar, body.firstChild);

        // Mobile menu toggle functionality
        mobileMenuToggle.addEventListener('click', function() {
            mobileMenu.classList.toggle('active');

            // Change icon based on state
            const icon = this.querySelector('i');
            if (mobileMenu.classList.contains('active')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times');
                document.body.style.overflow = 'hidden'; // Prevent scrolling when menu is open
            } else {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
                document.body.style.overflow = ''; // Restore scrolling
            }
        });

        // Close menu when clicking on a link
        const mobileMenuLinks = mobileMenu.querySelectorAll('a');
        mobileMenuLinks.forEach(link => {
            link.addEventListener('click', function() {
                mobileMenu.classList.remove('active');

                // Reset icon
                const icon = mobileMenuToggle.querySelector('i');
                if (icon) {
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                }

                document.body.style.overflow = ''; // Restore scrolling
            });
        });

        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            if (mobileMenu.classList.contains('active') &&
                !mobileMenu.contains(event.target) &&
                !mobileMenuToggle.contains(event.target)) {
                mobileMenu.classList.remove('active');

                // Reset icon
                const icon = mobileMenuToggle.querySelector('i');
                if (icon) {
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                }

                document.body.style.overflow = ''; // Restore scrolling
            }
        });

        // Add active class to current page link
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-links a');

        navLinks.forEach(link => {
            const linkPath = link.getAttribute('href');

            // Handle exact matches
            if (currentPath === linkPath) {
                link.classList.add('active');
            }
            // Handle subpaths (like /details/1 should highlight the parent category)
            else if (linkPath !== '/' && currentPath.startsWith(linkPath)) {
                link.classList.add('active');
            }
            // Special case for home page
            else if (linkPath === '/' && (currentPath === '/' || currentPath === '/index.html')) {
                link.classList.add('active');
            }
        });

        // Add scroll effect to navbar
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });

        // Initialize search filters toggle if present
        const filterToggle = document.querySelector('.filter-toggle');
        const searchFilters = document.querySelector('.search-filters');

        if (filterToggle && searchFilters) {
            filterToggle.addEventListener('click', function() {
                searchFilters.classList.toggle('show');

                // Change icon based on state
                const icon = this.querySelector('i');
                if (searchFilters.classList.contains('show')) {
                    if (icon.classList.contains('fa-sliders-h')) {
                        icon.classList.remove('fa-sliders-h');
                        icon.classList.add('fa-times-circle');
                    }
                } else {
                    if (icon.classList.contains('fa-times-circle')) {
                        icon.classList.remove('fa-times-circle');
                        icon.classList.add('fa-sliders-h');
                    }
                }
            });
        }

        // Add padding to body to account for fixed navbar
        document.body.style.paddingTop = navbar.offsetHeight + 'px';

        // Adjust padding on window resize
        window.addEventListener('resize', function() {
            document.body.style.paddingTop = navbar.offsetHeight + 'px';
        });
        } catch (error) {
            console.error('Error initializing navbar:', error);
            // Fallback to a simple navbar if there's an error
            if (!document.querySelector('.navbar')) {
                const fallbackNavbar = document.createElement('nav');
                fallbackNavbar.className = 'navbar';
                fallbackNavbar.innerHTML = `
                    <div class="container">
                        <a href="/" class="nav-brand">
                            <i class="fas fa-compass"></i> TripInsight
                        </a>
                        <div class="nav-menu">
                            <div class="nav-links">
                                <a href="/" class="nav-link">Home</a>
                                <a href="/explore/" class="nav-link">Explore</a>
                                <a href="/stories/" class="nav-link">Travel Stories</a>
                                <a href="/about/" class="nav-link">About Us</a>
                            </div>
                        </div>
                    </div>
                `;
                document.body.insertBefore(fallbackNavbar, document.body.firstChild);
                
                // Add padding to body to account for fixed navbar
                document.body.style.paddingTop = fallbackNavbar.offsetHeight + 'px';
            }
        }
    }, 100); // Increased delay to ensure authentication class is added
});