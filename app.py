import streamlit as st
import numpy as np
import plotly.graph_objects as go
import sympy as sp

# --- 1. App Configuration ---
st.set_page_config(page_title="Civil Engineer's Terrain Analyzer Pro", layout="wide")

st.title("🏗️ The Civil Engineer's Terrain Analyzer (Pro Version)")
st.markdown("""
**Assignment Context:** This tool assists civil engineers in analyzing terrain.
Now featuring **Custom Function Input** powered by Symbolic AI.
""")

# --- 2. Sidebar Controls ---
st.sidebar.header("⚙️ Engineering Controls")

# Scenario Selection
scenario = st.sidebar.selectbox(
    "Select Terrain Scenario:",
    ("Scenario A: Symmetrical Hill", "Scenario B: Mountain Pass", "Custom (Enter your own formula)")
)

# Custom Input Handling
if scenario == "Custom (Enter your own formula)":
    st.sidebar.info("Tip: Use Python syntax. e.g., `x**2` for $x^2$, `sin(x)` for $\sin(x)$")
    user_formula = st.sidebar.text_input("Enter Function f(x,y):", value="sin(x) + cos(y)")
else:
    # Presets
    if "Scenario A" in scenario:
        user_formula = "100 - x**2 - y**2"
    else:
        user_formula = "x**2 - y**2 + 50"

# Coordinates Input
st.sidebar.subheader("📍 Surveyor Position")
x_val = st.sidebar.slider("X Coordinate", -5.0, 5.0, 1.0, 0.1)
y_val = st.sidebar.slider("Y Coordinate", -5.0, 5.0, 1.0, 0.1)

# Tools
st.sidebar.subheader("🛠️ Analysis Tools")
show_gradient = st.sidebar.checkbox("Show Gradient (Drainage Flow)", value=True)
show_tangent = st.sidebar.checkbox("Show Tangent Plane (Construction)", value=False)

# --- 3. The Math Engine (SymPy) ---

def process_function(formula_str, x_input, y_input):
    try:
        # Define symbols
        x, y = sp.symbols('x y')
        
        # Parse the string into a math expression
        expr = sp.sympify(formula_str)
        
        # Calculate Partial Derivatives Symbolically
        fx_expr = sp.diff(expr, x)
        fy_expr = sp.diff(expr, y)
        
        # Convert to Python functions for fast plotting (numpy)
        f_func = sp.lambdify((x, y), expr, 'numpy')
        fx_func = sp.lambdify((x, y), fx_expr, 'numpy')
        fy_func = sp.lambdify((x, y), fy_expr, 'numpy')
        
        # Calculate values at the specific point
        z_val = float(f_func(x_input, y_input))
        fx_val = float(fx_func(x_input, y_input))
        fy_val = float(fy_func(x_input, y_input))
        
        # Generate Grid Data for 3D Plot
        x_range = np.linspace(-6, 6, 100)
        y_range = np.linspace(-6, 6, 100)
        X, Y = np.meshgrid(x_range, y_range)
        Z = f_func(X, Y) # This might broadcast a single value if function is constant
        
        # Handle constant functions (e.g. z=10)
        if isinstance(Z, (int, float)):
            Z = np.full_like(X, Z)
            
        return X, Y, Z, z_val, fx_val, fy_val, sp.latex(expr), sp.latex(fx_expr), sp.latex(fy_expr), None
        
    except Exception as e:
        return None, None, None, None, None, None, None, None, None, str(e)

# Run the Math Engine
X, Y, Z, z0, fx, fy, latex_f, latex_fx, latex_fy, error_msg = process_function(user_formula, x_val, y_val)

# --- 4. Main Display ---

col1, col2 = st.columns([1, 2])

with col1:
    if error_msg:
        st.error(f"❌ **Syntax Error:** {error_msg}")
        st.warning("Please check your math syntax. Use `**` for power, `np.sin` is not needed, just `sin`.")
    else:
        st.info(f"**Function:** $f(x,y) = {latex_f}$")
        st.divider()
        
        st.subheader("📊 Calculus Data")
        st.metric("Elevation (z)", f"{z0:.2f} m")
        
        st.markdown("#### 1. Partial Derivatives")
        st.latex(r"\frac{\partial f}{\partial x} = " + latex_fx)
        st.latex(r"\frac{\partial f}{\partial y} = " + latex_fy)
        
        c1, c2 = st.columns(2)
        c1.metric("Slope X (fx)", f"{fx:.2f}")
        c2.metric("Slope Y (fy)", f"{fy:.2f}")
        
        # Topic 4: Gradient
        st.markdown("#### 2. Gradient Vector")
        grad_mag = np.sqrt(fx**2 + fy**2)
        st.latex(r"\nabla f = \langle " + f"{fx:.2f}, {fy:.2f}" + r" \rangle")
        
        if grad_mag < 0.1:
            st.error("🚩 **PEAK/VALLEY DETECTED** (Gradient ≈ 0)")
        else:
            st.success(f"Steepness: {grad_mag:.2f}")

with col2:
    if error_msg:
        st.image("https://media.giphy.com/media/26hkhKd9CQzzXsps4/giphy.gif", caption="Waiting for valid input...")
    else:
        st.subheader("🌍 3D Terrain Visualization")
        
        fig = go.Figure(data=[go.Surface(z=Z, x=X, y=Y, colorscale='Earth', opacity=0.8)])

        # Surveyor Point
        fig.add_trace(go.Scatter3d(
            x=[x_val], y=[y_val], z=[z0],
            mode='markers', marker=dict(size=8, color='red'), name='Surveyor'
        ))

        # Gradient Arrow
        if show_gradient and grad_mag > 0.1:
            fig.add_trace(go.Cone(
                x=[x_val], y=[y_val], z=[z0],
                u=[fx], v=[fy], w=[0],
                sizemode="absolute", sizeref=2, anchor="tail", colorscale=[[0, 'red'], [1, 'red']], name='Gradient'
            ))

        # Tangent Plane
        if show_tangent:
            xt = np.linspace(x_val - 1.5, x_val + 1.5, 10)
            yt = np.linspace(y_val - 1.5, y_val + 1.5, 10)
            Xt, Yt = np.meshgrid(xt, yt)
            Zt = z0 + fx * (Xt - x_val) + fy * (Yt - y_val)
            fig.add_trace(go.Surface(x=Xt, y=Yt, z=Zt, colorscale='Gray', opacity=0.5, showscale=False, name='Tangent Plane'))

        fig.update_layout(scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'), height=600, margin=dict(l=0, r=0, b=0, t=30))
        st.plotly_chart(fig, use_container_width=True)
