import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

# --- PAGE TITLE AND INFO ---
st.title("👥 Network Analysis Dashboard")
st.markdown("This page visualizes the friendship network, colored by community, and labeled by the number of connections (degree).")

# --- CORE DATA AND ANALYSIS FUNCTION ---
def create_and_analyze_graph():
    # ... (Keep the exact code for G, communities, color_map, etc., here) ...
    G = nx.Graph()
    G.add_edges_from([
        ("Alice", "Bob"), ("Alice", "Charlie"), ("Bob", "Charlie"), 
        ("Charlie", "Diana"), ("Diana", "Eve"), ("Bob", "Diana"),
        ("Frank", "Eve"), ("Eve", "Ian"), ("Diana", "Ian"), 
        ("Ian", "Grace"), ("Grace", "Hannah"), ("Hannah", "Jack"),
        ("Grace", "Jack"), ("Charlie", "Frank"), ("Alice", "Eve"), 
        ("Bob", "Jack")
    ])
    
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

    # ... (Rest of the analysis code) ...
    node_color_lookup = {}
    for community_name, members in communities.items():
        color = color_map[community_name]
        for member in members:
            node_color_lookup[member] = color

    colors = [node_color_lookup.get(node, 'gray') for node in G.nodes()]
    node_degrees = dict(G.degree()) 

    custom_labels = {node: f"{node} ({degree})" for node, degree in node_degrees.items()}
    
    most_connected_node = max(node_degrees, key=node_degrees.get)
    max_connections = node_degrees[most_connected_node]
    
    pos = nx.spring_layout(G, seed=42, k=0.8) 
    fig, ax = plt.subplots(figsize=(12, 8))
    
    nx.draw(G, pos, ax=ax, labels=custom_labels, with_labels=True, 
            node_size=3500, node_color=colors, edge_color='gray', 
            font_size=10, font_weight='bold')
    ax.set_title(f"Friend Group Network | Most Connected: {most_connected_node} ({max_connections})", fontsize=16)

    return fig, most_connected_node, max_connections, node_degrees, communities, color_map


# --- STREAMLIT PAGE DISPLAY ---
graph_fig, most_connected_node, max_connections, node_degrees, communities, color_map = create_and_analyze_graph()

st.success(f"**Most Connected Person:** **{most_connected_node}** with **{max_connections}** connections.")
st.pyplot(graph_fig)

# ... (Keep the rest of the display/table code) ...
col1, col2 = st.columns(2)

with col1:
    st.subheader("Community Legend")
    st.markdown("---")
    for community_name, color in color_map.items():
        st.markdown(
            f'<div style="background-color:{color}; padding: 5px; border-radius: 5px; margin-bottom: 5px;">'
            f'**{community_name}**'
            f'</div>', 
            unsafe_allow_html=True
        )
        st.write(f"Members: {', '.join(communities[community_name])}")

with col2:
    st.subheader("Connection Counts (Degree)")
    st.markdown("---")
    sorted_degrees = sorted(node_degrees.items(), key=lambda item: item[1], reverse=True)
    st.table(sorted_degrees)
