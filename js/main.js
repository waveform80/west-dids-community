$(document).ready(function() {
    $(document).foundation();
});

/* Append the "Back to top" link and add the event handlers to scroll back to
 * the top of the page, and fade it in/out based on scroll position
 */
(function() {
    let template = document.createElement('template');
    template.innerHTML =
        '<a href="#" class="btn-fancy" id="back-top">' +
            '<div class="solid-layer"></div>' +
            '<div class="border-layer"></div>' +
            '<div class="text-layer">' +
                '<img src="img/top_arrow.png" alt="Back to top">' +
            '</div>' +
        '</a>';
    document.body.appendChild(template.content);

    var back_top = document.querySelector('#back-top');

    back_top.addEventListener('click', function(evt) {
        evt.preventDefault();
        window.scroll({behavior: 'smooth', left: 0, top: 0});
    });

    window.addEventListener('scroll', function(evt) {
        if (window.scrollY > 600) {
            back_top.style.opacity = 1;
        }
        else {
            back_top.style.opacity = 0;
        }
    });
})();
