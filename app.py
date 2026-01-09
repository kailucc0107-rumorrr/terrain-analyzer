import streamlit as st
import numpy as np
import plotly.graph_objects as go
import sympy as sp

# --- 1. App Configuration ---
st.set_page_config(page_title="Civil Engineer's Terrain Analyzer (Edu)", layout="wide")

st.title("🏗️ The Civil Engineer's Terrain Analyzer (Educational Ver.)")
st.markdown("""
**Welcome, Student Engineer!** 👷‍♂️
This tool helps you visualize how Calculus concepts (Derivatives & Gradients) are used in real-world Civil Engineering to analyze land topography.
""")

# --- Add a "How to Use" Guide ---
with st.expander("📖 READ ME FIRST: How to use this tool?"):
    st.markdown("""
    1.  **Select a Scenario:** Choose a terrain type on the left.
    2.  **Move the Surveyor:** Drag the sliders to move your position (Red Dot).
    3.  **Analyze the Data:** Check the panel below to see if the slope is safe for construction.
    """)

# --- 2. Sidebar Controls ---
st.sidebar.header("⚙️ Engineering Controls")

# Scenario Selection
scenario = st.sidebar.selectbox(
    "Select Terrain Scenario:",
    ("Scenario A: Symmetrical Hill", "Scenario B: Mountain Pass", "Custom (Enter your own formula)"),
    help="Choose a preset land shape or enter a custom function."
)

# Custom Input Handling
if scenario == "Custom (Enter your own formula)":
    st.sidebar.info("Tip: Use Python syntax. e.g., `x**2` for x², `sin(x)`")
    user_formula = st.sidebar.text_input("Enter Function f(x,y):", value="sin(x) + cos(y)")
else:
    if "Scenario A" in scenario:
        user_formula = "100 - x**2 - y**2"
    else:
        user_formula = "x**2 - y**2 + 50"

# Coordinates Input (Updated Labels as requested)
st.sidebar.subheader("📍 Surveyor Position")
x_val = st.sidebar.slider("X Coordinate (East-West)", -5.0, 5.0, 1.0, 0.1, help="Move left/right on the map")
y_val = st.sidebar.slider("Y Coordinate (North-South)", -5.0, 5.0, 1.0, 0.1, help="Move up/down on the map")

# Tools (Updated Labels as requested)
st.sidebar.subheader("🛠️ Analysis Tools")
show_gradient = st.sidebar.checkbox("Show Gradient (Water Flow)", value=True, help="Visualizes the direction of steepest ascent.")
show_tangent = st.sidebar.checkbox("Show Tangent Plane (Leveling)", value=False, help="Visualizes the flat surface approximation.")

# --- 3. The Math Engine (SymPy) ---
def process_function(formula_str, x_input, y_input):
    try:
        x, y = sp.symbols('x y')
        expr = sp.sympify(formula_str)
        fx_expr = sp.diff(expr, x)
        fy_expr = sp.diff(expr, y)
        
        f_func = sp.lambdify((x, y), expr, 'numpy')
        fx_func = sp.lambdify((x, y), fx_expr, 'numpy')
        fy_func = sp.lambdify((x, y), fy_expr, 'numpy')
        
        z_val = float(f_func(x_input, y_input))
        fx_val = float(fx_func(x_input, y_input))
        fy_val = float(fy_func(x_input, y_input))
        
        x_range = np.linspace(-6, 6, 100)
        y_range = np.linspace(-6, 6, 100)
        X, Y = np.meshgrid(x_range, y_range)
        Z = f_func(X, Y)
        
        if isinstance(Z, (int, float)):
            Z = np.full_like(X, Z)
            
        return X, Y, Z, z_val, fx_val, fy_val, sp.latex(expr), sp.latex(fx_expr), sp.latex(fy_expr), None
        
    except Exception as e:
        return None, None, None, None, None, None, None, None, None, str(e)

X, Y, Z, z0, fx, fy, latex_f, latex_fx, latex_fy, error_msg = process_function(user_formula, x_val, y_val)

# --- 4. Main Display with Explanations ---

col1, col2 = st.columns([1, 2])

