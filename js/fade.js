/* Search for any links with data-toggle set and configure them to toggle the
 * targetted section shown / hidden
 */
(function() {
    var toggles = document.querySelectorAll('a[data-toggle]');

    function toggleHandler(evt) {
        evt.preventDefault();
        const block = document.getElementById(evt.currentTarget.dataset.toggle);

        if (block.style.display === 'block') {
            block.style.display = 'none';
        }
        else {
            for (let other of toggles) {
                other = document.getElementById(other.dataset.toggle);
                other.style.display = 'none';
            }
            block.style.display = 'block';
        }
    }

    for (const toggle of toggles)
        toggle.addEventListener('click', toggleHandler);
})();
