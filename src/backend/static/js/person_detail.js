(() => {
  'use strict'

  const treeId = document.getElementById('person-data').dataset.treeId;
  const personForm = document.getElementById('person-form');
  const createPersonButton = document.getElementById('create-person-button');
  const deletePersonForm = document.getElementById('delete-person-form');
  const foundRelativesElem = document.getElementById('found-relatives');
  const relativeForms = document.querySelectorAll('.relative-form');

  let addRelativeForm = document.getElementById('add-relative-form');
  let savedFiles = [];

  document.querySelector('#photos').addEventListener('change', readFiles);
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
  }, false);

  if (deletePersonForm) {
      deletePersonForm.addEventListener('submit', event => {
      event.preventDefault();
      const personId = personForm.dataset.personId;
      if (personId) deletePerson(personId);
    }, false);
  }

  if (addRelativeForm) {
    addRelativeForm.addEventListener('keyup', findRelatives);
    addRelativeForm.addEventListener('submit', addRelative);
  }

  relativeForms.forEach(form => form.addEventListener('submit', deleteRelative));

  function createPerson() {
    const createPersonUrl = `${document.location.origin}/api/v1/tree/${treeId}/persons`;
    const xhr = new XMLHttpRequest();

    xhr.open('POST', createPersonUrl);
    xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');
    xhr.responseType = 'json';
    xhr.send(getFormData());
    xhr.onload = function() {
        if (xhr.status === 201) {
          const person_id = xhr.response.id;
          window.location.replace(`${document.location.origin}/ui/tree/${treeId}/person/${person_id}`);
        }
    };
    xhr.onerror = function() {
        alert(`Network Error`);
    };
  }

  function updatePerson(personId) {
    const personUrl = `${document.location.origin}/api/v1/tree/${treeId}/persons/${personId}`;
    const xhr = new XMLHttpRequest();

    xhr.open('PATCH', personUrl);
    xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');
    xhr.responseType = 'json';
    xhr.send(getFormData());
    xhr.onload = function () {
      window.location.reload();
    };
    xhr.onerror = function() {
        alert(`Network Error`);
    };
  }

  function deletePerson(personId) {
    const personUrl = `${document.location.origin}/api/v1/tree/${treeId}/persons/${personId}`;
    const xhr = new XMLHttpRequest();

    xhr.open('DELETE', personUrl);
    xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');
    xhr.responseType = 'json';
    xhr.send();
    xhr.onload = function() {
        if (xhr.status === 200) {
          window.location.replace(`${document.location.origin}/ui/tree/${treeId}/list`);
        }
    };
    xhr.onerror = function() {
        alert(`Network Error`);
    };
  }

  function findRelatives(event) {
    if (event.target.value.length < 5) {
      addRelativeForm.querySelector('input').removeAttribute('data-relative-id');
      foundRelativesElem.innerHTML = '';
      return;
    }

    const query = event.target.value;
    const personId = personForm.dataset.personId;
    const personUrl = `${document.location.origin}/api/v1/tree/${treeId}/persons?q=${query}&exclude=${personId}`;
    const xhr = new XMLHttpRequest();

    xhr.open('GET', personUrl);
    xhr.responseType = 'json';
    xhr.send();
    xhr.onload = function() {
      foundRelativesElem.innerHTML = '';

      if (xhr.status === 200) {
        xhr.response.forEach(rel => {
          const newRelative = document.createElement('li');
          newRelative.classList.add('list-group-item', 'list-group-item-action');
          newRelative.setAttribute('data-relative-id', rel.id);
          newRelative.innerText = `${rel.surname} ${rel.name} ${rel.patronymic || ''}`;
          newRelative.addEventListener('click', event => {
            const newRelativeInput = addRelativeForm.querySelector('input');
            newRelativeInput.value = event.target.textContent;
            newRelativeInput.setAttribute('data-relative-id', event.target.dataset.relativeId);
            foundRelativesElem.innerHTML = '';
          })
          foundRelativesElem.append(newRelative);
        });
      }
    };
    xhr.onerror = function() {
        alert(`Network Error`);
    };

  }

  function addRelative(event) {
    event.preventDefault();
    const oldForm = event.target;

    if (!oldForm.checkValidity()) return;

    const relativeId = event.target.elements.fullName.dataset.relativeId;
    const url = `${document.location.origin}/api/v1/tree/${treeId}/relations`;
    const payload = JSON.stringify({
      'person_from': personForm.dataset.personId,
      'person_to': relativeId,
      'relation': event.target.elements.relation.value,
    });
    const xhr = new XMLHttpRequest();

    xhr.open('POST', url);
    xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');
    xhr.responseType = 'json';
    xhr.send(payload);
    xhr.onload = function() {
      if (xhr.status === 201) {
        oldForm.removeEventListener('submit', addRelative);
        oldForm.removeEventListener('keyup', findRelatives);
        oldForm.addEventListener('submit', deleteRelative);
        const oldButton = oldForm.querySelector('button');
        const formId = oldForm.getAttribute('id');
        oldForm.setAttribute('data-relative-id', relativeId);

        // replace this form with new empty
        addRelativeForm = oldForm.cloneNode(true);
        oldForm.removeAttribute('id');
        addRelativeForm.setAttribute('id', formId);
        addRelativeForm.addEventListener('keyup', findRelatives);
        addRelativeForm.addEventListener('submit', addRelative);
        addRelativeForm.elements.fullName.value = '';
        addRelativeForm.elements.relation.value = '';

        oldButton.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-person-plus" viewBox="0 0 16 16">\n' +
            '<path d="M6 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm2-3a2 2 0 1 1-4 0 2 2 0 0 1 4 0zm4 8c0 1-1 1-1 1H1s-1 0-1-1 1-4 6-4 6 3 6 4zm-1-.004c-.001-.246-.154-.986-.832-1.664C9.516 10.68 8.289 10 6 10c-2.29 0-3.516.68-4.168 1.332-.678.678-.83 1.418-.832 1.664h10z"/>\n' +
            '<path fill-rule="evenodd" d="M13.5 5a.5.5 0 0 1 .5.5V7h1.5a.5.5 0 0 1 0 1H14v1.5a.5.5 0 0 1-1 0V8h-1.5a.5.5 0 0 1 0-1H13V5.5a.5.5 0 0 1 .5-.5z"/>\n' +
            '</svg>';
        oldButton.classList.remove('btn-success');
        oldButton.classList.add('btn-danger');

        // insert new empty form after saved one
        foundRelativesElem.parentNode.insertBefore(addRelativeForm, foundRelativesElem);
      }
    };
    xhr.onerror = function() {
        alert(`Network Error`);
    };
  }

  function deleteRelative(event) {
    event.preventDefault();
    const relativeForm = event.target;
    const personFrom = personForm.dataset.personId;
    const personTo = relativeForm.dataset.relativeId;
    const url = `${document.location.origin}/api/v1/tree/${treeId}/persons/${personFrom}/relatives/${personTo}`;
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
      photos: savedFiles,
    });
  }

  function readFiles(event) {
    savedFiles = [];
    const files = Array.from(event.target.files);

    for (let i in files) {
      let file = files[i];

      if (!(file instanceof Blob)) continue;

      if (file.size > 5_242_880) {
        alert(`File is too large (max 5 Mb): ${file.name}`)
        continue
      }

      let reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = function() {
        savedFiles.push(reader.result);
      };
      reader.onerror = function() {
        console.log(reader.error);
      };
    }
  }

})()
