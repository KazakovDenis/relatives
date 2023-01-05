document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('sign-in-form');
    if (document.location.href.includes('signup')) {
        form.addEventListener('submit', signup);
    } else {
        form.addEventListener('submit', login);
    }
});

let loginUrl = `${document.location.origin}/api/v1/auth/login`;
let signupUrl = `${document.location.origin}/api/v1/auth/signup`;


function login(event) {
    event.preventDefault();

    const email = document.getElementById('email-input').value;
    const password = document.getElementById('password-input').value;
    const urlParams = new URLSearchParams(window.location.search);
    const next = urlParams.get('next');

    let xhr = new XMLHttpRequest();
    xhr.open('GET', `${loginUrl}?email=${email}&password=${password}`);
    xhr.send();
    xhr.onload = function() {
        if (xhr.status === 200) {
            window.location.replace(next || `${document.location.origin}/ui/welcome`);
        } else {
            alert(`Bad credentials`);
        }
    };
    xhr.onerror = function() {
        alert(`Network Error`);
    };
}

function signup(event) {
    event.preventDefault();

    const email = document.getElementById('email-input').value;
    const password = document.getElementById('password-input').value;
    const urlParams = new URLSearchParams(window.location.search);
    const next = urlParams.get('next');
    let payload = JSON.stringify({
      email,
      password
    });

    let xhr = new XMLHttpRequest();
    xhr.open('POST', signupUrl);
    xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');
    xhr.responseType = 'json';
    xhr.send(payload);
    xhr.onload = function() {
        if (xhr.status === 201) {
            window.location.replace(next || `${document.location.origin}/ui/verify-email`);
        } else {
            alert(`Bad credentials`);
        }
    };
    xhr.onerror = function() {
        alert(`Network Error`);
    };
}
