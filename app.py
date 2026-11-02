import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="3D Virtual Circuit Lab (Tinkercad Style)", layout="wide")

st.title("⚡ 3D Interactive Circuit & Microcontroller Workbench")
st.write("Place components, wire nodes, inspect microcontroller pins, and simulate circuits in 3D.")

# --- SESSION STATE INITIALIZATION ---
if "selected_component" not in st.session_state:
    st.session_state.selected_component = "ESP32 DevKit"
if "inspected_pin" not in st.session_state:
    st.session_state.inspected_pin = "GPIO21"

# --- SIDEBAR: COMPONENT TOOLBOX ---
st.sidebar.header("🧰 Component Toolbox")
chosen_item = st.sidebar.selectbox(
    "Choose Microcontroller / Module", 
    ["ESP32 DevKit", "Arduino Uno", "Resistor (220Ω)", "LED (Red)", "Buzzer"]
)

if st.sidebar.button("➕ Select/Place Component"):
    st.session_state.selected_component = chosen_item

st.sidebar.markdown("---")
st.sidebar.header("📊 Virtual Multimeter")
multimeter_mode = st.sidebar.radio("Mode", ["Voltage (V)", "Current (mA)", "Resistance (Ω)"])
if multimeter_mode == "Voltage (V)":
    st.sidebar.metric("Multimeter Readout", "3.30 V", "DC")
elif multimeter_mode == "Current (mA)":
    st.sidebar.metric("Multimeter Readout", "15.4 mA", "DC")
else:
    st.sidebar.metric("Multimeter Readout", "330.0 Ω")

# --- MAIN LAYOUT: CANVAS & PIN INSPECTOR ---
col_canvas, col_inspector = st.columns([2, 1])

with col_inspector:
    st.subheader("🔍 Pin Inspector")
    
    # Comprehensive Pin Database for ESP32 & Arduino
    pin_database = {
        "GPIO21": "ESP32: SDA (I2C Data line). Used for communicating with OLED screens, sensors, etc.",
        "GPIO22": "ESP32: SCL (I2C Clock line). Works alongside SDA for I2C bus communication.",
        "GPIO23": "ESP32: MOSI pin for SPI communication peripherals.",
        "GPIO18": "ESP32: SCK clock pin for SPI bus.",
        "3V3": "ESP32: Provides regulated 3.3V power output to low-power sensors.",
        "GND": "Ground reference pin (0V return path).",
        "VIN": "External power input pin (typically 5V from USB).",
        "D9 (PWM)": "Arduino: Digital PWM pin for analog output/dimming.",
        "D13": "Arduino: Built-in LED test pin and SPI SCK."
    }
    
    selected_inspect_pin = st.selectbox("Click/Select Pin to Inspect:", list(pin_database.keys()))
    st.session_state.inspected_pin = selected_inspect_pin
    
    st.info(f"**Specifications for [{st.session_state.inspected_pin}]:**")
    st.success(pin_database.get(st.session_state.inspected_pin, "Select a valid pin."))

with col_canvas:
    st.subheader(f"Workbench Canvas: Active Object -> {st.session_state.selected_component}")
    
    fig = go.Figure()

    # --- 1. RENDER REALISTIC BREADBOARD WITH VISIBLE HOLES ---
    # Breadboard Base Plate
    fig.add_trace(go.Mesh3d(
        x=[-6, 6, 6, -6, -6, 6, 6, -6],
        y=[-3.5, -3.5, 3.5, 3.5, -3.5, -3.5, 3.5, 3.5],
        z=[-0.4, -0.4, -0.4, -0.4, 0, 0, 0, 0],
        color='whitesmoke', opacity=0.95, name='Breadboard Body'
    ))

    # Generate Grid Holes (Tie-points) across the breadboard surface
    hole_x, hole_y, hole_z = [], [], []
    for x in np.linspace(-5, 5, 21):
        for y in [-2.0, -1.0, 1.0, 2.0]:  # Power and terminal strip rows
            hole_x.append(x)
            hole_y.append(y)
            hole_z.append(0.01)

    fig.add_trace(go.Scatter3d(
        x=hole_x, y=hole_y, z=hole_z,
        mode='markers',
        marker=dict(size=3, color='dimgray', symbol='circle'),
        name='Breadboard Holes'
    ))

    # --- 2. RENDER DUAL-ROW MICROCONTROLLER (ESP32 / Arduino) ---
    if "ESP32" in st.session_state.selected_component:
        # ESP32 Black Board Body
        fig.add_trace(go.Mesh3d(
            x=[-2.5, 2.5, 2.5, -2.5, -2.5, 2.5, 2.5, -2.5],
            y=[-1.2, -1.2, 1.2, 1.2, -1.2, -1.2, 1.2, 1.2],
            z=[0, 0, 0, 0, 0.35, 0.35, 0.35, 0.35],
            color='black', name='ESP32 Module'
        ))
        
        # Left Row Pins
        left_pins_x = np.linspace(-2.2, 2.2, 6)
        fig.add_trace(go.Scatter3d(
            x=left_pins_x, y=[-1.2 * np.ones(6)], z=[0.45 * np.ones(6)],
            mode='markers+text',
            text=['3V3', 'GND', 'GPIO21', 'GPIO22', 'GPIO23', 'GPIO18'],
            textposition='bottom center',
            marker=dict(size=6, color='silver'),
            name='ESP32 Left Header'
        ))
        
        # Right Row Pins
        fig.add_trace(go.Scatter3d(
            x=left_pins_x, y=[1.2 * np.ones(6)], z=[0.45 * np.ones(6)],
            mode='markers+text',
            text=['VIN', 'GND', 'GPIO4', 'GPIO2', 'GPIO15', 'EN'],
            textposition='top center',
            marker=dict(size=6, color='silver'),
            name='ESP32 Right Header'
        ))

    elif "Arduino" in st.session_state.selected_component:
        # Arduino Blue Board Body
        fig.add_trace(go.Mesh3d(
            x=[-3, 3, 3, -3, -3, 3, 3, -3],
            y=[-2, -2, 2, 2, -2, -2, 2, 2],
            z=[0, 0, 0, 0, 0.35, 0.35, 0.35, 0.35],
            color='dodgerblue', name='Arduino Uno'
        ))
        fig.add_trace(go.Scatter3d(
            x=np.linspace(-2.5, 2.5, 5), y=[-2 * np.ones(5)], z=[0.45 * np.ones(5)],
            mode='markers+text', text=['GND', '5V', 'D8', 'D9', 'D13'],
            textposition='bottom center',
            marker=dict(size=6, color='gold'), name='Arduino Headers'
        ))
    else:
        # Passive / Output Component
        fig.add_trace(go.Scatter3d(
            x=[-1, 1], y=[0, 0], z=[0.5, 0.5],
            mode='lines+markers', line=dict(color='crimson', width=10),
            name=st.session_state.selected_component
        ))

    # Layout formatting for interactive rotation
    fig.update_layout(
        scene=dict(
            xaxis=dict(title="X Grid"),
            yaxis=dict(title="Y Grid"),
            zaxis=dict(title="Z Height"),
            aspectmode='data'
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        height=550
    )

    st.plotly_chart(fig, width='stretch')

# --- EDUCATIONAL FOOTER ---
st.markdown("---")
st.success("✨ **Interactive Tip:** Click and rotate the 3D canvas to inspect how the microcontroller dual-row headers align directly over the breadboard grid tie-points!")
