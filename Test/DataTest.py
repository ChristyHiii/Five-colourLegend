# file: clustered_color_point_cloud_tangent.py
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio

pio.renderers.default = "browser"

category_files = {
    "青": "Test/cyan.xlsx",
    "赤": "Test/red.xlsx",
    "黄": "Test/yellow.xlsx",
    "白": "Test/white.xlsx",
    "黑": "Test/black.xlsx",
}

# === Fibonacci sphere 算法 ===
def fibonacci_sphere(samples):
    points = []
    golden_angle = np.pi * (3.0 - np.sqrt(5.0))
    for i in range(samples):
        z = 1 - (2 * i) / (samples - 1)
        radius = np.sqrt(1 - z * z)
        theta = golden_angle * i
        x = np.cos(theta) * radius
        y = np.sin(theta) * radius
        points.append((x, y, z))
    return points

directions = dict(zip(category_files.keys(), fibonacci_sphere(len(category_files))))

# === 参数 ===
R = 10     # 大球半径
r = 20    # 小球半径（团簇扩散）
n_points = 100

fig = go.Figure()

# 均匀采样球体内点
def sample_points(center, n_points, r):
    cx, cy, cz = center
    u = np.random.rand(n_points)
    costheta = np.random.uniform(-1, 1, n_points)
    theta = np.random.uniform(0, 2*np.pi, n_points)
    
    radius = r * u ** (1/3)
    x = radius * np.sqrt(1 - costheta**2) * np.cos(theta) + cx
    y = radius * np.sqrt(1 - costheta**2) * np.sin(theta) + cy
    z = radius * costheta + cz
    return x, y, z

# 绘制每个大类的团簇
for cat, file_path in category_files.items():
    df = pd.read_excel(file_path)
    df["Name"] = df["Name"].astype(str).str.strip()
    
    dx, dy, dz = directions[cat]
    cluster_center = (dx * (R + r), dy * (R + r), dz * (R + r))  # 小球球心
    
    for _, row in df.iterrows():
        name, red, green, blue = row["Name"], int(row["R"]), int(row["G"]), int(row["B"])
        color_rgb = f"rgb({red},{green},{blue})"
        
        x, y, z = sample_points(cluster_center, n_points, r)
        
        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z,
            mode="markers",
            marker=dict(size=5, color=color_rgb, opacity=0.85),
            hovertext=[f"{cat}-{name}"] * n_points,
            hoverinfo="text"
        ))

# 绘制大球（透明）帮助观察
u, v = np.mgrid[0:2*np.pi:50j, 0:np.pi:25j]
x = R * np.cos(u) * np.sin(v)
y = R * np.sin(u) * np.sin(v)
z = R * np.cos(v)
fig.add_trace(go.Surface(
    x=x, y=y, z=z,
    opacity=0.1, showscale=False, colorscale="Greys"
))

fig.update_layout(
    scene=dict(
        xaxis=dict(showgrid=False, visible=False),
        yaxis=dict(showgrid=False, visible=False),
        zaxis=dict(showgrid=False, visible=False),
    ),
    margin=dict(l=0, r=0, t=0, b=0),
    showlegend=False,
    scene_camera=dict(
        eye=dict(x=0, y=0, z=0),  # 眼睛就在球心
    )
)

fig.show()
