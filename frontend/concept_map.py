import streamlit as st
import json
import random
from api_layer.revision import RevisionHelper

def render_concept_map():
    """Render the concept map visualization UI component."""
    st.header("Concept Map")
    st.write("Visualize relationships between concepts in your study materials.")
    
    # Initialize session state variables if they don't exist
    if "concept_map_data" not in st.session_state:
        st.session_state.concept_map_data = None
    if "revision_helper" not in st.session_state:
        st.session_state.revision_helper = RevisionHelper()
    
    # Concept map generation options
    st.subheader("Generate a Concept Map")
    
    # Source selection
    map_source = st.radio(
        "Concept Map Source",
        ["From PDF", "From Text Input"]
    )
    
    # Main concept input
    main_concept = st.text_input("Main Concept:", placeholder="Enter the central concept for your map")
    
    # Source-specific inputs
    if map_source == "From PDF":
        if "pdf_text" in st.session_state and st.session_state.pdf_text:
            st.success("Using the currently loaded PDF.")
            content_source = st.session_state.pdf_text
        else:
            st.warning("No PDF loaded. Please upload a PDF in the PDF Study Assistant section first.")
            content_source = None
    
    elif map_source == "From Text Input":
        content_source = st.text_area("Enter the study material text:", height=200)
    
    # Generate concept map button
    if st.button("Generate Concept Map", key="generate_map_button"):
        if content_source and main_concept:
            with st.spinner("Generating concept map..."):
                try:
                    # Generate concept connections
                    concept_map = st.session_state.revision_helper.generate_concept_connections(
                        content_source, main_concept
                    )
                    
                    # Store in session state
                    st.session_state.concept_map_data = concept_map
                    
                    st.success("Concept map generated!")
                except Exception as e:
                    st.error(f"Error generating concept map: {str(e)}")
        else:
            st.error("Please provide both content and a main concept.")
    
    # Display concept map if data is available
    if st.session_state.concept_map_data:
        st.subheader("Concept Map Visualization")
        
        # Prepare data for visualization
        try:
            # Convert the concept map data to HTML/JavaScript visualization
            html_content = generate_concept_map_html(st.session_state.concept_map_data)
            
            # Display using HTML component
            st.components.v1.html(html_content, height=600)
            
            # Also display as a text list for accessibility
            with st.expander("View as Text List"):
                for node in st.session_state.concept_map_data.get("nodes", []):
                    st.write(f"**{node['label']}**")
                
                st.write("Connections:")
                for edge in st.session_state.concept_map_data.get("edges", []):
                    # Find the node labels
                    from_node = next((node["label"] for node in st.session_state.concept_map_data["nodes"] if node["id"] == edge["from"]), "Unknown")
                    to_node = next((node["label"] for node in st.session_state.concept_map_data["nodes"] if node["id"] == edge["to"]), "Unknown")
                    st.write(f"- {from_node} → {to_node}: {edge.get('label', '')}")
        
        except Exception as e:
            st.error(f"Error displaying concept map: {str(e)}")
            st.json(st.session_state.concept_map_data)  # Fallback to JSON display

def generate_concept_map_html(concept_map_data):
    """Generate HTML/JavaScript for concept map visualization.
    
    Args:
        concept_map_data: Dictionary with nodes and edges
        
    Returns:
        HTML string for the visualization
    """
    # Convert the concept map data to JSON string for JavaScript
    json_data = json.dumps(concept_map_data)
    
    # Generate random colors for nodes based on type
    node_colors = {
        "main": "#ff7f0e",  # Orange for main concept
        "related": "#1f77b4"  # Blue for related concepts
    }
    
    # HTML with D3.js for visualization
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <style>
            .node {{fill: #ccc; stroke: #fff; stroke-width: 2px;}}
            .link {{stroke: #999; stroke-opacity: 0.6; stroke-width: 1px;}}
            .node text {{fill: black; font-weight: bold;}}
            .link-label {{font-size: 10px; fill: #555;}}
        </style>
    </head>
    <body>
        <svg width="100%" height="580"></svg>
        <script>
            // Parse the data
            const data = {json_data};
            
            // Set up the SVG
            const svg = d3.select("svg");
            const width = svg.node().getBoundingClientRect().width;
            const height = svg.node().getBoundingClientRect().height;
            
            // Node colors based on type
            const nodeColors = {{
                "main": "{node_colors['main']}",
                "related": "{node_colors['related']}"
            }};
            
            // Create a force simulation
            const simulation = d3.forceSimulation(data.nodes)
                .force("link", d3.forceLink(data.edges).id(d => d.id).distance(150))
                .force("charge", d3.forceManyBody().strength(-500))
                .force("center", d3.forceCenter(width / 2, height / 2));
            
            // Create the links
            const link = svg.append("g")
                .selectAll("line")
                .data(data.edges)
                .enter().append("line")
                .attr("class", "link");
            
            // Create link labels
            const linkLabel = svg.append("g")
                .selectAll(".link-label")
                .data(data.edges)
                .enter().append("text")
                .attr("class", "link-label")
                .text(d => d.label || "");
            
            // Create the nodes
            const node = svg.append("g")
                .selectAll("circle")
                .data(data.nodes)
                .enter().append("circle")
                .attr("class", "node")
                .attr("r", d => d.type === "main" ? 20 : 15)
                .attr("fill", d => nodeColors[d.type] || "#ccc")
                .call(d3.drag()
                    .on("start", dragstarted)
                    .on("drag", dragged)
                    .on("end", dragended));
            
            // Add node labels
            const nodeLabel = svg.append("g")
                .selectAll(".node-label")
                .data(data.nodes)
                .enter().append("text")
                .attr("class", "node-label")
                .attr("text-anchor", "middle")
                .attr("dy", 30)
                .text(d => d.label);
            
            // Update positions on each tick
            simulation.on("tick", () => {{                
                link
                    .attr("x1", d => d.source.x)
                    .attr("y1", d => d.source.y)
                    .attr("x2", d => d.target.x)
                    .attr("y2", d => d.target.y);
                
                linkLabel
                    .attr("x", d => (d.source.x + d.target.x) / 2)
                    .attr("y", d => (d.source.y + d.target.y) / 2);
                
                node
                    .attr("cx", d => d.x = Math.max(20, Math.min(width - 20, d.x)))
                    .attr("cy", d => d.y = Math.max(20, Math.min(height - 20, d.y)));
                
                nodeLabel
                    .attr("x", d => d.x)
                    .attr("y", d => d.y);
            }});
            
            // Drag functions
            function dragstarted(event, d) {{
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            }}
            
            function dragged(event, d) {{
                d.fx = event.x;
                d.fy = event.y;
            }}
            
            function dragended(event, d) {{
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            }}
        </script>
    </body>
    </html>
    """
    
    return html