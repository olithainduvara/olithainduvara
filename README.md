<!-- ═══════════════════════════════ HEADER ═══════════════════════════════ -->
<div align="center">

<img src="assets/header.png" width="100%" alt="Olitha Induvara, Electrical and Electronic Engineering Undergraduate, University of Peradeniya"/>

<br/><br/>

[![Portfolio](https://img.shields.io/badge/Portfolio-olithainduvara.github.io-4A9EFF?style=for-the-badge&logo=googlechrome&logoColor=white)](https://olithainduvara.github.io/OlithaInduvara_Portfolio/)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Olitha_Induvara-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/olitha-induvara-16329733b/)
[![Email](https://img.shields.io/badge/Email-olithainduvara@gmail.com-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:olithainduvara@gmail.com)

</div>

---

## 👋 About Me

<table>
<tr>
<td width="32%" valign="top" align="center">
<img src="assets/about-photo.png" width="100%" alt="Olitha Induvara at EngEx 2025"/>
</td>
<td width="68%" valign="top">

I'm a third-year **Electrical & Electronic Engineering** undergraduate at the **University of Peradeniya, Sri Lanka**.

I build systems **end to end**: I solder the sensor node, write the firmware, design the radio link, and ship the desktop, web or mobile software that turns the data into decisions.

<br/>

| | |
|:--|:--|
| 🌊 **Now building** | **FloodLink**, a LoRa flood early-warning system for the Mahaweli River |
| ✈️ **Also building** | **FlyMe**, ESP32 LoRa telemetry and an Android ground station for an RC aircraft |
| 🧠 **Exploring** | River-level forecasting with classical ML and neural networks |
| 🏆 **Recognition** | 2nd Place, *Idea to Invention 2025* |
| 🎥 **Beyond code** | EngEx 2025 Media Lead · DJI drone pilot · photographer · astronomy enthusiast |
| 🤝 **Community** | IEEE PES & IEEE MTT-S · Former President, Buddhist Society (FoE) |

</td>
</tr>
</table>

---

## 🧭 What I Work On

<table>
<tr>
<td width="33%" valign="top">

### 🔌 Embedded & IoT
ESP32-C3 and STM32 firmware, LoRa (SX1278) radio links, IMU sensor fusion, GPS, ultrasonic level sensing, custom binary packet protocols and hand-built hardware.

</td>
<td width="33%" valign="top">

### 📊 Data & Modelling
Time-series cleaning and merging, lead-lag analysis, regression, tree ensembles, MLPs and LSTMs, with leak-free cross-validation for hydrological forecasting.

</td>
<td width="33%" valign="top">

### 🖥️ Apps & Dashboards
PySide6 desktop apps packaged as standalone `.exe`s, zero-dependency web dashboards, and an Android ground station over Wi-Fi/UDP and USB-OTG.

</td>
</tr>
</table>

---

## 🚀 Featured Projects

> Projects marked 🔒 are in private repositories. This page gives an overview of each one.

### 🌊 FloodLink: Flood Early-Warning Ecosystem

Several projects that together cover the full pipeline from river sensor to community alert on the Mahaweli River, Sri Lanka:

```mermaid
flowchart LR
    A["📡 Sensor node<br/>ESP32-C3 · JSN-SR04T"] -->|LoRa 433 MHz| B["📶 Gateway"]
    B -->|UDP JSON| C["🖥️ FloodLink dashboard<br/>ETA prediction"]
    C --> D["🔔 Telegram / WhatsApp alerts"]
    E["🛰️ ArcGIS gauge feed"] --> F["🌐 Web Monitor"]
    E --> G["🔄 HydroSync Studio<br/>dataset builder"]
    G --> H["🧠 Water-level models<br/>1–6 h forecasts"]
```

<!-- ─────────────── FloodLink 1.0 ─────────────── -->
<img src="assets/banners/floodlink.png" width="100%" alt="FloodLink 1.0"/>

**🔒 FloodLink 1.0**: a low-cost flood early-warning prototype, and the project that won **2nd Place at Idea to Invention 2025**.

- Hand-soldered **ESP32-C3 + JSN-SR04T** ultrasonic sensor nodes send river levels over **SX1278 LoRa** to a central gateway.
- A live dashboard receives UDP telemetry and fits a regression model to estimate **when each flood threshold (Alert, Minor, Major) will be crossed**.
- A local NDJSON event bus feeds **Telegram** and **WhatsApp (Twilio)** dispatchers that send alerts to the community.
- A Streamlit simulation dashboard is included for demos and testing.

<br/>

<!-- ─────────────── Flood Web Monitor ─────────────── -->
<a href="https://olithainduvara.github.io/Peradeniya-And-Nawalapitiya-Water-Level-and-Rainfall_WebMonitor-Mahaweli-River-/"><img src="assets/banners/flood-web-monitor.png" width="100%" alt="Flood Web Monitor"/></a>

**Flood Web Monitor**: a real-time water-level and rainfall dashboard for the Peradeniya and Nawalapitiya gauges.

- Pulls the last 3 days of readings from a public **ArcGIS REST** feed and refreshes itself every 5 minutes.
- Plots both stations against the official flood thresholds and **raises an alert banner** when one is crossed.
- Offers CSV export per station or combined. All times are shown in Sri Lanka time.
- The whole app is a single `index.html` with **no dependencies and no build step**, deployed on GitHub Pages.

[![Live Demo](https://img.shields.io/badge/Live_Demo-Open_Dashboard-4A9EFF?style=for-the-badge&logo=googlechrome&logoColor=white)](https://olithainduvara.github.io/Peradeniya-And-Nawalapitiya-Water-Level-and-Rainfall_WebMonitor-Mahaweli-River-/)
[![Repo](https://img.shields.io/badge/Source-GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/olithainduvara/Peradeniya-And-Nawalapitiya-Water-Level-and-Rainfall_WebMonitor-Mahaweli-River-)

<br/>

<!-- ─────────────── HydroSync Studio ─────────────── -->
<img src="assets/banners/hydrosync.png" width="100%" alt="HydroSync Studio"/>

**🔒 HydroSync Studio** (FloodLink 2.0): a desktop app that turns messy, overlapping gauge downloads into one clean training dataset.

- Merges rolling **72-hour exports** into a single row per hour per station. On the current data it removed **481 duplicate readings**.
- Handles **three timestamp formats**, one of them in UTC (verified against 68 overlapping hours), and converts them all to Sri Lanka time.
- Detects recording gaps so that no rows are invented across them, and fills only short dropouts.
- Has a **PySide6** interface with dark and light themes, drag-and-drop import and a headless CLI, and ships as a standalone **Windows .exe**.

<br/>

<!-- ─────────────── Water Level Forecasting ─────────────── -->
<img src="assets/banners/water-level-model.png" width="100%" alt="Water Level Forecasting"/>

**🔒 Peradeniya Water Level Forecasting**: forecasts the Peradeniya gauge from the upstream Nawalapitiya gauge and rainfall at both stations.

- Lead-lag analysis shows that Nawalapitiya **leads Peradeniya by 3–4 hours**, and that delay is what makes forecasting possible.
- Compares **9 models** (Ridge, Random Forest, Extra Trees, Gradient Boosting, SVR, MLP, LSTM and baselines) at **0, 1, 3 and 6 h lead times**.
- Uses leave-one-part-out cross-validation, so no feature is ever computed across the 39-day gap in the data.
- **Best result: 0.14 m RMSE with NSE 0.99 at 1 hour ahead**, a 45% improvement over the persistence baseline.

<br/>

### ✈️ FlyMe: RC Aircraft Telemetry & Ground Station

<!-- ─────────────── FlyMe Hardware ─────────────── -->
<img src="assets/banners/flyme-hardware.png" width="100%" alt="FlyMe Hardware"/>

**🔒 FlyMe Hardware**: ESP32-C3 firmware for the aircraft and its ground receiver.

- **200 Hz Mahony attitude estimation** on an MPU6500 IMU, plus NEO-M8N GPS for position and ground speed.
- A packed **47-byte telemetry frame sent 10 times per second** over LoRa (433 MHz, SF7), transmitted asynchronously so the 200 Hz filter never blocks.
- An acknowledged command uplink carries ground commands such as sensor calibration. Each command is repeated until the aircraft echoes its ID.
- The ground receiver bridges LoRa to **USB serial, Wi-Fi UDP and HTTP** using a documented JSON link protocol.

<br/>

<!-- ─────────────── FlyMe App ─────────────── -->
<img src="assets/banners/flyme-app.png" width="100%" alt="FlyMe Ground Station"/>

**🔒 FlyMe Ground Station**: an Android app for tracking the aircraft live.

- Shows the aircraft on satellite, dark or street maps, with distance from home, altitude, speed, heading, range rings and a return-to-home arrow.
- A full-screen HUD shows link and LoRa signal, satellites, battery and a flight timer.
- **Voice and vibration alerts** for signal loss, GPS fix loss, maximum distance, low altitude and low battery.
- Records flights automatically, with replay and **GPX export**. Connects over Wi-Fi (UDP/HTTP) or a **USB-OTG** cable, and has a built-in demo flight.

<br/>

### 🔬 More Engineering Projects

<!-- ─────────────── EMG Recorder ─────────────── -->
<a href="https://github.com/olithainduvara/EMG-Data-Recorder-Via-NiDAQ-card"><img src="assets/banners/emg-recorder.png" width="100%" alt="EMG Recorder"/></a>

**EMG Recorder**: a desktop tool for recording muscle signals through the NI USB-6009 data acquisition card.

- Acquires, plots and records **three EMG channels** at the same time, paired with a hand-soldered instrumentation-amplifier front end.
- A configurable **notch filter** removes mains interference.
- Smooth under load, with a **worst-case UI stall of 49 ms**, and dark and light themes.
- Packaged as a **standalone Windows executable** that needs no Python installation.

[![Repo](https://img.shields.io/badge/Source-GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/olithainduvara/EMG-Data-Recorder-Via-NiDAQ-card)

<br/>

<!-- ─────────────── MicroMouse ─────────────── -->
<img src="assets/banners/micromouse.png" width="100%" alt="MicroMouse"/>

**🔒 MicroMouse**: an autonomous maze-solving robot built on the **STM32F411 BlackPill**.

- Dual-motor PWM speed and direction control through an H-bridge driver.
- Built with PlatformIO (Arduino framework), plus STM32Cube HAL projects for low-level peripheral work.
- *In progress:* wall sensing and maze-solving algorithms.

---

## 🛠️ Tech Stack

<div align="center">

**Languages**

<img src="https://skillicons.dev/icons?i=python,cpp,c,java,js,html,css&theme=dark" alt="Languages"/>

**Hardware & Embedded**

<img src="https://skillicons.dev/icons?i=arduino,raspberrypi&theme=dark" alt="Hardware"/>

![ESP32](https://img.shields.io/badge/ESP32-E7352C?style=for-the-badge&logo=espressif&logoColor=white)
![STM32](https://img.shields.io/badge/STM32-03234B?style=for-the-badge&logo=stmicroelectronics&logoColor=white)
![PlatformIO](https://img.shields.io/badge/PlatformIO-F5822A?style=for-the-badge&logo=platformio&logoColor=white)
![LoRa](https://img.shields.io/badge/LoRa-1E88E5?style=for-the-badge)
![NI DAQ](https://img.shields.io/badge/NI--DAQmx-FFD100?style=for-the-badge)

**Data, ML & Apps**

![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![Qt](https://img.shields.io/badge/PySide6-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![Android](https://img.shields.io/badge/Android-3DDC84?style=for-the-badge&logo=android&logoColor=white)

**Tools**

<img src="https://skillicons.dev/icons?i=git,github,vscode,androidstudio,windows&theme=dark" alt="Tools"/>

</div>

---

## 🏆 Highlights

| | |
|:--|:--|
| 🥈 | **2nd Place, Idea to Invention 2025** with FloodLink |
| 🎬 | **Media Lead, EngEx 2025**, Sri Lanka's largest engineering exhibition |
| 🔭 | **International Asteroid Search Campaign**, citizen-science asteroid hunting |
| 🎤 | Invited speaker on *AI, Technology & Future Robotics* for the Lions Club of Puttalam |
| 🚁 | Aerial cinematography for the university's **first-ever drone show** |

---

## 📈 GitHub Stats

<div align="center">

<img height="170" src="https://github-profile-summary-cards.vercel.app/api/cards/stats?username=olithainduvara&theme=tokyonight" alt="GitHub stats"/>
<img height="170" src="https://github-profile-summary-cards.vercel.app/api/cards/repos-per-language?username=olithainduvara&theme=tokyonight" alt="Repos per language"/>

<img src="https://streak-stats.demolab.com?user=olithainduvara&hide_border=true&theme=tokyonight" alt="GitHub streak" width="60%"/>

</div>

---

<div align="center">

<img src="assets/footer.png" width="100%" alt="Let's build something that matters"/>

<br/><br/>

[![Portfolio](https://img.shields.io/badge/-Portfolio-4A9EFF?style=flat-square&logo=googlechrome&logoColor=white)](https://olithainduvara.github.io/OlithaInduvara_Portfolio/)
[![LinkedIn](https://img.shields.io/badge/-LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/olitha-induvara-16329733b/)
[![Gmail](https://img.shields.io/badge/-olithainduvara@gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white)](mailto:olithainduvara@gmail.com)

<img src="https://komarev.com/ghpvc/?username=olithainduvara&style=flat-square&color=4A9EFF&label=Profile+views" alt="Profile views"/>

</div>
