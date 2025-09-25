import open3d as o3d
import numpy as np
import math
import time

def create_ellipse_cloud(center, n_points=8000, a=6.0, b=1.8, c=3.5, color=[1,0,0]):
    """生成一个椭圆形分布的点云"""
    x = np.random.normal(0, 1, n_points) * a + center[0]
    y = np.random.normal(0, 1, n_points) * b + center[1]
    z = np.random.normal(0, 1, n_points) * c + center[2]

    points = np.vstack((x, y, z)).T
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd.paint_uniform_color(color)
    return pcd

# 五种颜色（赤黄青白黑）
colors = [
    [1, 0, 0],    # 赤
    [1, 1, 0],    # 黄
    [0, 0.5, 1],  # 青
    [1, 1, 1],    # 白
    [0, 0, 0]     # 黑
]

# 五边形顶点作为中心
radius = 8.0
centers = []
for i in range(5):
    theta = 2 * math.pi * i / 5
    centers.append([radius * math.cos(theta), radius * math.sin(theta), 0])

# 生成五个椭圆点云
pcds = []
for i, col in enumerate(colors):
    pcd = create_ellipse_cloud(center=centers[i], n_points=12000, a=6.0, b=1.8, c=3.5, color=col)
    pcds.append(pcd)

# 保存初始点
init_points = [np.asarray(pcd.points).copy() for pcd in pcds]

# 创建窗口
vis = o3d.visualization.VisualizerWithKeyCallback()
vis.create_window()
opt = vis.get_render_option()
opt.background_color = np.asarray([0.02, 0.02, 0.05])
opt.point_size = 6.0

# 初始相机参数：进入点云中心
ctr = vis.get_view_control()
params = ctr.convert_to_pinhole_camera_parameters()
params.extrinsic = np.array([
    [1, 0, 0, 0],   # 相机在中心
    [0, 1, 0, 0],
    [0, 0, 1, -2],  # Z方向往里一点（相机在点云群里面）
    [0, 0, 0, 1]
])
ctr.convert_from_pinhole_camera_parameters(params)

# 限制缩放范围
zoom_level = [1.0]  # 缓存缩放
def zoom_in(vis):
    if zoom_level[0] > 0.7:  # 下限
        ctr.scale(0.9)
        zoom_level[0] *= 0.9
def zoom_out(vis):
    if zoom_level[0] < 1.3:  # 上限
        ctr.scale(1.1)
        zoom_level[0] *= 1.1
vis.register_key_callback(ord("Z"), zoom_in)   # 按 Z 放大
vis.register_key_callback(ord("X"), zoom_out)  # 按 X 缩小

# ESC 退出
def exit_callback(vis):
    vis.close()
    return False
vis.register_key_callback(256, exit_callback)

for pcd in pcds:
    vis.add_geometry(pcd)

# 动态漂浮
t = 0
while vis.poll_events():
    for i, pcd in enumerate(pcds):
        base = init_points[i]
        noise = 0.02 * np.random.randn(*base.shape)  # 随机小扰动
        drift = 0.1 * np.sin(0.02 * t + np.random.rand(*base.shape))  # 慢速、振幅更大
        new_points = base + noise + drift
        pcd.points = o3d.utility.Vector3dVector(new_points)
        vis.update_geometry(pcd)

    vis.update_renderer()
    t += 1   # 时间步更慢
    time.sleep(0.05)

vis.destroy_window()
