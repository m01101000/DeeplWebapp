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
    var themeCss = '/static/css/login-' + colorScheme + '.css';
    document.getElementById('theme-css').setAttribute('href', themeCss);

    // Send color scheme to Flask
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/update_color_scheme", true);
    xhr.setRequestHeader('Content-Type', 'application/json; charset=utf-8');
    xhr.send(JSON.stringify({color_scheme: colorScheme}));
});