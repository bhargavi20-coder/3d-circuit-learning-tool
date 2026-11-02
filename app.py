import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="3D Virtual Circuit Lab", layout="wide")

st.title("⚡ 3D Interactive Circuit & Microcontroller Workbench")
st.write("Select components, choose pins, and connect virtual jumper wires in 3D.")

# --- SESSION STATE FOR WIRING ---
if "connections" not in st.session_state:
    st.session_state.connections = [("3V3", "Breadboard Power (+)", "red")]
if "selected_component" not in st.session_state:
    st.session_state.selected_component = "ESP32 DevKit"

# --- SIDEBAR: WIRING WORKBENCH ---
st.sidebar.header("🔌 Jumper Wire Manager")
st.sidebar.write("Connect two pins to complete your circuit loop:")

available_pins = [
    "3V3", "GND", "VIN", 
    "GPIO21 (SDA)", "GPIO22 (SCL)", "GPIO23", "GPIO18", 
    "LED Anode (+)", "LED Cathode (-)", 
    "Resistor Terminal 1", "Resistor Terminal 2",
    "Breadboard Power (+)", "Breadboard Ground (-)"
]

wire_start = st.sidebar.selectbox("From Pin / Node", available_pins, index=0)
wire_end = st.sidebar.selectbox("To Pin / Node", available_pins, index=7)
wire_color = st.sidebar.selectbox("Wire Color", ["red", "black", "blue", "green", "yellow", "orange"])

col_btn1, col_btn2 = st.sidebar.columns(2)
if col_btn1.button("➕ Connect Wire"):
    new_conn = (wire_start, wire_end, wire_color)
    if new_conn not in st.session_state.connections:
        st.session_state.connections.append(new_conn)
        st.sidebar.success(f"Connected {wire_start} to {wire_end}!")

if col_btn2.button("🗑️ Clear Wires"):
    st.session_state.connections = []
    st.sidebar.info("All wires cleared.")

st.sidebar.markdown("---")
st.sidebar.header("🧰 Component Selection")
chosen_item = st.sidebar.selectbox("Active Module", ["ESP32 DevKit", "Arduino Uno", "LED & Resistor Circuit"])
if st.sidebar.button("Load Module"):
    st.session_state.selected_component = chosen_item

# --- MAIN LAYOUT ---
col_canvas, col_info = st.columns([2, 1])

with col_info:
    st.subheader("📋 Active Circuit Connections")
    if st.session_state.connections:
        for idx, (start, end, color) in enumerate(st.session_state.connections):
            st.markdown(f"**{idx+1}.** <span style='color:{color};'>●</span> `{start}` ⟷ `{end}`", unsafe_allow_html=True)
    else:
        st.info("No wires connected yet. Use the sidebar to add connections.")
        
    st.markdown("---")
    st.subheader("💡 Beginner's Guide")
    st.success("To light an LED with an ESP32: Connect **3V3** to **LED Anode (+)**, and connect **LED Cathode (-)** through a **Resistor Terminal 1** to **GND**!")

with col_canvas:
    st.subheader(f"Workbench Canvas: {st.session_state.selected_component}")
    
    fig = go.Figure()

    # 1. Breadboard Base
    fig.add_trace(go.Mesh3d(
        x=[-6, 6, 6, -6, -6, 6, 6, -6],
        y=[-3.5, -3.5, 3.5, 3.5, -3.5, -3.5, 3.5, 3.5],
        z=[-0.4, -0.4, -0.4, -0.4, 0, 0, 0, 0],
        color='whitesmoke', opacity=0.9, name='Breadboard'
    ))

    # Grid Holes
    hx, hy, hz = [], [], []
    for x in np.linspace(-5, 5, 21):
        for y in [-2.0, -1.0, 1.0, 2.0]:
            hx.append(x); hy.append(y); hz.append(0.01)
    fig.add_trace(go.Scatter3d(x=hx, y=hy, z=hz, mode='markers', marker=dict(size=3, color='dimgray'), name='Holes'))

    # 2. Microcontroller / Components Render
    if "ESP32" in st.session_state.selected_component:
        # Board Body
        fig.add_trace(go.Mesh3d(
            x=[-2.5, 2.5, 2.5, -2.5, -2.5, 2.5, 2.5, -2.5],
            y=[-1.2, -1.2, 1.2, 1.2, -1.2, -1.2, 1.2, 1.2],
            z=[0, 0, 0, 0, 0.35, 0.35, 0.35, 0.35],
            color='black', name='ESP32'
        ))
        # Pin Headers
        px = np.linspace(-2.2, 2.2, 4)
        fig.add_trace(go.Scatter3d(
            x=px, y=[-1.2, -1.2, -1.2, -1.2], z=[0.45, 0.45, 0.45, 0.45],
            mode='markers+text', text=['3V3', 'GND', 'GPIO21', 'GPIO22'],
            textposition='bottom center', marker=dict(size=7, color='silver'), name='Pins'
        ))

    # 3. Dynamic 3D Wire Rendering based on Session State Connections
    # Node coordinate mapping dictionary for 3D placement
    node_coords = {
        "3V3": (-2.2, -1.2, 0.45),
        "GND": (-1.0, -1.2, 0.45),
        "VIN": (2.2, -1.2, 0.45),
        "GPIO21 (SDA)": (0.4, -1.2, 0.45),
        "GPIO22 (SCL)": (2.2, -1.2, 0.45),
        "GPIO23": (0.4, 1.2, 0.45),
        "GPIO18": (2.2, 1.2, 0.45),
        "LED Anode (+)": (2.0, 1.0, 0.8),
        "LED Cathode (-)": (2.0, 0.0, 0.8),
        "Resistor Terminal 1": (0.0, 1.0, 0.5),
        "Resistor Terminal 2": (0.0, 0.0, 0.5),
        "Breadboard Power (+)": (-4.0, -2.0, 0.0),
        "Breadboard Ground (-)": (-4.0, 2.0, 0.0)
    }

    for start_node, end_node, color in st.session_state.connections:
        if start_node in node_coords and end_node in node_coords:
            p1 = node_coords[start_node]
            p2 = node_coords[end_node]
            # Draw curved / arc jumper wire
            mid_z = max(p1[2], p2[2]) + 1.2
            fig.add_trace(go.Scatter3d(
                x=[p1[0], (p1[0]+p2[0])/2, p2[0]],
                y=[p1[1], (p1[1]+p2[1])/2, p2[1]],
                z=[p1[2], mid_z, p2[2]],
                mode='lines+markers',
                line=dict(color=color, width=6),
                marker=dict(size=4, color=color),
                name=f"{start_node} → {end_node}"
            ))

    fig.update_layout(
        scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), aspectmode='data'),
        margin=dict(l=0, r=0, b=0, t=30),
        height=550
    )

    st.plotly_chart(fig, width='stretch')
