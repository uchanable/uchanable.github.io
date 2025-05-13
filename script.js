document.addEventListener('DOMContentLoaded', function() {
    // Load sidebar content
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        fetch('sidebar.html')
            .then(response => response.text())
            .then(data => {
                sidebar.innerHTML = data;
                // Add 3D effect to profile image after sidebar is loaded
                initProfileImage3DEffect();
            })
            .catch(error => {
                console.error('Error loading sidebar:', error);
            });
    }
    
    // Activate fade-in animations for elements with class 'fade-in'
    const fadeElements = document.querySelectorAll('.fade-in');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            // When element is in view
            if (entry.isIntersecting) {
                // Add animation
                entry.target.style.animation = 'fadeIn 0.6s forwards';
                // Stop observing after animation is triggered
                observer.unobserve(entry.target);
            }
        });
    }, {
        root: null, // Use viewport as root
        threshold: 0.1, // Trigger when 10% of element is visible
        rootMargin: '0px 0px -50px 0px' // Adjust trigger point
    });
    
    // Observe all fade-in elements
    fadeElements.forEach(element => {
        observer.observe(element);
    });
    
    // Handle sidebar height on mobile
    function adjustSidebar() {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            if (window.innerWidth <= 1024) {
                sidebar.style.height = 'auto';
            } else {
                sidebar.style.height = 'calc(100vh - 100px)';
            }
        }
    }
    
    // Initial call
    adjustSidebar();
    
    // Add resize event listener
    window.addEventListener('resize', adjustSidebar);
    
    // Handle active navigation state
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const linkPage = link.getAttribute('href');
        if (linkPage === currentPage) {
            link.classList.add('active');
        }
    });
    
    // Initialize 3D effect for profile image
    function initProfileImage3DEffect() {
        // Add Pokemon card-like holographic effect
        const profileImage = document.querySelector('.profile-image');
        if (profileImage) {
            profileImage.addEventListener('mousemove', function(e) {
                const container = this.querySelector('.profile-image-container');
                const overlay = this.querySelector('.holographic-overlay');
                
                // Get position of mouse relative to the container
                const rect = this.getBoundingClientRect();
                const x = (e.clientX - rect.left) / rect.width;
                const y = (e.clientY - rect.top) / rect.height;
                
                // Calculate rotation (more limited for subtlety)
                const rotateX = (0.5 - y) * 10; // -5 to 5 degrees
                const rotateY = (x - 0.5) * 10; // -5 to 5 degrees
                
                // Apply rotation
                container.style.transform = `perspective(800px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
                
                // Update holographic effect based on angle
                const shine = `linear-gradient(
                    ${135 + rotateY * 5}deg, 
                    rgba(255,255,255,0) 0%,
                    rgba(255,255,255,0.1) 10%, 
                    rgba(255,255,255,0.3) ${20 + rotateX}%, 
                    rgba(255,255,255,0.1) ${30 + rotateX * 2}%, 
                    rgba(255,255,255,0) 50%
                )`;
                overlay.style.background = shine;
            });
            
            // Reset when mouse leaves
            profileImage.addEventListener('mouseleave', function() {
                const container = this.querySelector('.profile-image-container');
                const overlay = this.querySelector('.holographic-overlay');
                
                // Smooth transition back to normal
                container.style.transition = 'transform 0.6s ease-out';
                container.style.transform = 'perspective(800px) rotateX(0) rotateY(0) scale3d(1, 1, 1)';
                overlay.style.background = 'none';
                
                // Remove transition after reset
                setTimeout(() => {
                    container.style.transition = '';
                }, 600);
            });
            
            // Remove transition on mouse enter for responsiveness
            profileImage.addEventListener('mouseenter', function() {
                const container = this.querySelector('.profile-image-container');
                container.style.transition = 'none';
            });
        }
    }
});