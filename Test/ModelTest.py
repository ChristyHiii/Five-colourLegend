import sys
import numpy as np
from PyQt5 import QtWidgets, QtCore
import pyqtgraph.opengl as gl

# 五行颜色
colors = {
    "金": (1, 0.84, 0, 1),
    "木": (0, 1, 0, 1),
    "水": (0, 0.5, 1, 1),
    "火": (1, 0.2, 0, 1),
    "土": (0.7, 0.4, 0.2, 1)
}

N = 200

def create_cluster(center, scale=1.0):
    return center + np.random.normal(size=(N, 3)) * scale

centers = {
    "金": np.array([5, 0, 0]),
    "木": np.array([-5, 0, 0]),
    "水": np.array([0, 0, 5]),
    "火": np.array([0, 0, -5]),
    "土": np.array([0, -5, 0])
}

class FiveElementsWindow(gl.GLViewWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("五行点云动态演示")
        self.setCameraPosition(distance=30, elevation=12, azimuth=45)

        self.clusters = {}
        self.base_positions = {}
        self.phase_offsets = {}

        for i, (name, center) in enumerate(centers.items()):
            pos = create_cluster(center, scale=1.5)
            self.base_positions[name] = pos.copy()
            self.phase_offsets[name] = np.random.uniform(0, 2*np.pi, N)
            color_arr = np.tile(colors[name], (N, 1))
            scatter = gl.GLScatterPlotItem(pos=pos, size=6, color=color_arr, pxMode=True)
            self.addItem(scatter)
            self.clusters[name] = scatter

        self.phase = 0
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_positions)
        self.timer.start(30)

    def update_positions(self):
        self.phase += 0.05

        for i, (name, scatter) in enumerate(self.clusters.items()):
            base = self.base_positions[name]
            pos = base.copy()

            if name == "火":
                # 🔥 火：回到原本的膨胀收缩 + 粒子独立跳动
                center = np.mean(base, axis=0)
                scale = 1 + 0.02 * np.sin(self.phase * 0.3)  # 更剧烈的整体膨胀收缩
                jitter = 0.5 * np.sin(7 * self.phase + self.phase_offsets[name])  # 每个粒子独立上下跳动
                new_points = center + (pos - center) * scale
                new_points[:, 2] += jitter  # Z 轴方向的火苗跳动
                pos = new_points

            elif name == "水":
                # 💧 水：增强“水平面流动感”
                flow_speed = 0.2
                spiral_radius = 2.0
                phase = self.phase + self.phase_offsets[name]

                # 在 X-Z 平面做螺旋流动（类似水平旋涡）
                pos[:, 0] = base[:, 0] + spiral_radius * np.cos(flow_speed * phase) + 0.8 * np.sin(0.5 * self.phase + phase)
                pos[:, 2] = base[:, 2] + spiral_radius * np.sin(flow_speed * phase) + 0.8 * np.cos(0.5 * self.phase + phase)

                # 轻微上下波动（像水面起伏）
                pos[:, 1] += 0.2 * np.sin(0.7 * self.phase + phase)

            elif name == "木":
                # 🌿 木：增强生长 + 摆动
                growth_speed = 1.0   # ↑ 增大生长速度
                wobble_amp = 0.8      # ↑ 增大摆动幅度
                wobble_freq = 2.0     # ↑ 稍微加快摆动频率
                phase = np.linspace(0, 2 * np.pi, N)

                pos[:, 1] += growth_speed * np.sin(self.phase * 0.5) + wobble_amp * np.sin(wobble_freq * self.phase + phase)
                pos[:, 0] += 0.25 * np.sin(0.5 * self.phase + phase)  # X 方向摆动更明显
                pos[:, 2] += 0.25 * np.cos(0.5 * self.phase + phase)  # Z 方向摆动更明显

            elif name == "金":
                # ⚙️ 金：旋转 + 扩张
                rot_speed = 0.8
                radius = 2.5 + 0.3 * np.sin(self.phase)
                theta = rot_speed * self.phase + np.linspace(0, 2 * np.pi, N)
                pos[:, 0] = base[:, 0] + radius * np.cos(theta)
                pos[:, 2] = base[:, 2] + radius * np.sin(theta)

            elif name == "土":
                # 🪨 土：缓慢脉动
                pulse = 0.4 * np.sin(0.5 * self.phase)
                pos *= (1 + pulse * 0.1)

            scatter.setData(pos=pos)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = FiveElementsWindow()
    w.show()
    sys.exit(app.exec_())
