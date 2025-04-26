/**
 * First-time visitor modern UI redirect script
 */
(function() {
    // Only run this on the first visit
    if (!localStorage.getItem('ai_interview_visited')) {
        // Set visited flag
        localStorage.setItem('ai_interview_visited', 'true');
        
        // Set UI preference to modern
        localStorage.setItem('ai_interview_ui', 'modern');
        
        // Check if we're not already on a UI-specific page
        if (!window.location.href.includes('ui=')) {
            // Add modern UI parameter and redirect
            const separator = window.location.href.includes('?') ? '&' : '?';
            window.location.href = window.location.href + separator + 'ui=modern';
        }
    }
})();