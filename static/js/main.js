document.addEventListener('DOMContentLoaded', () => {
    // 1. Intersection Observer for fade-in animations on scroll
    const fadeElements = document.querySelectorAll('.fade-in');
    
    const fadeObserverOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };
    
    const fadeObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, fadeObserverOptions);
    
    fadeElements.forEach(el => fadeObserver.observe(el));

    // 2. Interactive Dropdowns in the "Trusted Marketplace" section
    const dropdowns = document.querySelectorAll('.dropdown-placeholder');
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('click', function(e) {
            e.preventDefault();
            const icon = this.querySelector('i');
            const menu = this.nextElementSibling;
            
            if (menu.classList.contains('active')) {
                menu.classList.remove('active');
                icon.classList.remove('fa-caret-up');
                icon.classList.add('fa-caret-down');
                this.style.backgroundColor = 'rgba(0,0,0,0.05)';
                this.style.borderColor = 'var(--text-dark)';
                this.style.borderRadius = '8px';
            } else {
                // Close others
                document.querySelectorAll('.dropdown-menu').forEach(m => m.classList.remove('active'));
                document.querySelectorAll('.dropdown-placeholder i').forEach(i => {
                    i.classList.remove('fa-caret-up');
                    i.classList.add('fa-caret-down');
                });
                
                menu.classList.add('active');
                icon.classList.remove('fa-caret-down');
                icon.classList.add('fa-caret-up');
                this.style.backgroundColor = 'white';
                this.style.borderColor = 'var(--border-color)';
                this.style.borderRadius = '8px 8px 0 0';
            }
        });
    });

    // View All Button Logic
    const viewAllBtn = document.getElementById('view-all-btn');
    const viewAllMenu = document.getElementById('view-all-menu');
    if (viewAllBtn && viewAllMenu) {
        viewAllBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const icon = this.querySelector('i');
            if (viewAllMenu.style.display === 'block') {
                viewAllMenu.style.display = 'none';
                icon.classList.remove('fa-chevron-up');
                icon.classList.add('fa-chevron-down');
            } else {
                viewAllMenu.style.display = 'block';
                icon.classList.remove('fa-chevron-down');
                icon.classList.add('fa-chevron-up');
            }
        });
    }

    // 3. Dynamic "Just Happened" badge
    const badge = document.querySelector('.just-happened');
    const matches = [
        "🤝 JUST HAPPENED New match",
        "🚀 Python lesson scheduled!",
        "🎨 Logo design traded!",
        "💡 Marketing tip shared!"
    ];
    let matchIndex = 0;
    
    if (badge) {
        setInterval(() => {
            matchIndex = (matchIndex + 1) % matches.length;
            badge.style.opacity = 0;
            setTimeout(() => {
                badge.innerText = matches[matchIndex];
                badge.style.opacity = 1;
            }, 500);
        }, 5000);
        
        // Add transition for opacity
        badge.style.transition = 'opacity 0.5s ease';
    }

    // 4. Hover effect on recent requests cards
    const requests = document.querySelectorAll('.request-item');
    requests.forEach(req => {
        req.addEventListener('mouseenter', () => {
            req.style.transform = 'translateX(-10px)';
            req.style.backgroundColor = 'rgba(168, 85, 247, 0.1)';
            req.style.transition = 'all 0.3s ease';
        });
        req.addEventListener('mouseleave', () => {
            req.style.transform = 'translateX(0)';
            req.style.backgroundColor = 'rgba(0,0,0,0.05)';
        });
    });
});
