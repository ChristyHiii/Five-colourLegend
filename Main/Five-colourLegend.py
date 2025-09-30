# file: clustered_color_point_cloud_dynamic.py
import sys
import numpy as np
import pandas as pd
from collections import defaultdict
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
import pyqtgraph.opengl as gl

# Excel
category_files = {
    "Cyan": "Main/colour data/Cyan.xlsx",
    "Red": "Main/colour data/Red.xlsx",
    "Yellow": "Main/colour data/Yellow.xlsx",
    "White": "Main/colour data/White.xlsx",
    "Black": "Main/colour data/Black.xlsx",
}

# Fibonacci Sphere algorithm
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

# cluster parameters
directions = dict(zip(category_files.keys(), fibonacci_sphere(len(category_files))))
R = 5    # datum sphere radius
r = 30    # cluster diffusion radius
n_points = 5  # number of points for each colour

# uniformly sample points within the sphere
def sample_points(center, n_points, r):
    cx, cy, cz = center
    u = np.random.rand(n_points)
    costheta = np.random.uniform(-1, 1, n_points)
    theta = np.random.uniform(0, 2*np.pi, n_points)

    radius = r * u ** (1/3)
    x = radius * np.sqrt(1 - costheta**2) * np.cos(theta) + cx
    y = radius * np.sqrt(1 - costheta**2) * np.sin(theta) + cy
    z = radius * costheta + cz
    return np.vstack((x, y, z)).T

# window settings
class ClusteredWindow(gl.GLViewWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Five-colour Legend")
        self.resize(1920, 1080)
        self.setCameraPosition(distance=100, elevation=40, azimuth=30)

        self.clusters = {}
        self.base_positions = {}
        self.phase_offsets = {}
        self.category_map = {
            "Red": "fire",
            "Black": "water",
            "Cyan": "wood",
            "White": "metal",
            "Yellow": "earth",
        }   # map: colour category -> dynamic effect

        # read data and create point clouds
        for cat, file_path in category_files.items():
            df = pd.read_excel(file_path)
            df["Name"] = df["Name"].astype(str).str.strip()

            dx, dy, dz = directions[cat]
            cluster_center = np.array([dx * (R + r), dy * (R + r), dz * (R + r)])

            for _, row in df.iterrows():
                red, green, blue = int(row["R"]), int(row["G"]), int(row["B"])
                color_rgb = (red/255, green/255, blue/255, 1)

                pos = sample_points(cluster_center, n_points, r)
                scatter = gl.GLScatterPlotItem(pos=pos, size=10, color=color_rgb, pxMode=True)   # point size
                self.addItem(scatter)

                key = f"{cat}-{row['Name']}"
                self.clusters[key] = scatter
                self.base_positions[key] = pos.copy()
                self.phase_offsets[key] = np.random.uniform(0, 2*np.pi, n_points)

        # five elements generation map
        self.sheng_map = {
            "wood": "fire",
            "fire": "earth",
            "earth": "metal",
            "metal": "water",
            "water": "wood"
        }

        # timer
        self.phase = 0
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_positions)
        self.timer.start(30)

    def compute_model_centers(self):
        accum = defaultdict(list)
        for key, base in self.base_positions.items():
            cat = key.split("-")[0]
            model = self.category_map.get(cat, "none")
            if model != "none":
                accum[model].append(np.mean(base, axis=0))
        model_centers = {}
        for model, centers in accum.items():
            model_centers[model] = np.mean(np.vstack(centers), axis=0)
        return model_centers

    def update_positions(self):
        self.phase += 0.05

        model_centers = self.compute_model_centers()
        # parameters
        base_influence = 0.1
        influence_mod = 0.5 * (1 + np.sin(self.phase * 0.2))
        influence_scalar = base_influence * influence_mod

        for key, scatter in self.clusters.items():
            base = self.base_positions[key]
            pos = base.copy()
            phase_arr = self.phase_offsets[key]

            # choose dynamic effect
            cat = key.split("-")[0]
            model = self.category_map.get(cat, "none")

            if model == "fire":
                # Fire: expansion + particle jitter
                center = np.mean(base, axis=0)
                scale = 1 + 0.08 * np.sin(self.phase * 0.5) # overall expansion/contraction
                jitter = 1.2 * np.sin(5 * self.phase + phase_arr)  # individual particle jitter
                new_points = center + (pos - center) * scale
                new_points[:, 2] += jitter  # z-axis jitter
                pos = new_points

            elif model == "water":
                # Water: horizontal vortex + vertical fluctuation
                flow_speed = 1.2
                spiral_radius = 5.0
                phase_vec = self.phase + phase_arr
                # spiral flow in x-z plane
                pos[:, 0] = base[:, 0] + spiral_radius * np.cos(flow_speed * phase_vec) + 0.8 * np.sin(0.5 * self.phase + phase_vec)
                pos[:, 2] = base[:, 2] + spiral_radius * np.sin(flow_speed * phase_vec) + 0.8 * np.cos(0.5 * self.phase + phase_vec)
                # slight vertical wave
                pos[:, 1] += 0.2 * np.sin(1.0 * self.phase + phase_vec)

            elif model == "wood":
                # Wood: growth + wobble
                growth_speed = 5.5    # growth speed
                wobble_amp = 1.2      # wobble amplitude
                wobble_freq = 2.0     # wobble frequency
                per_particle_phase = np.linspace(0, 2 * np.pi, n_points)

                pos[:, 1] += growth_speed * np.sin(self.phase * 0.5) + wobble_amp * np.sin(wobble_freq * self.phase + per_particle_phase)
                pos[:, 0] += 0.25 * np.sin(0.5 * self.phase + per_particle_phase)
                pos[:, 2] += 0.25 * np.cos(0.5 * self.phase + per_particle_phase)

            elif model == "metal":
                # Metal: rotation + expansion
                rot_speed = 1.0
                radius = 2.5 + 0.3 * np.sin(self.phase)
                theta = rot_speed * self.phase + np.linspace(0, 2 * np.pi, n_points)
                pos[:, 0] = base[:, 0] + radius * np.cos(theta)
                pos[:, 2] = base[:, 2] + radius * np.sin(theta)

            elif model == "earth":
                # Earth: slow pulsation
                pulse = 0.8 * np.sin(0.5 * self.phase)
                pos *= (1 + pulse * 0.1)

            # 五行相生影响
            target_model = self.sheng_map.get(model, None)
            if target_model and target_model in model_centers:
                target_center = model_centers[target_model]
                per_particle_mod = 0.5 * (1 + np.sin(self.phase * 0.3 + phase_arr))
                per_particle_mod = per_particle_mod.reshape(-1, 1)
                influence = influence_scalar * per_particle_mod
                direction = (target_center.reshape(1, 3) - pos)
                pos += influence * direction

            scatter.setData(pos=pos)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = ClusteredWindow()
    w.show()
    sys.exit(app.exec_())
