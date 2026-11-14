# 🪐 PERIHELION 🛰️

### 🚀 Design. Analyse. Launch. Explore.

**PERIHELION** is a spacecraft design and space exploration simulation built with Python and Pygame. Design spacecraft, balance engineering constraints, select scientific instruments, and attempt missions across the Solar System.

Every component matters. Mass, propulsion, power, communications, reliability, and budget all influence whether your mission succeeds.

---

## 🌌 Features

- 🚀 **Spacecraft Design** — Build spacecraft by selecting components and instruments.
- 🪐 **Multiple Missions** — Explore the Moon, Mars, Europa, asteroids, Earth, and deep space.
- ⚙️ **Engineering Analysis** — Evaluate mass, propulsion, power, communications, thermal protection, and more.
- 📊 **Resource Management** — Balance mass, fuel, electrical power, data storage, and budget.
- 🔬 **Scientific Instruments** — Equip your spacecraft for mission-specific scientific objectives.
- 🎯 **Deterministic Simulation** — Mission outcomes are based on your spacecraft design and engineering constraints.
- 🏆 **Scoring System** — Earn points for mission success, scientific value, efficiency, and resource optimization.
- 🔁 **Redesign and Retry** — Learn from failures, improve your design, and launch again.

---

## 🪐 Available Missions

| Mission | Destination | Objective |
|---|---|---|
| 🌕 Lunar Exploration | Moon | Land a geology and seismic station |
| 🔴 Mars Exploration | Mars | Study the atmosphere and interior |
| 🧊 Europa Ocean Discovery | Europa | Investigate the hidden subsurface ocean |
| ☄️ Asteroid Research | Asteroid Belt | Study an asteroid's composition and shape |
| 🌍 Earth Observation | Earth | Observe Earth's atmosphere and surface |
| 🌌 Deep Space Exploration | Outer Heliosphere | Study magnetic fields and radiation |

## 🎮 Difficulty Levels

Choose the challenge that suits your engineering skills.

| Difficulty | Budget Multiplier | Requirement Multiplier |
|---|---:|---:|
| 🟢 Easy | 1.30× | 0.85× |
| 🔵 Normal | 1.00× | 1.00× |
| 🟠 Hard | 0.85× | 1.10× |
| 🔴 Expert | 0.72× | 1.20× |

Higher difficulties mean tighter budgets and more demanding mission requirements.

---

## 🛠️ Spacecraft Components

Build your spacecraft using ten component categories:

| Component | Purpose |
|---|---|
| 🧱 Structure | Supports the spacecraft |
| 🚀 Propulsion | Provides thrust and manoeuvring capability |
| ☀️ Solar Panels | Generate electrical power |
| 🔋 Batteries | Store electrical energy |
| 📡 Antenna | Communicates with mission control |
| 💻 Computer | Controls the spacecraft and stores data |
| 🌡️ Thermal System | Protects against extreme temperatures |
| 🧭 Attitude Control | Controls spacecraft orientation |
| 🎯 Navigation | Supports navigation and landing guidance |
| ⛽ Fuel Load | Supplies propellant for manoeuvres |

Each component has its own mass, cost, power consumption or generation, reliability, and performance characteristics.

## 🔬 Scientific Instruments

Choose instruments according to your mission objectives:

- 📷 Hi-Res Camera
- 🌈 Infrared Spectrometer
- 📡 Radar
- 🧲 Magnetometer
- 🌫️ Atmospheric Analyzer
- ☢️ Radiation Detector
- 🌍 Seismometer

Your instrument selection determines the scientific objectives your spacecraft can accomplish.

## 🚀 Launch Vehicles

Select a launch vehicle based on spacecraft mass and mission requirements:

- Vanguard-1
- Titan-V
- Aurora Heavy

## 🛰️ Orbit Profiles

Choose from six available orbit and trajectory profiles:

- Low Earth Orbit
- Geostationary Orbit
- Polar Orbit
- Lunar Transfer
- Mars Transfer
- Deep Space Trajectory

---

## 🧮 Engineering & Physics

PERIHELION uses simplified engineering models to evaluate spacecraft feasibility.

### 🚀 1. Rocket Equation (Tsiolkovsky)

The available change in velocity, or delta-v, is calculated using the rocket equation:

$$
\Delta v = I_{sp} \cdot g_0 \cdot \ln\left(\frac{m_0}{m_f}\right)
$$

Where:

- $\Delta v$ = Available change in velocity (m/s)
- $I_{sp}$ = Specific impulse (seconds)
- $g_0$ = Standard gravitational acceleration (9.81 m/s²)
- $m_0$ = Wet mass (kg)
- $m_f$ = Dry mass (kg)

More propellant increases available delta-v, but also increases spacecraft mass.

### ☀️ 2. Solar Power

Solar panel output decreases with the square of the distance from the Sun:

$$
P_{\text{actual}} = \frac{P_{\text{rated}}}{r^2}
$$

Where:

- $P_{\text{actual}}$ = Available solar power (W)
- $P_{\text{rated}}$ = Solar panel rated output at 1 AU (W)
- $r$ = Distance from the Sun (AU)

