document.addEventListener("DOMContentLoaded", function() {
    retrieveNodes();
    document.getElementById("cyto-download").addEventListener("click", download)
});


let nodes, cyto;
let url = `${document.location.origin}/api/v1/tree/1/scheme`;


function retrieveNodes() {
    let xhr = new XMLHttpRequest();
    xhr.open('GET', url);
    xhr.send();
    xhr.onload = function() {
        if (xhr.status === 200) {
            parseResponse(xhr.response);
            buildTree();
        } else if (xhr.status < 500) {
            alert(`Server Error`);
        } else {
            alert(`Bad request`);
        }
    };
    xhr.onerror = function() {
        alert(`Network Error`);
    };
}


function parseResponse(response) {
    let data = JSON.parse(response);
    let newNodes = [];

    data.nodes.forEach(item => {
        let fullName;
        if (item['patronymic']) {
            fullName = `${item['name']} ${item['patronymic']} ${item['surname']}`;
        } else {
            fullName = `${item['name']} ${item['surname']}`;
        }
        let node = {
            data: {
                id: item['id'],
                fullName,
            }
        }
        newNodes.push(node)
    })

    data.edges.forEach(item => {
        let person_from = item['person_from']['id'];
        let person_to = item['person_to']['id'];
        let edge = {
            data: {
                id: `${person_from}/${person_to}`,
                source: person_from,
                target: person_to,
                relationType: item['type'],
            }
        }
        newNodes.push(edge)
    })
    nodes = newNodes;
}


function buildTree() {
    cyto = cytoscape({
        container: document.getElementById('cyto'),
        elements: nodes,
        style: [
            {
                selector: 'node',
                style: {
                    'label': 'data(fullName)',
                    'background-color': 'rgba(54,119,206,0.65)',
                    'font-size': 8,
                    'text-valign': 'bottom',
                }
            },
            {
                selector: 'edge',
                style: {
                    'width': 3,
                    'line-color': '#ccc',
                    'curve-style': 'bezier'
                }
            }
        ],
        layout: {
            name: 'cose',
            fit: true,
        }
    });
    let head = cyto.nodes()[0];
    head.style("background-color", "rgb(200,0,0)");
}

function download() {
    let png64 = cyto.png();
    let img = document.getElementById('cyto-png');
    img.setAttribute('src', png64);
    img.classList.remove("visually-hidden");
    document.getElementById('cyto').classList.add("visually-hidden");
}