(() => {
    'use strict'

    const treeCreateLink = document.getElementById('tree-create');
    const newTreeForm = document.getElementById('new-tree-form');
    newTreeForm.addEventListener('submit', createTree);

    function createTree(event) {
        event.preventDefault();

        const url = `${document.location.origin}/api/v1/tree`;
        const treeName = event.target.elements.treeName.value;
        const payload = JSON.stringify({'name': treeName});
        const xhr = new XMLHttpRequest();

        xhr.open('POST', url);
        xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');
        xhr.responseType = 'json';
        xhr.send(payload);
        xhr.onload = function() {
            if (xhr.status === 200) {
                const tree = xhr.response;
                newTreeForm.querySelector('.btn-close').click();
                const newTreeLink = treeCreateLink.cloneNode();
                const treeUrl = `${document.location.origin}/ui/tree/${tree.id}/list`;
                newTreeLink.setAttribute('id', null);
                newTreeLink.innerHTML = `<a href="${treeUrl}" class="link-dark d-inline-flex text-decoration-none rounded">${tree.name}</a>`;
                treeCreateLink.parentNode.insertBefore(newTreeLink, treeCreateLink);
            }
        };
        xhr.onerror = function() {
            alert(`Network Error`);
        };
    }

})()