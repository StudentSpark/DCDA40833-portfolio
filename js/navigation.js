/**
 * Hamburger Menu Navigation
 * Toggles mobile navigation menu on/off
 */

document.addEventListener('DOMContentLoaded', function() {
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    
    // AI-GENERATED: Only run hamburger menu code if elements exist on the page
    if (hamburger && navMenu) {
        // Toggle menu when hamburger is clicked
        hamburger.addEventListener('click', function() {
            hamburger.classList.toggle('active');
            navMenu.classList.toggle('active');
            
            // Update aria-expanded for accessibility
            const isExpanded = hamburger.classList.contains('active');
            hamburger.setAttribute('aria-expanded', isExpanded);
        });
        
        // Close menu when a nav link is clicked
        const navLinks = document.querySelectorAll('.nav-menu a');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                hamburger.classList.remove('active');
                navMenu.classList.remove('active');
                hamburger.setAttribute('aria-expanded', 'false');
            });
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            const isClickInsideNav = navMenu.contains(event.target);
            const isClickOnHamburger = hamburger.contains(event.target);
            
            if (!isClickInsideNav && !isClickOnHamburger && navMenu.classList.contains('active')) {
                hamburger.classList.remove('active');
                navMenu.classList.remove('active');
                hamburger.setAttribute('aria-expanded', 'false');
            }
        });
    }

    // ============================================
    // AI-GENERATED: Dark Mode Toggle Functionality
    // Enables switching between light and dark themes for comfortable viewing in low-light environments
    // ============================================
    
    const darkModeToggle = document.getElementById('darkModeToggle');
    const htmlElement = document.documentElement;
    
    // AI-GENERATED: Only run if dark mode toggle exists on the page
    if (darkModeToggle) {
        // Check for saved user preference in localStorage
        const savedTheme = localStorage.getItem('theme');
        
        // Apply saved theme or default to light mode
        if (savedTheme === 'dark') {
            htmlElement.classList.add('dark-mode');
            darkModeToggle.checked = true;
        }
        
        // Toggle dark mode when switch is clicked
        darkModeToggle.addEventListener('change', function() {
            if (this.checked) {
                htmlElement.classList.add('dark-mode');
                localStorage.setItem('theme', 'dark');
            } else {
                htmlElement.classList.remove('dark-mode');
                localStorage.setItem('theme', 'light');
            }
        });
    }
    // ============================================
    // END AI-GENERATED CODE
    // ============================================
// Implemetation of dark mode functionality. If it has a darkmode switch, check for a saved theme, in this case 'dark'. Then switch to it when button is toggled, otherwise use default.
// I understand the basic concepts of how this works, but I have some difficulty fully understanding the syntax. I also had no idea about the localStorage or the preset themes have.
});
