/* Search for any links with data-map set and configure them to switch out the
 * contents of #map-title, #map-link and #map-image
 */
(function() {
    var map_title = document.querySelector('#map-title');
    var map_link = document.querySelector('a#map-link');
    var map_image = document.querySelector('img#map-image');
    var maps = document.querySelectorAll('a[data-map]');

    for (const map of maps) {
        map.addEventListener('click', function (evt) {
            evt.preventDefault();
            if (map_title) {
                map_title.textContent = evt.currentTarget.dataset.title;
            }
            map_link.href = 'img/' + evt.currentTarget.dataset.map + '.opt.svg';
            map_image.src = 'img/' + evt.currentTarget.dataset.map + '.jpg';
        });
    }
})();
