document.addEventListener("DOMContentLoaded", function() {
    retrieveNodes();
});


let nodes;
let url = `${document.URL}api/v1/tree/1/`;


function retrieveNodes() {
    let xhr = new XMLHttpRequest();
    xhr.open('GET', url);
    xhr.send();
    xhr.onload = function() {
      if (xhr.status === 200) {
        parseResponse(xhr.response);
        buildGraph();
      }
    };
    xhr.onerror = function() {
      alert(`Network Error`);
    };
}


function parseResponse(response) {
    let newNodes = [];
    response.forEach(item => {
        let node = {
            data: {
                id: item['id'],
            }
        }
        let edge = {
            data: {
                id: `${item['person_from']}/${item['person_to']}`,
                source: item['person_from'],
                target: item['person_to'],
            }
        }
        newNodes.push(node, edge)
    })
    nodes = newNodes;
}


function buildGraph() {
    cytoscape({
        container: document.getElementById('cyto'),
        elements: nodes,
        style: [
            {
                selector: 'node',
                style: {
                    'background-color': 'rgba(102,102,102,0.65)',
                    'label': 'data(id)'
                }
            },
            {
                selector: 'edge',
                style: {
                    'width': 3,
                    'line-color': '#ccc',
                    'target-arrow-color': '#ccc',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier'
                }
            }
        ],
        layout: {
            name: 'grid',
            rows: 1
        }
    });
}
