// Modern navbar functionality with error handling
document.addEventListener('DOMContentLoaded', function() {
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
});