document.addEventListener("DOMContentLoaded", function() {
    // Function to detect user's preferred color scheme
    function detectColorScheme() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        } else {
            return 'light';
        }
    }

    // Load appropriate CSS based on color scheme
    var colorScheme = detectColorScheme();
    var siteCss = '/static/css/site-' + colorScheme + '.css';
    var dashboardCss = '/static/css/imprint-' + colorScheme + '.css';
    document.getElementById('site-css').setAttribute('href', siteCss);
    document.getElementById('imprint-css').setAttribute('href', dashboardCss);

    // Send color scheme to Flask
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/update_color_scheme", true);
    xhr.setRequestHeader('Content-Type', 'application/json; charset=utf-8');
    xhr.send(JSON.stringify({color_scheme: colorScheme}));
});

// Function to toggle menu visibility
function toggleMenu() {
    var menu = document.getElementById("navbar-mobile");
    menu.style.display = menu.style.display === "none" ? "block" : "none";

    // Toggle section visibility based on menu visibility
    var sections = document.querySelectorAll("section");
    sections.forEach(function(section) {
        section.style.display = menu.style.display === "none" ? "block" : "none";
    });
}

// Hide menu on page load
document.addEventListener("DOMContentLoaded", function() {
    var menu = document.getElementById("navbar-mobile");
    menu.style.display = "none";

    // Show sections by default
    var sections = document.querySelectorAll("section");
    sections.forEach(function(section) {
        section.style.display = "block";
    });
});