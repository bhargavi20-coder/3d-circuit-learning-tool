import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Set Page Config
st.set_page_config(page_title="Interactive 3D Circuit Workbench", layout="wide")

st.title("⚡ 3D Interactive Circuit Workbench for Beginners")
st.write("Construct simple circuits, explore 3D components, and understand electrical flow.")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🔌 Circuit Parameters")
battery_voltage = st.sidebar.slider("Battery Voltage (V)", 1.0, 12.0, 9.0, 0.5)
resistor_value = st.sidebar.slider("Resistor Resistance (Ω)", 100, 1000, 330, 10)
switch_state = st.sidebar.toggle("Close Switch", value=True)

# --- CIRCUIT CALCULATIONS ---
if switch_state:
    current_ma = (battery_voltage / resistor_value) * 1000
    led_status = "🟢 ON (Bright)" if current_ma >= 15 else "🟡 ON (Dim)"
    if current_ma > 30:
        led_status = "💥 BURNT OUT! (Too much current)"
else:
    current_ma = 0.0
    led_status = "🔴 OFF"

# Display metrics
col1, col2, col3 = st.columns(3)
col1.metric("Voltage", f"{battery_voltage} V")
col2.metric("Current", f"{current_ma:.2f} mA")
col3.metric("LED Status", led_status)

# --- 3D VISUALIZATION ENGINE ---
def draw_3d_circuit(voltage, current_active):
    fig = go.Figure()

    # 1. Draw 3D Battery Block
    fig.add_trace(go.Mesh3d(
        x=[0, 1, 1, 0, 0, 1, 1, 0],
        y=[0, 0, 2, 2, 0, 0, 2, 2],
        z=[0, 0, 0, 0, 1.5, 1.5, 1.5, 1.5],
        i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
        j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
        k=[0, 7, 5, 3, 6, 7, 1, 1, 5, 5, 7, 6],
        color='gold', opacity=0.8, name='9V Battery'
    ))

    # 2. Draw 3D LED (Sphere + Cylinder base)
    u = np.linspace(0, 2 * np.pi, 20)
    v = np.linspace(0, np.pi, 20)
    x_led = 4 + 0.4 * np.outer(np.cos(u), np.sin(v))
    y_led = 1 + 0.4 * np.outer(np.sin(u), np.sin(v))
    z_led = 1.5 + 0.4 * np.outer(np.ones(np.size(u)), np.cos(v))

    led_color = 'crimson' if current_active else 'gray'
    fig.add_trace(go.Surface(x=x_led, y=y_led, z=z_led, colorscale=[[0, led_color], [1, led_color]], showscale=False, name="LED"))

    # 3. Draw Connecting 3D Wires (Line Traces)
    wire_color = "red" if current_active else "navy"

    # Positive Rail Wires
    fig.add_trace(go.Scatter3d(
        x=[0.5, 0.5, 4], y=[2, 3, 3], z=[0.75, 0.75, 0.75],
        mode='lines+markers', line=dict(color=wire_color, width=8), name='Positive Wire'
    ))
    # Resistor Connection to LED Wire
    fig.add_trace(go.Scatter3d(
        x=[4, 4], y=[3, 1.4], z=[0.75, 1.5],
        mode='lines', line=dict(color=wire_color, width=8), name='LED Anode'
    ))
    # Ground Return Wire
    fig.add_trace(go.Scatter3d(
        x=[4, 4, 0.5, 0.5], y=[0.6, -1, -1, 0], z=[1.5, 0.75, 0.75, 0.75],
        mode='lines', line=dict(color='black', width=8), name='Ground Wire'
    ))

    # 4. Layout formatting for Interactive 3D Orbiting
    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode='data'
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        height=550
    )
    return fig

# Render Visualizer in Streamlit
st.plotly_chart(draw_3d_circuit(battery_voltage, switch_state and current_ma <= 30), use_container_width=True)

# Interactive Guidance Section
st.subheader("💡 Beginner's AI Assistant Tip")
if current_ma > 30:
    st.error("Warning: The current is too high! An LED typically safely operates around 15-20 mA. Decrease voltage or increase resistance.")
elif current_ma == 0:
    st.info("The switch is OPEN. Close the switch in the sidebar to complete the loop circuit.")
else:
    st.success(f"Circuit operates safely! Ohm's Law in action: I = V / R = {battery_voltage}V / {resistor_value}Ω = {current_ma:.2f}mA.")