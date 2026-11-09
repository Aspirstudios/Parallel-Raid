<div align="center">
<pre>
               ██████╗  █████╗ ██████╗  █████╗ ██╗     ██╗     ███████╗██╗         ██████╗  █████╗ ██╗██████╗
               ██╔══██╗██╔══██╗██╔══██╗██╔══██╗██║     ██║     ██╔════╝██║         ██╔══██╗██╔══██╗██║██╔══██╗
               ██████╔╝███████║██████╔╝███████║██║     ██║     █████╗  ██║         ██████╔╝███████║██║██║  ██║
               ██╔═══╝ ██╔══██║██╔══██╗██╔══██║██║     ██║     ██╔══╝  ██║         ██╔══██╗██╔══██║██║██║  ██║
               ██║     ██║  ██║██║  ██║██║  ██║███████╗███████╗███████╗███████╗    ██║  ██║██║  ██║██║██████╔╝
               ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚══════╝    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═════╝
</pre>

<div align="center">


![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-2.x-34A853?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-4B4B4B?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Beta-orange?style=for-the-badge)



</div>

---

## What is *Parallel Raid*?

**Parallel Raid** is a **top-down** tactical shooter written **entirely in Python** with `pygame`, which pays tribute to the classics of Counter-Strike (1.6, Source, CS:GO and CS2).

> Intelligent bots and pixel art graphics, varied maps and LAN multiplayer between computers


---

## ✨ Features

### 🎮 Gameplay
- **Classic bomb defusal mode**: the **Landers (T)** plant the C4, the **Kyras (CT)** defuse it
- **Configurable rounds**: first to **3, 6, 10 or 15** rounds
- **Full economy**: rewards for victory/defeat, streak bonuses, starting and maximum money
- **Buy system** with vest, defuse kit and 11 weapons divided by categories
- **AI bots**: *flow field* navigation, response to fire, cover, position memory
- **6 s freeze time** before each round, **20 s buy time** at the start

### 🔫 Arsenal (11 weapons)
| Category | Weapons |
|-----------|-------|
| **Pistols** | Glock, USP, Deagle |
| **SMGs** | MAC-10, MP5 |
| **Shotgun** | XM1014 (8 pellets) |
| **Rifles** | Galil, FAMAS, AK-47, M4A1 |
| **Sniper** | AWP (200 damage, one-shot) |

Each weapon has its own **damage, fire rate, recoil, spread, range and sound**.

### 🗺️ Maps (25 total)
- **Classic tributes**: Dust2, Inferno, Nuke, Train, Aztec, Mirage, Cbble, Chateau, Port, Prodigy, Rotterdam, Tuscan
- **Extended CS 1.6**: Italy, Piranesi, Office
- **CS:GO**: Overpass, Vertigo, Cache
- **CS2 / originals**: Ancient, Anubis, Agency
- **Nature**: Bayou, Monsoon, Cascade
- Each map has its own **visual style, weather, palette, props and decorative elements**

### 🎨 Procedural graphics engine
- **Ground** with FBM fractal noise, lit relief, cracks, cobblestones, carpet, ballast, dunes
- **Walls** with brick/concrete, extruded depth (front face + shadowed side), "danger" texts
- **Volumetric sprites**: barrels, crates, rocks, trees, palm trees — generated with height map + light
- **Lighting**: low-sun gradient, ambient occlusion, cast shadows, volumetric light shafts
- **Weather**: rain with drops, ripples and thunder; snow with blizzards and white blanket; reflective puddles
- **Dynamic vegetation**: tree canopies with parallax and wind, grass swaying over the characters, leaves blown by the wind
- **Interiors**: opaque ceilings that become transparent when entering, role-based furniture (warehouse, temple, office, library…)
- **Post-processing**: vignette, film grain, color grading, dust motes
<img width="1020" height="631" alt="1" src="https://github.com/user-attachments/assets/403f1dea-4bd2-4435-969a-73916cc10a10" />

<img width="1016" height="632" alt="5" src="https://github.com/user-attachments/assets/915c76bc-9d8c-41a2-b285-b9ac205ec34a" />


### 🌐 LAN multiplayer
- **Integrated UDP server and client** (optional `cs2d_server.py`)
- **Automatic discovery** via broadcast on port `25566`
- **Client-server movement reconciliation** (prediction + acknowledge)
- **Remote player interpolation** with 100 ms buffer
- **Basic anti-cheat**: input validation, time budget, command limits
- Up to **10 players** per match
<img width="1009" height="632" alt="3" src="https://github.com/user-attachments/assets/cd4165d2-2dce-441f-bb1e-a3cbf1161904" />
---

## 📦 Installation

### Requirements
- **Python 3.10+** ([download](https://www.python.org/downloads/))
- **pygame 2.x**
- *(optional but recommended)* **numpy** — required for photorealistic textures and synthesized audio
</div>
