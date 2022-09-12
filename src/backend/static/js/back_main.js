(() => {
    'use strict'

    const treeList = document.getElementById('tree-list');
    const createTreeLink = document.getElementById('tree-create');

    getTrees();

    function getTrees() {
        const url = `${document.location.origin}/api/v1/tree`;
        const xhr = new XMLHttpRequest();

        xhr.open('GET', url);
        xhr.responseType = 'json';
        xhr.send();
        xhr.onload = function() {
            if (xhr.status === 200) {
              xhr.response.forEach(tree => {
                  const treeUrl = `${document.location.origin}/ui/tree/${tree.id}/list`;
                  const li = document.createElement('li');
                  li.innerHTML = `<a href="${treeUrl}" class="link-dark d-inline-flex text-decoration-none rounded">${tree.name}</a>`;
                  treeList.insertBefore(li, createTreeLink);
              })
            }
        };
        xhr.onerror = function() {
            alert(`Network Error`);
        };
    }

})()