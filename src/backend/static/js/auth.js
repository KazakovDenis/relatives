document.addEventListener('DOMContentLoaded', function() {
    let button = document.getElementById('logout-button');
    if (button) {
        button.addEventListener('click', logout);
    }
});

let logoutUrl = `${document.location.origin}/api/v1/auth/logout`;

function logout() {
    let xhr = new XMLHttpRequest();
    xhr.open('GET', logoutUrl);
    xhr.send();
    xhr.onload = function() {
        if (xhr.status === 202) {
            window.location.replace(document.location.origin);
        }
    };
    xhr.onerror = function() {
        alert(`Network Error`);
    };
}
