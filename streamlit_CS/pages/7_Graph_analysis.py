import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd 

# --- PAGE CONFIGURATION ---
st.title("👥 Network Analysis Dashboard")
st.markdown("This page visualizes the friendship network, colored by community, and labeled by the number of connections (degree).")

# --- CORE DATA AND ANALYSIS FUNCTION ---
def create_and_analyze_graph():
    # 1. Graph Definition
    G = nx.Graph()
    G.add_edges_from([
        ("Alice", "Bob"), ("Alice", "Charlie"), ("Bob", "Charlie"), 
        ("Charlie", "Diana"), ("Diana", "Eve"), ("Bob", "Diana"),
        ("Frank", "Eve"), ("Eve", "Ian"), ("Diana", "Ian"), 
        ("Ian", "Grace"), ("Grace", "Hannah"), ("Hannah", "Jack"),
        ("Grace", "Jack"), ("Charlie", "Frank"), ("Alice", "Eve"), 
        ("Bob", "Jack")
    ])

    # 2. Community and Color Mapping
    communities = {
        'Community 1': ['Charlie', 'Frank', 'Bob', 'Alice'],
        'Community 2': ['Diana', 'Eve', 'Ian'],
        'Community 3': ['Hannah', 'Grace', 'Jack']
    }
    color_map = {
        'Community 1': 'skyblue',
        'Community 2': 'salmon',
        'Community 3': 'lightgreen'
    }

    node_color_lookup = {}
    for community_name, members in communities.items():
        color = color_map[community_name]
        for member in members:
            node_color_lookup[member] = color

    colors = [node_color_lookup.get(node, 'gray') for node in G.nodes()]
    
    # 3. Degree Calculation and Custom Labels
    node_degrees = dict(G.degree()) 
    custom_labels = {node: f"{node}\n({degree})" for node, degree in node_degrees.items()} 
    
    most_connected_node = max(node_degrees, key=node_degrees.get)
    max_connections = node_degrees[most_connected_node]
    
    # 4. Plotting Setup and Drawing
    pos = nx.spring_layout(G, seed=42, k=0.8) 
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # --- Drawing the Graph with Node Labels ---
    nx.draw(
        G, pos, ax=ax, 
        labels=custom_labels,         
        with_labels=True,             
        node_size=3500, 
        node_color=colors,
        edge_color='gray', 
        font_size=10, 
        font_weight='bold'
    )
    
    # --- Setting the Title ---
    ax.set_title(
        f"Friend Group Network | Most Connected: {most_connected_node} ({max_connections})", 
        fontsize=16, 
        pad=20
    )

    # --- In-Figure Legend with Colors ---
    ax.text(1.05, 0.95, "Community Legend:", 
            transform=ax.transAxes, fontsize=12, verticalalignment='top', 
            fontweight='bold')
    
    y_start = 0.90
    for i, (name, color) in enumerate(color_map.items()):
        # Draw a small, colored line/box to represent the node color
        ax.plot([1.05, 1.08], [y_start - i*0.05, y_start - i*0.05], 
                color=color, linewidth=8, solid_capstyle='butt', 
                transform=ax.transAxes)
        # Place the community name next to the colored line
        ax.text(1.09, y_start - i*0.05, name, 
                transform=ax.transAxes, fontsize=10, verticalalignment='center')
        
    ax.set_axis_off()

    return fig, most_connected_node, max_connections, node_degrees, communities, color_map


# --- STREAMLIT PAGE DISPLAY ---
graph_fig, most_connected_node, max_connections, node_degrees, communities, color_map = create_and_analyze_graph()

st.success(f"**Most Connected Person:** **{most_connected_node}** with **{max_connections}** connections.")
st.pyplot(graph_fig) 

st.header("💡 Network Analysis Reflection")
st.markdown("---")

st.subheader("Key Findings and Graph Description")

st.markdown("""
This analysis focused on mapping and measuring connectivity within the defined **Friend Group Network**. The resulting graph visualization, colored by **Community** and labeled by **Degree** (number of connections), revealed clear structural features and identified key individuals in the network.

### Description of the Graph
* **Structure:** The network is moderately dense but clearly separates into three distinct groups, confirming the identified community structure. While the **Community 1 (Blue)** and **Community 2 (Salmon)** nodes show heavy internal connectivity, there are critical **bridge nodes** (like Diana and Eve) linking them. **Community 3 (Green)** forms a tight-knit cluster that is connected primarily through a single link to Bob (Community 1) and Ian/Eve (Community 2).
* **Color-Coding (Community):** Nodes are color-coded to instantly show group membership (e.g., Alice, Bob, Charlie, and Frank are in the blue group). This visual separation confirms the validity of the community detection approach.
* **Node Labels (Degree):** Each node is labeled with the person's name and their connection count (degree). This directly addresses the goal of identifying the most connected individuals.

### Interpretation of Connection Counts
The **Connection Counts (Degree) table** and node labels identify the most central figures:

1.  **Diana (Degree 4), Bob (Degree 4), Charlie (Degree 4), and Eve (Degree 4)** are the most connected individuals. This high degree suggests they are socially active or critical hubs for information flow.
2.  **Bob** is a particularly important node as he sits in the **Community 1 (Blue)** group but is connected to **Community 2 (Salmon)** and **Community 3 (LightGreen)**
3.  **Frank (Degree 2)** and **Hannah (Degree 2)** are the least connected members, suggesting they are on the periphery of the network.

### Conclusion
The visualization successfully highlights the underlying community structure and quantifies the social importance of each individual. The presence of high-degree nodes like **Diana** and **Bob** indicates potential single points of failure for information transmission, meaning if they were removed, the network might fragment significantly. Further analysis, such as **Betweenness Centrality**, could confirm their role as critical bridge nodes.
""")

# --- Detailed Analysis & Legend ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Community Members")
    st.markdown("---")
    for community_name, members in communities.items():
        color = color_map[community_name]
        # Correctly formatted HTML markdown line
        st.markdown(
            f'<span style="color:{color}; font-weight:bold;">{community_name}</span>',
            unsafe_allow_html=True
        )
        st.write(f"Members: {', '.join(members)}")

with col2:
    st.subheader("Connection Counts (Degree)")
    st.markdown("---")
    
    # Sort degrees and convert to DataFrame for labeled table
    sorted_degrees = sorted(node_degrees.items(), key=lambda item: item[1], reverse=True)
    df_degrees = pd.DataFrame(
        sorted_degrees, 
        columns=["Name", "Connections"]
    )
    
    st.table(df_degrees)
