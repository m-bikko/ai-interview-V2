/**
 * UI Switcher for AI Interview
 * Allows toggling between original UI and modern UI
 */

(function() {
    // Check if the user has a UI preference
    const currentUi = localStorage.getItem('ai_interview_ui') || 'original';
    
    // Apply the current UI choice
    document.documentElement.setAttribute('data-ui', currentUi);
    
    // If the modern UI is selected, load the modern stylesheet
    if (currentUi === 'modern') {
        const linkElement = document.getElementById('main-css');
        if (linkElement) {
            // Get the current href
            const currentHref = linkElement.getAttribute('href');
            
            // Replace main.css with modern.css
            if (currentHref.includes('main.css')) {
                linkElement.setAttribute('href', currentHref.replace('main.css', 'modern.css'));
            }
        }
    }
    
    // Create UI switcher button
    window.addEventListener('DOMContentLoaded', () => {
        // Create the switcher element
        const switcher = document.createElement('div');
        switcher.className = 'ui-switcher';
        switcher.innerHTML = `
            <button class="ui-switcher-button">
                <i class="fas fa-palette"></i>
                <span>Switch UI</span>
            </button>
            <div class="ui-options">
                <div class="ui-option ${currentUi === 'original' ? 'active' : ''}" data-ui="original">
                    <div class="ui-preview original-ui"></div>
                    <span>Original UI</span>
                </div>
                <div class="ui-option ${currentUi === 'modern' ? 'active' : ''}" data-ui="modern">
                    <div class="ui-preview modern-ui"></div>
                    <span>Modern UI</span>
                </div>
            </div>
        `;
        
        // Add styles for the switcher
        const style = document.createElement('style');
        style.textContent = `
            .ui-switcher {
                position: fixed;
                bottom: 20px;
                right: 20px;
                z-index: 9999;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            }
            
            .ui-switcher-button {
                background: #7C4DFF;
                color: white;
                border: none;
                padding: 12px 16px;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 8px;
                font-weight: 500;
                transition: all 0.2s ease;
            }
            
            .ui-switcher-button:hover {
                background: #6941C6;
                transform: translateY(-2px);
            }
            
            .ui-options {
                position: absolute;
                bottom: 60px;
                right: 0;
                background: white;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
                padding: 16px;
                display: none;
                width: 280px;
            }
            
            .ui-switcher.active .ui-options {
                display: block;
                animation: fadeIn 0.2s ease;
            }
            
            .ui-option {
                padding: 12px;
                border-radius: 8px;
                cursor: pointer;
                display: flex;
                flex-direction: column;
                align-items: center;
                margin-bottom: 8px;
                transition: all 0.2s ease;
            }
            
            .ui-option:last-child {
                margin-bottom: 0;
            }
            
            .ui-option:hover {
                background-color: #F3F4F6;
            }
            
            .ui-option.active {
                background-color: #F3F4F6;
                border: 2px solid #7C4DFF;
            }
            
            .ui-preview {
                width: 100%;
                height: 100px;
                border-radius: 6px;
                margin-bottom: 8px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            
            .original-ui {
                background: linear-gradient(to right, #4f46e5, #6366f1);
                border-top: 10px solid #1f2937;
            }
            
            .modern-ui {
                background: white;
                border: 1px solid #e0e0e0;
                position: relative;
            }
            
            .modern-ui:before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 10px;
                background: linear-gradient(to right, #7C4DFF, #536DFE);
                border-radius: 6px 6px 0 0;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
        `;
        
        document.head.appendChild(style);
        document.body.appendChild(switcher);
        
        // Toggle options visibility
        const switcherButton = switcher.querySelector('.ui-switcher-button');
        switcherButton.addEventListener('click', () => {
            switcher.classList.toggle('active');
        });
        
        // Handle option selection
        const options = switcher.querySelectorAll('.ui-option');
        options.forEach(option => {
            option.addEventListener('click', () => {
                // Get the UI choice
                const ui = option.getAttribute('data-ui');
                
                // Save preference
                localStorage.setItem('ai_interview_ui', ui);
                
                // Reload the page to apply changes
                window.location.reload();
            });
        });
        
        // Close when clicking outside
        document.addEventListener('click', (event) => {
            if (!switcher.contains(event.target)) {
                switcher.classList.remove('active');
            }
        });
    });
})();