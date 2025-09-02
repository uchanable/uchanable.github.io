// Scroll Animation Script
document.addEventListener('DOMContentLoaded', function() {
    // Add animation classes to sections
    const sections = document.querySelectorAll('section');
    sections.forEach((section, index) => {
        section.classList.add('fade-in-section');
        section.style.animationDelay = `${index * 0.1}s`;
    });

    // Intersection Observer for scroll animations
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                
                // Animate table rows if present
                const tableRows = entry.target.querySelectorAll('.info-table tr');
                tableRows.forEach((row, index) => {
                    setTimeout(() => {
                        row.classList.add('slide-in');
                    }, index * 50);
                });

                // Animate list items if present
                const listItems = entry.target.querySelectorAll('li');
                listItems.forEach((item, index) => {
                    setTimeout(() => {
                        item.classList.add('fade-in');
                    }, index * 50);
                });
            }
        });
    }, observerOptions);

    // Observe all sections
    sections.forEach(section => {
        observer.observe(section);
    });
    
    // Add animation to illustration container
    const illustrationContainer = document.querySelector('.illustration-container');
    if (illustrationContainer) {
        illustrationContainer.classList.add('fade-in-section');
        observer.observe(illustrationContainer);
    }

    // Smooth parallax effect for header
    let ticking = false;
    function updateParallax() {
        const scrolled = window.pageYOffset;
        const header = document.querySelector('header');
        const speed = 0.5;
        
        if (header) {
            header.style.transform = `translateY(${scrolled * speed}px)`;
        }
        ticking = false;
    }

    function requestTick() {
        if (!ticking) {
            window.requestAnimationFrame(updateParallax);
            ticking = true;
        }
    }

    window.addEventListener('scroll', requestTick);

    // Add ripple effect to register button
    const registerBtn = document.querySelector('.register-btn');
    if (registerBtn) {
        registerBtn.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            ripple.classList.add('ripple');
            this.appendChild(ripple);

            const x = e.clientX - e.target.offsetLeft;
            const y = e.clientY - e.target.offsetTop;

            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;

            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    }

    // Animate language switcher on hover
    const langLinks = document.querySelectorAll('.language-switcher a');
    langLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.05)';
        });
        link.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Progressive content reveal
    const contentPlaceholders = document.querySelectorAll('.content-placeholder');
    contentPlaceholders.forEach(placeholder => {
        const children = Array.from(placeholder.children);
        children.forEach((child, index) => {
            child.style.opacity = '0';
            child.style.transform = 'translateY(20px)';
            child.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            child.style.transitionDelay = `${index * 0.1}s`;
        });
    });

    // Trigger content reveal when visible
    const contentObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const children = Array.from(entry.target.children);
                children.forEach(child => {
                    child.style.opacity = '1';
                    child.style.transform = 'translateY(0)';
                });
            }
        });
    }, observerOptions);

    contentPlaceholders.forEach(placeholder => {
        contentObserver.observe(placeholder);
    });
});