This makes power generation increasingly challenging for outer Solar System missions.

### 📡 3. Communication Bandwidth

Communication performance also decreases with the square of distance:

$$
B_{\text{actual}} = \frac{B_{\text{rated}}}{d^2}
$$

Where:

- $B_{\text{actual}}$ = Effective communication performance
- $B_{\text{rated}}$ = Rated antenna performance
- $d$ = Mission communication distance in AU

The simulation applies a scaling factor of 10.8 when converting its antenna performance into the downlink data rate.

### ⚖️ 4. Launch Mass

The spacecraft's wet mass is:

$$
m_{\text{wet}} = m_{\text{dry}} + m_{\text{fuel}}
$$

The launch vehicle's available payload capacity must be sufficient for the selected spacecraft and orbit profile.

### 🔋 5. Power Balance

The power system must generate enough electricity to support spacecraft consumption:

$$
P_{\text{generated}} \geq P_{\text{consumed}}
$$

Battery capacity also matters when solar generation cannot meet demand.

### 📊 6. Communications and Data

The spacecraft generates scientific data that must be transmitted or stored.

The simulation checks whether downlink capacity and onboard storage can handle the generated data over the mission duration.

---

## 🧪 Mission Feasibility Analysis

Before launch, PERIHELION evaluates several engineering constraints:

| Check | What It Evaluates |
|---|---|
| ⚖️ Launch Mass | Spacecraft mass versus launch capacity |
| 🛰️ Orbit / Trajectory | Whether the selected trajectory matches the mission |
| 🚀 Delta-v | Available propulsion versus required delta-v |
| 🔋 Power Balance | Electrical generation versus consumption |
| 📡 Comms & Data | Downlink and storage capacity |
| 🌡️ Thermal Protection | Whether thermal protection meets mission requirements |
| 🎯 Terminal Guidance | Whether a landing mission has sufficient guidance |
| 💰 Budget | Total spacecraft and launch costs |
| 🔬 Science Objectives | Required scientific observations |
| 🛡️ Reliability | Estimated system reliability |

### Feasibility Results

The analysis produces one of four classifications:

- 🟢 **READY FOR LAUNCH**
- 🟡 **FEASIBLE WITH WARNINGS**
- 🟠 **HIGH RISK**
- 🔴 **NOT FEASIBLE**

You can still launch a spacecraft that is not feasible. However, engineering failures can cause the mission to fail.

The simulation uses deterministic failure logic: the first violated critical constraint determines the failure event.

---

## 🏆 Scoring System

A successful mission is not just about reaching the destination. Efficient engineering matters too.

The maximum score is **1,000 points**.

| Category | Maximum Points |
|---|---:|
| 🎯 Mission Objectives | 300 |
| 🔬 Scientific Value | 200 |
| ⚙️ Engineering Efficiency | 150 |
| 💰 Budget Management | 100 |
| 🛡️ Reliability | 100 |
| 📊 Resource Optimization | 100 |
| 🚀 Mission Execution | 50 |
| **Total** | **1,000** |

Design a spacecraft that meets its objectives without wasting mass, money, fuel, or electrical power.

---

## 🎮 How to Play

1. Launch PERIHELION.
2. Select a mission and difficulty level.
3. Configure your spacecraft components.
4. Choose scientific instruments.
5. Select a launch vehicle and orbit profile.
6. Review your spacecraft's engineering dashboard.
7. Run the feasibility analysis.
8. Launch your spacecraft and observe the simulation.
9. Review the mission debrief and score.
10. Redesign your spacecraft and try again!

### 🖱️ Controls

| Input | Action |
|---|---|
| Mouse Click | Select components and interact with the interface |
| Arrow Buttons | Change component selections |
| Mouse Hover | View component information |
| ESC | Return to the main menu |

During simulation, use the available controls to pause, resume, restart, skip, or change simulation speed.

---

## 💻 Installation

### Requirements

- Python
- Pygame

### 1. Clone the repository

```bash
git clone https://github.com/Lord-Mortal/PERIHELION.git
```

### 2. Navigate to the project folder

```bash
cd PERIHELION
```

### 3. Install the dependency

```bash
pip install pygame-ce
```

### 4. Run the simulation

```bash
python perihelion.py
```

---

## 📁 Project Structure

```text
PERIHELION/
│
├── engine.py       # Mission data, engineering calculations,
│                   # feasibility analysis and scoring
│
├── perihelion.py   # Pygame interface and simulation
│
└── README.md       # Project documentation
```

---

## 🧠 Engineering Philosophy

PERIHELION is built around a simple idea:

**Every engineering decision has a consequence.**

A larger rocket may solve a mass problem, but it costs more. More instruments may increase scientific value, but they consume additional power and generate more data. More fuel increases delta-v, but also increases launch mass.

The challenge is to find the right balance.

---

## 🌟 Future Improvements

Potential directions for expanding the project:

- 🌍 Additional planetary destinations
- 🛰️ More spacecraft components
- 🔬 Expanded scientific objectives
- 📈 More detailed telemetry and mission analytics
- 🪐 Additional orbital mechanics and mission scenarios

---

##
