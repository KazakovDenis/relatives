document.addEventListener("DOMContentLoaded", function() {
    retrieveNodes();
    document.getElementById("cyto-download").addEventListener("click", download);
});


let nodes, cyto, treeId, prevNode;


function retrieveNodes() {
    treeId = document.getElementById('cyto').dataset.treeId;
    const url = `${document.location.origin}/api/v1/tree/${treeId}/scheme`;

    const xhr = new XMLHttpRequest();
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
                href: `${document.location.origin}/ui/tree/${treeId}/person/${item['id']}`,
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
            }
        }
        if (item['type'] === 'PARENT') edge.data.arrow = 'triangle';
        newNodes.push(edge);
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
                    'curve-style': 'bezier',
                    'line-color': '#ccc',
                    'line-dash-pattern': [3, 5],
                    'line-style': 'dashed',
                }
            },
            {
                'selector': 'edge[arrow]',
                'style': {
                    'source-arrow-shape': 'data(arrow)',
                }
            },
        ],
        layout: {
            name: 'cose-bilkent',
            fit: true,
            nodeDimensionsIncludeLabels: true,
            idealEdgeLength: 50,
        },
        ready: () => {
            alert('You can move nodes, zoom in/out and open person profile by clicking');
        }
    });

    cyto.on('tap', 'node', function(){
      try {
        window.open( this.data('href') );
      } catch(e){
        window.location.href = this.data('href');
      }
    });

    cyto.on('drag', 'node', function(event){
        prevNode.style('background-color', 'rgba(54,119,206,0.65)');
        event.target.style('background-color', 'rgb(200,0,0)');
        prevNode = event.target;
    });

    prevNode = cyto.nodes()[0];
    prevNode.style('background-color', 'rgb(200,0,0)');
}

function download() {
    const image = cyto.jpg({
        full: true,
        scale: 10,
        quality: 1,
    });
    fetch(image)
    .then(resp => resp.blob())
    .then(data => {
        const blob = window.URL.createObjectURL(data);
        const anchor = document.createElement('a');
        anchor.style.display = 'none';
        anchor.href = blob;
        anchor.download = 'tree.jpg';
        document.body.appendChild(anchor);
        anchor.click();
        window.URL.revokeObjectURL(blob);
    });
}