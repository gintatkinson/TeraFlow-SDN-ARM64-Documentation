// Copyright 2022-2025 ETSI SDG TeraFlowSDN (TFS) (https://tfs.etsi.org/)
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
// Overhauled for GCP/Material Design Dark Theme and Multi-Layer Visualization

function initializeTopology(data) {
    const container = d3.select("#topology-canvas");
    if (container.empty()) {
        console.error("Topology canvas not found.");
        return;
    }

    // --- SETUP ---
    // --- SETUP ---
    container.selectAll("*").remove(); // Clear previous
    const width = container.node().clientWidth;
    const height = container.node().clientHeight;

    const svg = container.append("svg")
        .attr("width", "100%")
        .attr("height", "100%")
        .attr("viewBox", [-width / 2, -height / 2, width, height])
        .style("background-color", "var(--bg-base)");

    const g = svg.append("g");

    // --- DATA ---
    let nodes = data.nodes.map(d => ({...d}));
    let links = data.links.map(d => ({...d}));

    const layerColors = {
        '3gpp': '#f28b82',   // Red
        'ip': '#8ab4f8',     // Blue
        'optical': '#fdd663',// Yellow
        'qkd': '#81c995'     // Green
    };

    // --- SIMULATION ---
    const simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(links).id(d => d.id).distance(100))
        .force("charge", d3.forceManyBody().strength(-300))
        .force("center", d3.forceCenter(0, 0))
        .force("collide", d3.forceCollide().radius(30));

    // --- ELEMENTS ---
    let link = g.append("g")
        .attr("stroke-opacity", 0.6)
        .selectAll("line")
        .data(links)
        .join("line")
        .attr("stroke-width", d => d.type === 'quantum' ? 2 : 1.5)
        .attr("stroke", d => d.type === 'quantum' ? "var(--success-green)" : "var(--border-color)")
        .attr("stroke-dasharray", d => d.type === 'quantum' ? "4,4" : null);

    let node = g.append("g")
        .selectAll("g")
        .data(nodes)
        .join("g")
        .call(drag(simulation));

    node.append("circle")
        .attr("r", 12)
        .attr("stroke", "var(--bg-base)")
        .attr("stroke-width", 2)
        .attr("fill", d => layerColors[d.layer] || 'var(--text-secondary)');
    
    node.append("text")
        .attr("x", 18)
        .attr("y", "0.31em")
        .text(d => d.label)
        .attr("fill", "var(--text-primary)")
        .attr("font-size", "0.8em")
        .attr("font-family", "Roboto, sans-serif");

    node.append("title")
        .text(d => `${d.label}\nLayer: ${d.layer.toUpperCase()}`);

    // --- TICK & ZOOM ---
    simulation.on("tick", () => {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);
        node
            .attr("transform", d => `translate(${d.x},${d.y})`);
    });

    const zoom = d3.zoom()
        .scaleExtent([0.1, 4])
        .on("zoom", (event) => {
            g.attr("transform", event.transform);
        });
    svg.call(zoom);


    // --- FILTERING ---
    const layerFilters = {
        '3gpp': d3.select("#layer-3gpp"),
        'ip': d3.select("#layer-ip"),
        'optical': d3.select("#layer-optical"),
        'qkd': d3.select("#layer-qkd")
    };

    function updateFilters() {
        const activeLayers = Object.keys(layerFilters).filter(layer => layerFilters[layer].property("checked"));

        // Update nodes
        const filteredNodes = data.nodes.filter(d => activeLayers.includes(d.layer));
        const filteredNodeIds = new Set(filteredNodes.map(n => n.id));

        // Update links
        const filteredLinks = data.links.filter(d => filteredNodeIds.has(d.source.id || d.source) && filteredNodeIds.has(d.target.id || d.target));
        
        // Restart simulation with new data
        nodes = filteredNodes.map(d => ({...d}));
        links = filteredLinks.map(d => ({...d}));

        // Re-join data
        link = link.data(links, d => `${d.source.id}-${d.target.id}`);
        link.exit().remove();
        link = link.enter().append("line")
            .attr("stroke-width", d => d.type === 'quantum' ? 2 : 1.5)
            .attr("stroke", d => d.type === 'quantum' ? "var(--success-green)" : "var(--border-color)")
            .attr("stroke-dasharray", d => d.type === 'quantum' ? "4,4" : null)
            .merge(link);

        node = node.data(nodes, d => d.id);
        node.exit().remove();
        const nodeEnter = node.enter().append("g").call(drag(simulation));
        nodeEnter.append("circle")
             .attr("r", 12)
             .attr("stroke", "var(--bg-base)")
             .attr("stroke-width", 2)
             .attr("fill", d => layerColors[d.layer] || 'var(--text-secondary)');
        nodeEnter.append("text")
             .attr("x", 18)
             .attr("y", "0.31em")
             .text(d => d.label)
             .attr("fill", "var(--text-primary)")
             .attr("font-size", "0.8em")
             .attr("font-family", "Roboto, sans-serif");
        nodeEnter.append("title")
             .text(d => `${d.label}\nLayer: ${d.layer.toUpperCase()}`);
        node = nodeEnter.merge(node);
        
        simulation.nodes(nodes);
        simulation.force("link").links(links);
        simulation.alpha(1).restart();
    }

    Object.values(layerFilters).forEach(filter => {
        filter.on("change", updateFilters);
    });
}

// --- DRAG BEHAVIOR ---
function drag(simulation) {
    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    return d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended);
}
