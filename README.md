# Five-colourLegend: Five Elements Point Cloud Simulation

---

## 📖 Project Overview

**Five-colourLegend** is an interactive 3D visualisation project built with Python, transforming the ancient Chinese philosophy of the ***Wu Xing (Five Elements)*** (Metal, Wood, Water, Fire, Earth) into a dynamic particle system.

Inspired by the ancient Chinese theory of ***Wu Xing***, the project collects and categorises real colours extracted from natural phenomena — including biological species, minerals, celestial events, and geological formations — into five fundamental categories:
**Red (Fire), Yellow (Earth), Cyan (Wood), White (Metal), Black (Water)**.

Each colour cluster is visualised as a 3D point cloud and animated through mathematical motion models that mimic the natural dynamics associated with each element. 
Additionally, the concept of ***“mutual generation(相生)”*** is introduced to simulate energetic interactions and flows between the five elements, forming a continuous, cyclical dynamic system.

---

## 🚀 Usage

1. Clone the repository:

```bash
git clone https://github.com/ChristyHiii/Five-colourLegend.git
cd Five-colourLegend
```

2. Prepare your data files in `colour data/`:

| Name | R | G | B | Source from Nature |
| ---- | - | - | - | ------------------ |
| xxxx | 0 | 0 | 0 |   xxxxxxxxxxxxxx   |

The colours selected for this project are from: Pantone Colour System, Ral Colour System, and NCS. And we also referred to bird, insect, plant guides and mineralogical maps. We used ai to help organise the data.

3. Run the simulation:

```bash
python Five-colourLegend.py
```

4. Rotate, zoom, and explore the evolving 3D point cloud visualisation.

---

## 🔬 Motion Model Design

The core of this project lies in **translating symbolic meanings of the Five Elements into mathematical motion models**. Each cluster behaves according to a unique set of equations, and they are interconnected through a dynamic generative cycle.

### 🔥 Fire — Flickering and Expansion

* **Symbolism**: Vitality, creativity, upward energy
* **Model**: Global pulsation + independent particle jumping
* **Equations**:

    **[
P'(t) = C + (P - C) [1 + 0.08sin(0.5t)]
]
[
P'_z(t) += 1.2sin(5t + φ)
]**

Where ( P ) is the original particle position, ( C ) is the cluster center, and ( φ ) is a particle-specific phase offset.

Particles jump like burning flames.

---

### 💧 Water — Horizontal Flow and Surge

* **Symbolism**: Flexibility, adaptability, flow
* **Model**: Spiral flow in the X-Z plane + vertical oscillation
* **Equations**:

    **[
P'_x(t) = P_x + Rcos(ωt + φ) + 0.8sin(0.5t + φ​)
]
[
P'_z(t) = P_z + Rsin(ωt + φ) + 0.8cos(0.5t + φ​)
]
[
P'_y(t) += 0.2sin(1.0t + φ)
]**

Where ( R ) is the spiral radius, and ( ω ) is the flow speed.

Particles exhibit horizontal flow and soft, wave-like motion.

---

### 🌱 Wood — Growth and Sway

* **Symbolism**: Vitality, upward growth, expansion
* **Model**: Periodic vertical growth + gentle spatial swaying
* **Equations**:

    **[
P'*y(t) = P_y + Asin(0.5t) + B​sin(2.0t + φ​)
]
[
P'*{x,z}(t) += 0.25sin(0.5t + φ)
]**

Where ( A ) is the growth amplitude, and ( B ) is the sway amplitude.

This simulates tree-like vertical growth and wind-driven swaying.

---

### ⚙️ Metal — Contraction and Rotation

* **Symbolism**: Solidity, authority, inward force
* **Model**: Cluster rotation + periodic radius pulsation
* **Equations**:

    **[
P'_x(t) = P_x + [R(t)]cos(ωt + φ)
]
[
P'_z(t) = P_z + [Rsin(t)]sin(ωt + φ)
]
[
R(t) = 2.5 + 0.3sin(t)
]**

Where ( ω ) is the rotation speed.

The release and recovery of energy are demonstrated in the cycle.

---

### 🪨 Earth — Breathing and Stability

* **Symbolism**: Stability, support, structure
* **Model**: Rhythmic breathing-like scaling
* **Equations**:

    **[
P'(t) = P ⋅ [1.0 + 0.1 * 0.8sin(0.5t)]
]**

As heavy and steady as the breath of the earth.

---

## 🔁 Generative Cycle Modeling

The generative (“mutual-promoting”) cycle follows:

**Wood → Fire → Earth → Metal → Water → Wood**

To simulate this interaction, a **weak attraction field** is introduced between clusters:

**[
P'(t) = P(t) + ϵ(t) [C_target - P(t)]
]**

Where:

* ( C_target ): center of the next element in the cycle
* ( ϵ(t) = α[1 + sin(βt)] ): a time-varying attraction coefficient

This creates a subtle directional flow of energy between elements.

---

## 📐 Project Structure

```
📁 Main/
├─ colours/                     # Excel colour data files
├─ Five-colourLegend.py  # Main simulation script
├─ requirements.txt                # Documentation

📁 Test/      # Testfile
├─ ......

📃 README.md                # Documentation
```

---

## 🧠 Inadequacy

After testing, the **PyQt5 +PyQtGraph** library was finally selected for the implementation of the dynamic point cloud.
Unfortunately, PyQtGraph's GLScatterPlotItem cannot achieve mouse hover or click picking under OpenGL, so we are unable to display the names and natural sources corresponding to the colours.

The Plotly library can perfectly implement the function of picking up target points, but its own Scatter3d is static and cannot update the position of the point cloud in real time.
You can find the DataTest.py script in the Test folder. This is where we use Plotly to render the point cloud, and the effect is very good.

---

## 📜 License

MIT License © 2025 ChrisTing Huang
Free to use for learning, research, and creative projects. Contributions and forks are welcome!

🌟 If you enjoy this project, please ⭐ star the repository and share it — let more people experience the beauty of the Five Elements through computation.

---

## ✨ Author

**ChrisTing Huang** – [GitHub](https://github.com/ChristyHiii) | [Email](candybrownhuang@gmail.com)
