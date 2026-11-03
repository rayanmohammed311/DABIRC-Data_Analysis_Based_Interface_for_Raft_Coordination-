import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import plotly.graph_objects as go

# 1. Page Configuration & Title
st.set_page_config(page_title="DABIRC by Project Nerosiya", layout="wide")
st.title("Project Nerosiya: Data Analysis Based Interface for Raft Coordination (DABIRC)")

st.sidebar.header("Sand Bed Physical Inputs")

# 2. Toggle to choose between Phone Tilt Sensor or Manual Slider
use_phone_sensor = st.sidebar.checkbox(
    "Connect Mobile Tilt Sensor", value=False
)

affected_raft = st.sidebar.selectbox(
    "Target Raft Node", ["Node (0, 0)", "Node (0, 1)", "Node (1, 2)"]
)

# 3. Mobile Sensor Component Integration
settlement_val = 0.0

if use_phone_sensor:
  st.sidebar.markdown(
      "**Tilt your phone to control structural settlement:**"
  )

  # Custom HTML/JS component embedded in Streamlit to read phone motion
  phone_sensor_code = """
        <div style="font-family: monospace; padding: 10px; background: #f0f2f6; border-radius: 5px;">
            <b>Live Tilt Data:</b><br>
            X (Gamma): <span id="gamma">0</span>°<br>
            Y (Beta): <span id="beta">0</span>°
        </div>

        <script>
            // Listen for device orientation changes
            if (window.DeviceOrientationEvent) {
                window.addEventListener('deviceorientation', function(event) {
                    // gamma: left-to-right tilt (-90 to 90)
                    // beta: front-to-back tilt (-180 to 180)
                    let gamma = Math.round(event.gamma || 0);
                    let beta = Math.round(event.beta || 0);
                    
                    document.getElementById('gamma').innerText = gamma;
                    document.getElementById('beta').innerText = beta;

                    // Streamlit custom component communication bridge
                    window.parent.postMessage({
                        type: 'streamlit:setComponentValue',
                        value: { gamma: gamma, beta: beta }
                    }, '*');
                }, true);
            } else {
                document.getElementById('gamma').innerText = "Not Supported";
            }
        </script>
    """
  # Render the sensor reader component in the sidebar and catch its value
  sensor_output = components.html(phone_sensor_code, height=100)

  # If data is being streamed back from the phone, use it; otherwise default to 0
  if sensor_output and isinstance(sensor_output, dict):
    # Map phone's left-to-right tilt (gamma) to settlement depth magnitude
    raw_tilt = abs(sensor_output.get("gamma", 0))
    # Scale down the degrees (0-90) into a realistic millimetre settlement range (0 to 25mm)
    settlement_val = min(float(raw_tilt) * 0.3, 25.0)
  else:
    settlement_val = 0.0
  st.sidebar.info(f"Calculated Settlement Depth: {settlement_val:.1f} mm")

else:
  # Fallback manual slider if phone sensor mode is turned off
  settlement_val = st.sidebar.slider("Settlement Depth (mm)", 0.0, 25.0, 0.0)

# 4. Matrix Math & Simulation Logic
matrix = np.zeros((3, 3))
active_simulation = st.sidebar.checkbox(
    "Simulate Live Sand Erosion / Fault", value=True
)

if active_simulation:
  # Safe parsing of row and column coordinates from dropdown string
  cleaned_str = (
      affected_raft.replace("Node (", "").replace(")", "").replace(" ", "")
  )
  r, c = map(int, cleaned_str.split(","))

  # Ensure indices stay within the 3x3 matrix boundaries
  if 0 <= r < 3 and 0 <= c < 3:
    matrix[r, c] = -settlement_val

# 5. Drawing the 3D Plotly Surface Map
fig = go.Figure(
    data=[go.Surface(z=matrix, colorscale="RdylGn_r")]
)
fig.update_layout(
    title="Real-Time Raft Elevation Matrix (mm)",
    scene=dict(
        xaxis_title="Raft X",
        yaxis_title="Raft Y",
        zaxis_title="Settlement (mm)",
        zaxis=dict(range=[-25, 5]),
    ),
    margin=dict(l=0, r=0, b=0, t=40),
)

# 6. Streamlit Page Layout (Columns)
col1, col2 = st.columns([2, 1])

with col1:
  st.plotly_chart(fig, use_container_width=True)

with col2:
  st.subheader("DABIRC Node Diagnostics")
  max_diff = abs(np.min(matrix))

  st.metric(
      label="Max Differential Settlement",
      value=f"{max_diff:.1f} mm",
      delta=f"-{max_diff:.1f} mm" if max_diff > 0 else "0.0 mm",
      delta_color="inverse",
  )

  # Dynamic threshold alerts
  if max_diff > 12.0:
    st.error("STATUS: CRITICAL SHIFT DETECTED")
    st.warning("Action: Actuating pneumatic re-leveling sub-base ports...")
  else:
    st.success("STATUS: STRUCTURAL BALANCE OPTIMAL")
    st.info("Joint Elastomeric Seals within elastic limits.")