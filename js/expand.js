/* Search for any links with data-toggle set and configure them to toggle the
 * targetted section open and closed
 */
(function() {
    function collapse(elem) {
        elem.style.minHeight = null;
        elem.style.padding = null;
        elem.dataset.expanded = '';
    }

    function expand(elem) {
        elem.style.minHeight = '300px';
        elem.style.padding = '20px';
        elem.dataset.expanded = 'expanded';
    }

    var toggles = document.querySelectorAll('a[data-toggle]');

    function toggleHandler(evt) {
        evt.preventDefault();
        const block = document.getElementById(evt.currentTarget.dataset.toggle);

        if (Foundation.utils.is_small_only()) {
            // Fixed open in small screen
            block.scrollIntoView({behavior: 'smooth', block: 'start'});
        }
        else if (block.dataset.expanded) {
            // Expanded in larger screen
            collapse(block);
        }
        else {
            // Collapsed in larger screen
            for (let other of toggles) {
                other = document.getElementById(other.dataset.toggle);
                if (other !== block && other.dataset.expanded) collapse(other);
            }
            expand(block);
        }
    }

    function resizeThrottle() {
        if (!resizeTimeout) {
            resizeTimeout = setTimeout(function() {
                resizeTimeout = null;
                resizeHandler();
            }, 100);
        }
    }

    var resizeTimeout;
    var wasSmall = Foundation.utils.is_small_only();

    function resizeHandler() {
        const isSmall = Foundation.utils.is_small_only();
        if (!wasSmall && isSmall) {
            for (let elem of toggles) {
                elem = document.getElementById(elem.dataset.toggle);
                collapse(elem);
            }
            wasSmall = isSmall;
        }
        else if (wasSmall && !isSmall) {
            wasSmall = isSmall;
        }
    }

    for (const toggle of toggles)
        toggle.addEventListener('click', toggleHandler);

    window.addEventListener('resize', resizeThrottle, false);
})();
