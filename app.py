import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="3D Virtual Circuit Lab (Tinkercad Style)", layout="wide")

st.title("⚡ 3D Interactive Circuit & Microcontroller Workbench")
st.write("Place components, wire nodes, inspect microcontroller pins, and simulate circuits in 3D.")

# --- SESSION STATE INITIALIZATION ---
if "selected_component" not in st.session_state:
    st.session_state.selected_component = "Arduino Uno"
if "inspected_pin" not in st.session_state:
    st.session_state.inspected_pin = "Select a pin on the 3D model"

# --- SIDEBAR: COMPONENT TOOLBOX ---
st.sidebar.header("🧰 Component Toolbox")
component_category = st.sidebar.selectbox(
    "Select Category", 
    ["Microcontrollers", "Passive Components", "Active & Output", "Sensors"]
)

if component_category == "Microcontrollers":
    chosen_item = st.sidebar.selectbox("Choose Model", ["Arduino Uno", "ESP32 DevKit"])
elif component_category == "Passive Components":
    chosen_item = st.sidebar.selectbox("Choose Component", ["Resistor (220Ω)", "Ceramic Capacitor (10µF)"])
elif component_category == "Active & Output":
    chosen_item = st.sidebar.selectbox("Choose Device", ["LED (Red)", "Buzzer", "NPN Transistor (2N2222)"])
else:
    chosen_item = st.sidebar.selectbox("Choose Sensor", ["DHT11 Temp/Humidity", "Ultrasonic (HC-SR04)"])

if st.sidebar.button("➕ Add to Workbench Canvas"):
    st.session_state.selected_component = chosen_item

st.sidebar.markdown("---")
st.sidebar.header("📊 Virtual Multimeter")
multimeter_mode = st.sidebar.radio("Mode", ["Voltage (V)", "Current (mA)", "Resistance (Ω)"])
if multimeter_mode == "Voltage (V)":
    st.sidebar.metric("Multimeter Readout", "4.98 V", "DC")
elif multimeter_mode == "Current (mA)":
    st.sidebar.metric("Multimeter Readout", "18.5 mA", "DC")
else:
      st.sidebar.metric("Multimeter Readout", "220.0 Ω")

# --- MAIN LAYOUT: CANVAS & PIN INSPECTOR ---
col_canvas, col_inspector = st.columns([2, 1])

with col_inspector:
    st.subheader("🔍 Pin Inspector")
    st.info(f"**Active Inspection:** {st.session_state.inspected_pin}")
    
    # Dynamic Pin Descriptions Database
    pin_database = {
        "D9 (PWM)": "Digital Pin 9. Supports Pulse Width Modulation (PWM) for dimming LEDs or controlling motor speed.",
        "GND": "Ground reference pin (0V). Completes the electrical return path back to the power source.",
        "5V": "Regulated 5-volt power output pin used to supply external sensors and modules.",
        "VIN": "Input voltage pin when powering the board externally via an AC/DC adapter or battery.",
        "GPIO21": "General Purpose Input/Output pin on ESP32, frequently used for I2C SDA communication."
    }
    
    clicked_query = st.selectbox("Simulate Pin Click Selection:", list(pin_database.keys()))
    if st.button("Inspect Pin Details"):
        st.session_state.inspected_pin = clicked_query
    
    if st.session_state.inspected_pin in pin_database:
        st.success(pin_database[st.session_state.inspected_pin])
    else:
        st.write("Click a pin or select one above to view its technical specification and beginner guidelines.")

with col_canvas:
    st.subheader(f"Workbench Canvas: Active Object -> {st.session_state.selected_component}")
    
    # --- 3D RENDER ENGINE ---
    fig = go.Figure()

    # 1. Render Breadboard Base Plate
    fig.add_trace(go.Mesh3d(
        x=[-5, 5, 5, -5, -5, 5, 5, -5],
        y=[-3, -3, 3, 3, -3, -3, 3, 3],
        z=[-0.5, -0.5, -0.5, -0.5, 0, 0, 0, 0],
        color='ivory', opacity=0.9, name='Breadboard'
    ))

    # 2. Render Microcontroller / Component Body based on Selection
    if "Arduino" in st.session_state.selected_component:
        # Arduino Blue Board Box
        fig.add_trace(go.Mesh3d(
            x=[-2, 2, 2, -2, -2, 2, 2, -2],
            y=[-1.5, -1.5, 1.5, 1.5, -1.5, -1.5, 1.5, 1.5],
            z=[0, 0, 0, 0, 0.4, 0.4, 0.4, 0.4],
            color='dodgerblue', name='Arduino Uno'
        ))
        # Add interactive clickable pin markers on Arduino header
        fig.add_trace(go.Scatter3d(
            x=[-1.8, -1.2, -0.6, 0, 0.6, 1.2, 1.8],
            y=[1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5],
            z=[0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
            mode='markers+text',
            text=['GND', '5V', 'D8', 'D9', 'D10', 'D11', 'VIN'],
            textposition='top center',
            marker=dict(size=8, color='gold'),
            name='Arduino Pins'
        ))
    elif "ESP32" in st.session_state.selected_component:
        fig.add_trace(go.Mesh3d(
            x=[-1.5, 1.5, 1.5, -1.5, -1.5, 1.5, 1.5, -1.5],
            y=[-1, -1, 1, 1, -1, -1, 1, 1],
            z=[0, 0, 0, 0, 0.3, 0.3, 0.3, 0.3],
            color='black', name='ESP32 DevKit'
        ))
        fig.add_trace(go.Scatter3d(
            x=[-1.2, 0, 1.2], y=[1, 1, 1], z=[0.4, 0.4, 0.4],
            mode='markers+text', text=['GND', '3V3', 'GPIO21'],
            marker=dict(size=8, color='silver'), name='ESP32 Pins'
        ))
    else:
        # Generic Component 3D Representation
        fig.add_trace(go.Scatter3d(
            x=[0, 2], y=[0, 0], z=[0.5, 0.5],
            mode='lines+markers', line=dict(color='crimson', width=10),
            name=st.session_state.selected_component
        ))

    # Layout styling for rotation
    fig.update_layout(
        scene=dict(
            xaxis=dict(title="X Axis (Breadboard Grid)"),
            yaxis=dict(title="Y Axis"),
            zaxis=dict(title="Z Axis"),
            aspectmode='data'
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        height=500
    )

    st.plotly_chart(fig, width='stretch')

# --- EDUCATIONAL HELPER ---
st.markdown("---")
st.subheader("💡 Circuit Assistant & Wiring Guide")
st.success("Tip: Click and drag your mouse over the 3D canvas to rotate your board, inspect component node alignments, and verify wiring loops.")