with col1:
    if error_msg:
        st.error(f"❌ **Syntax Error:** {error_msg}")
    else:
        st.info(f"**Current Function:**\n\n $f(x,y) = {latex_f}$")
        
        st.subheader("📊 Site Analysis Data")
        
        # --- Elevation ---
        st.metric("Elevation (z)", f"{z0:.2f} m")
        st.caption("ℹ️ This represents the height above sea level.")
        
        st.divider()

        # --- Partial Derivatives ---
        st.markdown("#### 1. Slope Analysis (Partial Derivatives)")
        st.latex(r"\frac{\partial f}{\partial x} = " + latex_fx)
        st.latex(r"\frac{\partial f}{\partial y} = " + latex_fy)
        
        c1, c2 = st.columns(2)
        # Keeping technical terms + Direction context
        c1.metric("Slope X (East-West)", f"{fx:.2f}")
        c2.metric("Slope Y (North-South)", f"{fy:.2f}")

        # ✨ EXPLANATION FOR BEGINNERS ✨
        with st.expander("❓ What does this mean?"):
            st.markdown("""
            **Engineering Application: Road Safety**
            * **Slope X:** Tells us how steep the road is in the East-West direction.
            * **Slope Y:** Tells us how steep the road is in the North-South direction.
            * **Why it matters:** If this number is too high (e.g., > 0.10), construction trucks cannot climb it safely!
            """)

        st.divider()
        
        # --- Gradient ---
        st.markdown("#### 2. Drainage Analysis (Gradient)")
        grad_mag = np.sqrt(fx**2 + fy**2)
        st.latex(r"\nabla f = \langle " + f"{fx:.2f}, {fy:.2f}" + r" \rangle")
        
        if grad_mag < 0.1:
            st.success("✅ **FLAT LAND** (Good for construction)")
        else:
            st.warning(f"⚠️ **STEEP TERRAIN** (Steepness: {grad_mag:.2f})")

        # ✨ EXPLANATION FOR BEGINNERS ✨
        with st.expander("❓ How to read the arrow?"):
            st.markdown("""
            **Engineering Application: Water Drainage**
            * The **Red Arrow (Gradient)** points to the highest peak (steepest ascent).
            * **Water Flow:** Water always flows in the **OPPOSITE** direction of the arrow.
            * Engineers use this to decide where to place drainage pipes so the road doesn't flood.
            """)

with col2:
    if not error_msg:
        st.subheader("🌍 3D Terrain Visualization")
        
        fig = go.Figure(data=[go.Surface(z=Z, x=X, y=Y, colorscale='Earth', opacity=0.8)])
        
        # Surveyor Position
        fig.add_trace(go.Scatter3d(
            x=[x_val], y=[y_val], z=[z0],
            mode='markers', marker=dict(size=8, color='red'), name='Surveyor (You)'
        ))

        # Gradient Arrow
        if show_gradient and grad_mag > 0.1:
            fig.add_trace(go.Cone(
                x=[x_val], y=[y_val], z=[z0],
                u=[fx], v=[fy], w=[0],
                sizemode="absolute", sizeref=2, anchor="tail", colorscale=[[0, 'red'], [1, 'red']], name='Gradient (Ascent)'
            ))

        # Tangent Plane
        if show_tangent:
            xt = np.linspace(x_val - 1.5, x_val + 1.5, 10)
            yt = np.linspace(y_val - 1.5, y_val + 1.5, 10)
            Xt, Yt = np.meshgrid(xt, yt)
            Zt = z0 + fx * (Xt - x_val) + fy * (Yt - y_val)
            fig.add_trace(go.Surface(x=Xt, y=Yt, z=Zt, colorscale='Gray', opacity=0.5, showscale=False, name='Tangent Plane'))

        fig.update_layout(scene=dict(xaxis_title='X (East)', yaxis_title='Y (North)', zaxis_title='Z (Height)'), height=600, margin=dict(l=0, r=0, b=0, t=30))
        st.plotly_chart(fig, use_container_width=True)
        
        # Visual Guide
        st.caption("""
        **Visual Key:** 🔴 **Red Dot:** Your Position | 
        🔻 **Red Cone:** Steepest Way Up (Water flows opposite) | 
        ⬜ **Gray Plane:** Leveling Surface
        """)
