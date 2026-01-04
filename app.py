import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- 1. App Configuration & Title ---
st.set_page_config(page_title="Civil Engineer's Terrain Analyzer", layout="wide")

st.title("🏗️ The Civil Engineer's Terrain Analyzer")
st.markdown("""
**Assignment Context:** This tool assists civil engineers in analyzing terrain for highway construction and drainage systems.
It utilizes **Multivariable Calculus** to visualize slopes, water flow directions, and construction feasibility.
""")

# --- 2. Sidebar Controls ---
st.sidebar.header("⚙️ Engineering Controls")

# Scenario Selection (The Function)
scenario = st.sidebar.selectbox(
    "Select Terrain Scenario:",
    ("Scenario A: Symmetrical Hill (Dome)", "Scenario B: Mountain Pass (Saddle)")
)

# Coordinates Input (The Surveyor)
st.sidebar.subheader("📍 Surveyor Position")
x_val = st.sidebar.slider("X Coordinate", -5.0, 5.0, 1.0, 0.1)
y_val = st.sidebar.slider("Y Coordinate", -5.0, 5.0, 1.0, 0.1)

# Analysis Tools (Key Concepts)
st.sidebar.subheader("🛠️ Analysis Tools")
show_gradient = st.sidebar.checkbox("Show Gradient (Drainage Flow)", value=True)
show_tangent = st.sidebar.checkbox("Show Tangent Plane (Construction)", value=False)

# --- 3. Mathematical Functions ---

def get_terrain_data(scenario, x, y):
    # Create a grid for plotting
    x_range = np.linspace(-6, 6, 100)
    y_range = np.linspace(-6, 6, 100)
    X, Y = np.meshgrid(x_range, y_range)
    
    if "Scenario A" in scenario:
        # Function: f(x,y) = 100 - x^2 - y^2
        Z = 100 - X**2 - Y**2
        z_point = 100 - x**2 - y**2
        fx = -2 * x
        fy = -2 * y
        formula = "f(x,y) = 100 - x^2 - y^2"
        desc = "A simple hill. Ideal for analyzing basic run-off."
    else:
        # Function: f(x,y) = x^2 - y^2 + 50
        Z = X**2 - Y**2 + 50
        z_point = x**2 - y**2 + 50
        fx = 2 * x
        fy = -2 * y
        formula = "f(x,y) = x^2 - y^2 + 50"
        desc = "A saddle point. Critical for finding passes between mountains."
        
    return X, Y, Z, z_point, fx, fy, formula, desc

# Get data based on user input
X, Y, Z, z0, fx, fy, formula, description = get_terrain_data(scenario, x_val, y_val)

# --- 4. Main Analysis Panel (Calculations) ---

col1, col2 = st.columns([1, 2])

with col1:
    st.info(f"**Current Function:** ${formula}$")
    st.write(f"*{description}*")
    st.divider()
    
    st.subheader("📊 Calculus Data")
    st.metric(label="Elevation (z)", value=f"{z0:.2f} m")
    
    # Topic 2: Partial Derivatives
    st.markdown("#### 1. Partial Derivatives (Rates of Change)")
    c1, c2 = st.columns(2)
    c1.metric("Slope in X (fx)", f"{fx:.2f}")
    c2.metric("Slope in Y (fy)", f"{fy:.2f}")
    
    if abs(fx) > 2 or abs(fy) > 2:
        st.warning("⚠️ **Steep Slope Warning:** Grade is too steep for standard highway construction.")
    else:
        st.success("✅ **Slope Acceptable:** Gradient is safe for building.")

    # Topic 4: Gradient
    st.markdown("#### 2. Gradient Vector (Steepest Ascent)")
    grad_mag = np.sqrt(fx**2 + fy**2)
    st.latex(r"\nabla f = \langle " + f"{fx:.2f}, {fy:.2f}" + r" \rangle")
    st.write(f"Magnitude: **{grad_mag:.2f}**")
    
    if grad_mag < 0.1:
        st.error("🚩 **CRITICAL POINT DETECTED:** You are at a Peak, Valley, or Saddle Point. (Gradient ≈ 0)")
    else:
        st.info("💧 **Drainage Info:** Water will flow in the direction opposite to the gradient.")

with col2:
    # --- 5. Visualization (Topic 1 & 5) ---
    st.subheader("🌍 3D Terrain Visualization")
    
    # Base Surface
    fig = go.Figure(data=[go.Surface(z=Z, x=X, y=Y, colorscale='Earth', opacity=0.8)])

    # Add the Surveyor Point
    fig.add_trace(go.Scatter3d(
        x=[x_val], y=[y_val], z=[z0],
        mode='markers', marker=dict(size=8, color='red'),
        name='Surveyor Position'
    ))

    # Add Gradient Vector (Arrow)
    if show_gradient and grad_mag > 0.1:
        # Scale arrow for visibility
        scale = 2.0 
        fig.add_trace(go.Cone(
            x=[x_val], y=[y_val], z=[z0],
            u=[fx], v=[fy], w=[0], # 2D gradient projected on the map, or w can be calculated for 3D direction
            sizemode="absolute", sizeref=2, anchor="tail", colorscale=[[0, 'red'], [1, 'red']],
            name='Gradient Vector'
        ))

    # Add Tangent Plane (Linear Approximation)
    if show_tangent:
        # Create a small grid around the point
        xt = np.linspace(x_val - 1.5, x_val + 1.5, 10)
        yt = np.linspace(y_val - 1.5, y_val + 1.5, 10)
        Xt, Yt = np.meshgrid(xt, yt)
        # Tangent plane equation: z - z0 = fx(x-x0) + fy(y-y0)
        Zt = z0 + fx * (Xt - x_val) + fy * (Yt - y_val)
        
        fig.add_trace(go.Surface(
            x=Xt, y=Yt, z=Zt,
            colorscale='Gray', opacity=0.5, showscale=False,
            name='Tangent Plane'
        ))

    fig.update_layout(
        title='Interactive Terrain Model',
        scene=dict(
            xaxis_title='X (East-West)',
            yaxis_title='Y (North-South)',
            zaxis_title='Elevation (Z)'
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)
