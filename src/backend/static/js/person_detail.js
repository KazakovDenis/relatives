(() => {
  'use strict'

  let createUserUrl = `${document.location.origin}/api/v1/persons`;

  function createUser() {
    const form = document.getElementById('create-person-form');
    const payload = JSON.stringify({
      name: form.elements.name.value,
      surname: form.elements.surname.value,
      patronymic: form.elements.patronymic.value,
      birthdate: form.elements.birthdate.value,
      birthplace: form.elements.birthplace.value,
      gender: form.elements.gender.value,
      info: form.elements.info.value,
    });
    const xhr = new XMLHttpRequest();

    xhr.open('POST', createUserUrl);
    xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');
    xhr.send(payload);
    xhr.onload = function() {
        if (xhr.status === 200) {
            window.location.replace(`${document.location.origin}/ui/tree/list?page=1`);
        }
    };
    xhr.onerror = function() {
        alert(`Network Error`);
    };
  }

  const forms = document.querySelectorAll('.needs-validation');

  Array.from(forms).forEach(form => {
    form.addEventListener('submit', event => {
      event.preventDefault();
      event.stopPropagation();

      if (form.checkValidity()) {
        createUser();
      }
      form.classList.add('was-validated')
    }, false)
  })
})()
