(() => {
    'use strict'

    const shareTreeForm = document.getElementById('share-tree-form');
    shareTreeForm.addEventListener('submit', shareTree);

    function shareTree(event) {
        event.preventDefault();

        console.log(event.target);

        const treeId = event.target.dataset.treeId;
        const url = `${document.location.origin}/api/v1/tree/${treeId}/share`;
        const payload = JSON.stringify({'email': event.target.elements.email.value});
        const xhr = new XMLHttpRequest();

        xhr.open('POST', url);
        xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');
        xhr.responseType = 'json';
        xhr.send(payload);
        xhr.onload = function() {
            if (xhr.status >= 400) {
                alert('Network error');
            }
        };
        xhr.onerror = function() {
            alert(`Network Error`);
        };
    }
})()