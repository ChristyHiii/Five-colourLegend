# file: clustered_color_point_cloud_tangent_pyqtgraph.py
import sys
import pandas as pd
import numpy as np
from PyQt5 import QtWidgets
import pyqtgraph as pg
import pyqtgraph.opengl as gl


# ========== 配置 Excel 路径 ==========
category_files = {
    "青": "Test/cyan2.csv",
    "赤": "Test/red2.csv",
    "黄": "Test/yellow2.csv",
    "白": "Test/white2.csv",
    "黑": "Test/black2.csv",
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
R = 10   # 大球半径
r = 100   # 小球半径（团簇扩散）
n_points = 5   # 每个颜色类别点数
size_points = 2    # 每个点云大小


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


# ========== PyQtGraph 可视化 ==========
class PointCloudApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("五色点云 - PyQtGraph 版本")
        self.resize(1920, 1080)

        # OpenGL 3D 窗口
        self.view = gl.GLViewWidget()
        self.view.opts['distance'] = 80  # 控制相机远近
        self.setCentralWidget(self.view)

        # # 坐标轴
        # axis = gl.GLAxisItem()
        # axis.setSize(30, 30, 30)
        # self.view.addItem(axis)

        # # 大球参考 (透明网格)
        # self.add_sphere(radius=R, color=(0.5, 0.5, 0.5, 0.1))

        # 添加每个颜色类别的点云
        for cat, file_path in category_files.items():
            df = pd.read_excel(file_path)
            df["Name"] = df["Name"].astype(str).str.strip()

            dx, dy, dz = directions[cat]
            cluster_center = (dx * (R + r), dy * (R + r), dz * (R + r))  # 团簇球心

            for _, row in df.iterrows():
                red, green, blue = int(row["R"]), int(row["G"]), int(row["B"])
                color_rgb = (red / 255.0, green / 255.0, blue / 255.0, 0.9)

                x, y, z = sample_points(cluster_center, n_points, r)
                pts = np.vstack([x, y, z]).T

                scatter = gl.GLScatterPlotItem(pos=pts, color=color_rgb, size=size_points, pxMode=False)
                self.view.addItem(scatter)

    # def add_sphere(self, radius=R, color=(1, 1, 1, 0.2)):
    #     """绘制一个球体网格"""
    #     md = gl.MeshData.sphere(rows=20, cols=40, radius=radius)
    #     mesh = gl.GLMeshItem(
    #         meshdata=md,
    #         smooth=True,
    #         color=color,
    #         shader="balloon",
    #         drawEdges=True,
    #     )
    #     self.view.addItem(mesh)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = PointCloudApp()
    window.show()
    sys.exit(app.exec_())
