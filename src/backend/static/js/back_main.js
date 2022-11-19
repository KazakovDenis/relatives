(() => {
    'use strict'

    const treeList = document.getElementById('tree-list');
    const createTreeLink = document.getElementById('tree-create');
    const sharedTreeList = document.getElementById('shared-tree-list');

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
})()