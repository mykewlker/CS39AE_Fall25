import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

# --- PAGE TITLE AND INFO ---
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

    custom_labels = {node: f"{node}\n({degree})" for node, degree in node_degrees.items()} # Added newline for better spacing on the node
    
    most_connected_node = max(node_degrees, key=node_degrees.get)
    max_connections = node_degrees[most_connected_node]
    
    # 4. Plotting Setup and Drawing
    pos = nx.spring_layout(G, seed=42, k=0.8) 
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # --- ESSENTIAL FOR NODE LABELS ---
    nx.draw(
        G, pos, ax=ax, 
        labels=custom_labels,         # Custom labels dictionary
        with_labels=True,             # MUST be True to display labels
        node_size=3500, 
        node_color=colors,
        edge_color='gray', 
        font_size=10, 
        font_weight='bold'
    )
    
    # --- ESSENTIAL FOR GRAPH TITLE & LEGEND ---
    ax.set_title(
        f"Friend Group Network | Most Connected: {most_connected_node} ({max_connections})", 
        fontsize=16, 
        pad=20 # Add padding so the title isn't too close to the graph
    )

    # Adding a simple text legend to the side of the plot for color explanation
    legend_title = "Community Legend:"
    legend_items = [f"• {name}" for name in color_map.keys()]
    
    # Position the text outside the main drawing area
    ax.text(1.05, 0.95, legend_title, 
            transform=ax.transAxes, fontsize=12, verticalalignment='top', 
            fontweight='bold')
    
    # Draw colored lines for the legend items
    y_start = 0.90
    for i, (name, color) in enumerate(color_map.items()):
        ax.plot([1.05, 1.08], [y_start - i*0.05, y_start - i*0.05], 
                color=color, linewidth=8, transform=ax.transAxes)
        ax.text(1.09, y_start - i*0.05, name, 
                transform=ax.transAxes, fontsize=10, verticalalignment='center')
        
    # Turn off axis to clean up the plot area
    ax.set_axis_off()

    return fig, most_connected_node, max_connections, node_degrees, communities, color_map


# --- STREAMLIT PAGE DISPLAY ---
graph_fig, most_connected_node, max_connections, node_degrees, communities, color_map = create_and_analyze_graph()

st.success(f"**Most Connected Person:** **{most_connected_node}** with **{max_connections}** connections.")
st.pyplot(graph_fig) # This displays the graph with labels, title, and the new Matplotlib legend

# --- Detailed Analysis (The table part) ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Community Members")
    st.markdown("---")
    for community_name, members in communities.items():
        color = color_map[community_name]
        # Use an HTML span for colored text in Streamlit
        st.markdown(
            f'<span style="color:{color}; font-weight:bold;">{community_name}</span>',
            unsafe_allow_html=True
        )
        st.write(f"Members: {', '.join(members)}")

with col2:
    st.subheader("Connection Counts (Degree)")
    st.markdown("---")
    sorted_degrees = sorted(node_degrees.items(), key=lambda item: item[1], reverse=True)
    st.table(sorted_degrees)
