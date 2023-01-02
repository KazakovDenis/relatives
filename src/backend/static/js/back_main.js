(() => {
    'use strict'

    const treeList = document.getElementById('tree-list');
    const createTreeLink = document.getElementById('tree-create');
    const sharedTreeList = document.getElementById('shared-tree-list');

    document.querySelectorAll('thead th span').forEach(elem => {
        elem.addEventListener('click', sortTable);

        const urlParams = new URLSearchParams(window.location.search);
        if (elem.dataset.field === urlParams.get('sort')) {
            elem.dataset.order = urlParams.get('order') ^ '1';
        }
    });

    getTrees();

    function getTrees() {
        const url = `${document.location.origin}/api/v1/tree`;
        const xhr = new XMLHttpRequest();

        xhr.open('GET', url);
        xhr.responseType = 'json';
        xhr.send();
        xhr.onload = function() {
            if (xhr.status === 200) {
                if (!xhr.response.length) {
                    sharedTreeList.parentElement.classList.remove('show');
                    return
                }

                xhr.response.forEach(userTree => {
                    const li = createLink(userTree);
                    if (userTree.is_owner) {
                      treeList.insertBefore(li, createTreeLink);
                    } else {
                      sharedTreeList.append(li);
                    }
                })
            }
        };
        xhr.onerror = function() {
            alert(`Network Error`);
        };
    }

    function createLink(userTree) {
        const treeUrl = `${document.location.origin}/ui/tree/${userTree.tree.id}/list`;
        const li = document.createElement('li');
        li.innerHTML = `<a href="${treeUrl}" class="link-dark d-inline-flex text-decoration-none rounded">${userTree.tree.name}</a>`;
        return li;
    }

    function sortTable(event) {
        event.preventDefault();

        const field = event.target.dataset.field;
        const order = event.target.dataset.order;
        const url = document.location.origin + document.location.pathname
        const urlParams = new URLSearchParams(window.location.search);

        urlParams.set('sort', field);
        urlParams.set('order', order);
        window.location.replace(`${url}?${urlParams.toString()}`);
    }
})()