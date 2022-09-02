document.addEventListener('DOMContentLoaded', function() {
    let button = document.getElementById('sign-in-button');
    button.addEventListener('click', login);
});

let loginUrl = `${document.location.origin}/api/v1/auth/login`;

function login() {
    let email = document.getElementById('email-input').value;
    let password = document.getElementById('password-input').value;

    let xhr = new XMLHttpRequest();
    xhr.open('GET', `${loginUrl}?email=${email}&password=${password}`);
    xhr.send();
    xhr.onload = function() {
        if (xhr.status === 200) {
            window.location.replace(`${document.location.origin}/ui/tree/list`);
        } else {
            alert(`Bad credentials`);
        }
    };
    xhr.onerror = function() {
        alert(`Network Error`);
    };
}
