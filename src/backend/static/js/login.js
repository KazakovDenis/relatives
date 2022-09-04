document.addEventListener('DOMContentLoaded', function() {
    let button = document.getElementById('sign-in-button');
    if (document.location.href.includes('signup')) {
        button.addEventListener('click', signup);
    } else {
        button.addEventListener('click', login);
    }
});

let loginUrl = `${document.location.origin}/api/v1/auth/login`;
let signupUrl = `${document.location.origin}/api/v1/auth/signup`;

function redirectToList() {
    window.location.replace(`${document.location.origin}/ui/tree/list`);
}

function login() {
    let email = document.getElementById('email-input').value;
    let password = document.getElementById('password-input').value;

    let xhr = new XMLHttpRequest();
    xhr.open('GET', `${loginUrl}?email=${email}&password=${password}`);
    xhr.send();
    xhr.onload = function() {
        if (xhr.status === 200) {
            redirectToList();
        } else {
            alert(`Bad credentials`);
        }
    };
    xhr.onerror = function() {
        alert(`Network Error`);
    };
}

function signup() {
    let email = document.getElementById('email-input').value;
    let password = document.getElementById('password-input').value;
    let payload = JSON.stringify({
      email,
      password
    });

    let xhr = new XMLHttpRequest();
    xhr.open('POST', signupUrl);
    xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');
    xhr.send(payload);
    xhr.onload = function() {
        if (xhr.status === 200) {
            redirectToList();
        } else {
            alert(`Error`);
        }
    };
    xhr.onerror = function() {
        alert(`Network Error`);
    };
}
