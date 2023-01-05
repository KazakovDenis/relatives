(() => {
    'use strict'

    const shareTreeForm = document.getElementById('share-tree-form');
    shareTreeForm.addEventListener('submit', shareTree);

    const shareTreeButton = document.getElementById('share-button');
    if (shareTreeButton) shareTreeButton.addEventListener('click', getShareLink);

    function shareTree(event) {
        event.preventDefault();

        const treeId = event.target.dataset.treeId;
        const email = event.target.elements.email.value;
        const url = `${document.location.origin}/api/v1/tree/${treeId}/share`;
        const payload = JSON.stringify({'email': email});
        const xhr = new XMLHttpRequest();

        xhr.open('POST', url);
        xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');
        xhr.responseType = 'json';
        xhr.send(payload);
        xhr.onload = function() {
            if (xhr.status === 406) {
                alert(`${email} is not registered at Relatives.`)
            } else if (xhr.status === 409) {
                alert(`${email} has access to this tree already.`);
            } else if (xhr.status > 400) {
                alert('Forbidden');
            }
        };
        xhr.onerror = function() {
            alert(`Network Error`);
        };
    }

    function getShareLink(event) {
        const treeId = event.target.dataset.treeId;
        const url = `${document.location.origin}/api/v1/tree/${treeId}/share-link`;
        const xhr = new XMLHttpRequest();

        xhr.open('GET', url);
        xhr.responseType = 'json';
        xhr.send();
        xhr.onload = function() {
            const sharedWithList = document.getElementById('shared-with');
            sharedWithList.replaceChildren();

            xhr.response.shared_with.forEach(item => {
                const elem = document.createElement('li');
                elem.classList.add('list-group-item', 'd-flex', 'align-items-center', 'justify-content-between')
                elem.innerHTML = `${item.email}<button type="button" data-tree-id="${treeId}" data-email="${item.email}" class="btn">⨯</button>`;
                elem.lastChild.addEventListener('click', revokeAccess)
                sharedWithList.append(elem);
            })

            // copy share link logic
            const linkElem = document.getElementById('share-link');
            linkElem.textContent = xhr.response.link;

            linkElem.onclick = function(clickEvent) {
                clickEvent.preventDefault();
                navigator.clipboard.writeText(linkElem.textContent);
                alert('Copied!');
            }

            document.getElementById('copy-share-link').onclick = function(clickEvent) {
                clickEvent.preventDefault();
                navigator.clipboard.writeText(linkElem.textContent);
                alert('Copied!');
            }
        };
        xhr.onerror = function() {
            alert(`Network Error`);
        };
    }

    function revokeAccess(event) {
        const treeId = event.target.dataset.treeId;
        const email = event.target.dataset.email;

        const xhr = new XMLHttpRequest();

        xhr.open('POST', `${document.location.origin}/api/v1/tree/${treeId}/revoke-access`);
        xhr.responseType = 'json';
        xhr.send(email);
        xhr.onload = function() {
            event.target.parentNode.remove();
        }
        xhr.onerror = function() {
            alert(`Network Error`);
        };
    }

})()