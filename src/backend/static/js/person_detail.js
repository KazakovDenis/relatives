(() => {
  'use strict'

  const personForm = document.getElementById('person-form');
  const createPersonButton = document.getElementById('create-person-button');
  const deletePersonButton = document.getElementById('delete-person-button');
  const addRelativeForm = document.getElementById('add-relative-form');
  const relativeForms = document.querySelectorAll('.relative-form');

  createPersonButton.addEventListener('click', event => {
    if (personForm.checkValidity()) {
      const personId = personForm.dataset.personId;
      if (personId) {
        updatePerson(personId);
      } else {
        createPerson();
      }
    }
    personForm.classList.add('was-validated')
  }, false)

  deletePersonButton.addEventListener('click', event => {
    const personId = personForm.dataset.personId;
    if (personId) deletePerson(personId);
  }, false)

  relativeForms.forEach(form => {
    form.addEventListener('submit', event => {
      event.preventDefault();
      deleteRelative(event.target);
    });
  })

  function createPerson() {
    const createPersonUrl = `${document.location.origin}/api/v1/persons`;
    const xhr = new XMLHttpRequest();

    xhr.open('POST', createPersonUrl);
    xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');
    xhr.responseType = 'json';
    xhr.send(getFormData());
    xhr.onload = function() {
        if (xhr.status === 200) {
          const person_id = xhr.response.id;
          window.location.replace(`${document.location.origin}/ui/person/${person_id}`);
        }
    };
    xhr.onerror = function() {
        alert(`Network Error`);
    };
  }

  function updatePerson(personId) {
    const personUrl = `${document.location.origin}/api/v1/persons/${personId}`;
    const xhr = new XMLHttpRequest();

    xhr.open('PATCH', personUrl);
    xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');
    xhr.responseType = 'json';
    xhr.send(getFormData());
    xhr.onerror = function() {
        alert(`Network Error`);
    };
  }

  function deletePerson(personId) {
    const personUrl = `${document.location.origin}/api/v1/persons/${personId}`;
    const xhr = new XMLHttpRequest();

    xhr.open('DELETE', personUrl);
    xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');
    xhr.responseType = 'json';
    xhr.send();
    xhr.onload = function() {
        if (xhr.status === 200) {
          window.location.replace(`${document.location.origin}/ui/tree/list`);
        }
    };
    xhr.onerror = function() {
        alert(`Network Error`);
    };
  }

  function deleteRelative(relativeForm) {
    const personFrom = personForm.dataset.personId;
    const personTo = relativeForm.dataset.relativeId;
    const url = `${document.location.origin}/api/v1/persons/${personFrom}/relatives/${personTo}`;
    const xhr = new XMLHttpRequest();

    xhr.open('DELETE', url);
    xhr.responseType = 'json';
    xhr.send();
    xhr.onload = function() {
        if (xhr.status === 200) {
          relativeForm.remove();
        }
    };
    xhr.onerror = function() {
        alert(`Network Error`);
    };
  }

  function getFormData() {
    return JSON.stringify({
      name: personForm.elements.name.value,
      surname: personForm.elements.surname.value,
      patronymic: personForm.elements.patronymic.value,
      birthname: personForm.elements.birthname.value,
      birthdate: personForm.elements.birthdate.value,
      birthplace: personForm.elements.birthplace.value,
      gender: personForm.elements.gender.value,
      info: personForm.elements.info.value,
    });
  }

})()
