# 🎮 CONNECT4: Neural Arena

> **An AI-powered Connect4 game featuring intelligent game-tree search, real-time AI telemetry, dynamic themes, procedural audio, and automated deployment.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-Game%20Engine-green)](https://www.pygame.org/)
[![NumPy](https://img.shields.io/badge/NumPy-Numerical%20Computing-orange?logo=numpy)](https://numpy.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?logo=windows)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/License-Educational-lightblue)](#)

---

## 🧠 About the Project

**CONNECT4: Neural Arena** is an AI-powered implementation of the classic Connect4 board game, developed using **Python and Pygame**.

The project focuses on demonstrating how **Artificial Intelligence search algorithms** can be applied to a competitive two-player game. The AI analyzes possible future game states and selects strategic moves using **Minimax**, optimized with **Alpha-Beta Pruning** and supported by a **heuristic evaluation function**.

The project also goes beyond basic gameplay by providing real-time insight into the AI's decision-making process through an interactive telemetry system.

---
<img width="1025" height="601" alt="image" src="https://github.com/user-attachments/assets/0c22e1f5-9ecd-4ca8-9954-e9359d4c0a61" />
<img width="1017" height="595" alt="image" src="https://github.com/user-attachments/assets/4fb34b72-2ed4-4f1b-9caa-ed6ea03e5e32" />
<img width="1012" height="591" alt="image" src="https://github.com/user-attachments/assets/13839cf4-f561-4863-9d69-7b7f80b9ac1f" />


## ✨ Features

### 🎯 Multiple Game Modes

* **Human vs Human** — Play against another person.
* **Human vs AI** — Challenge the AI at different difficulty levels.
* **AI vs AI** — Watch two AI players compete against each other.

### 🤖 Artificial Intelligence

* Minimax game-tree search
* Alpha-Beta pruning optimization
* Heuristic board evaluation
* Configurable search depth
* Strategic center-column preference
* Offensive and defensive move evaluation
* AI move scoring

### 📊 Real-Time AI Telemetry

The Neural Arena provides an engine-style telemetry panel showing information such as:

* Search depth
* Nodes explored
* Nodes per second (NPS)
* Branches pruned
* Evaluation score
* Best move
* AI thinking status

This allows the player to see how much computation the AI is performing while making its decision.

### 💡 AI Hint System

In Human vs AI mode, players can request a hint.

The hint system performs an AI search on the current board and identifies a strategically optimal move.

### 📈 Live AI Visualization

The interface includes visual indicators inspired by chess-engine analysis:

* AI thinking indicator
* Evaluation bar
* Live performance information
* Search statistics

### 🎨 Dynamic Themes

The game supports multiple visual themes:

* 🌌 Space
* ⚡ Cyberpunk
* 💜 Neon
* 🕹️ Retro Arcade
* ◼️ Minimalist

Themes can be changed dynamically during the game.

### 📜 Match History

Previous games are stored using a JSON-based persistence system.

The history system records information such as:

* Game mode
* Winner
* Number of moves
* Match duration
* Previous game results

### 🔊 Procedural Audio

Instead of relying entirely on pre-recorded audio files, the project uses **NumPy-based waveform generation** to create parts of the game's audio experience.

The audio system can generate:

* Ambient background sounds
* Sine-wave tones
* Square-wave effects
* Atmospheric sound effects

### 🖥️ Responsive UI

The interface includes:

* Dynamic resolution scaling
* Fullscreen support
* Animated backgrounds
* Particle effects
* Glassmorphism-inspired panels
* Neon-style visual elements
* Animated game interactions

---

# 🧮 AI Architecture

The AI follows a game-tree search approach.

```text
                    Current Board
                         │
                         ▼
                  Generate Moves
                         │
                         ▼
                  Minimax Search
                         │
                         ▼
               Alpha-Beta Pruning
                         │
                         ▼
              Heuristic Evaluation
                         │
                         ▼
                 Best Move Selected
                         │
                         ▼
                   Update Board
```

---

## Minimax Algorithm

The **Minimax algorithm** is used as the fundamental decision-making technique.

It recursively explores possible future game states and assumes that both players will make optimal decisions.

The AI attempts to:

* Maximize its own score
* Minimize the opponent's score
* Select the move with the strongest expected outcome

---

## Alpha-Beta Pruning

Searching every possible game state can become computationally expensive.

**Alpha-Beta Pruning** improves Minimax by eliminating branches of the search tree that cannot influence the final decision.

This allows the AI to:

* Explore deeper positions
* Reduce unnecessary calculations
* Make decisions faster
* Improve overall performance

---

## Heuristic Evaluation

The AI cannot always search until the end of the game, especially at higher search depths.

Therefore, a heuristic evaluation function estimates the strength of a board position.

The evaluation considers factors such as:

* Center-column control
* Two-in-a-row formations
* Three-in-a-row formations
* Potential winning combinations
* Opponent threats
* Defensive opportunities
* Open-ended chains

This gives the AI a strategic understanding of positions that are not immediately winning or losing.

---

# 🎮 How Connect4 Works

The game uses the standard **6 × 7 Connect4 board**.

Players take turns dropping discs into columns.

The objective is to connect four discs:

```text
Horizontal
● ● ● ●

Vertical
●
●
●
●

Diagonal
●
  ●
    ●
      ●
```

The first player to create a sequence of four wins the game.

---

# 📊 Telemetry Explained

The telemetry panel provides insight into the AI's search process.

| Metric               | Description                                                  |
| -------------------- | ------------------------------------------------------------ |
| **Search Depth**     | Number of future moves explored by the AI                    |
| **Nodes Explored**   | Number of board states evaluated                             |
| **Nodes/sec**        | Speed at which the AI evaluates states                       |
| **Branches Pruned**  | Number of unnecessary branches removed by Alpha-Beta pruning |
| **Evaluation Score** | Estimated strategic advantage of the current position        |
| **Best Move**        | Move selected by the AI                                      |

This turns the game into more than a simple board game—it also acts as a small **AI search visualization system**.

---

# 🏗️ Project Structure

```text
CONNECT4/
│
├── ai.py                  # AI algorithms and decision-making
├── audio.py               # Procedural audio generation
├── board.py               # Connect4 board and game rules
├── config.py              # Game configuration and constants
├── history.py             # Match history and JSON persistence
├── main.py                # Main program and game loop
├── states.py              # Game-state management
├── ui.py                  # User interface and visual components
│
├── match_history.json     # Stored match history
├── requirements.txt       # Python dependencies
├── main.spec              # PyInstaller configuration
├── Neural Arena.spec      # Executable build configuration
│
└── .github/
    └── workflows/
        └── main.yml       # GitHub Actions deployment workflow
```

---

# 🔧 Technologies Used

| Technology         | Purpose                                    |
| ------------------ | ------------------------------------------ |
| **Python**         | Core programming language                  |
| **Pygame**         | Game engine, graphics and event handling   |
| **NumPy**          | Numerical computation and procedural audio |
| **JSON**           | Persistent match history                   |
| **PyInstaller**    | Windows executable packaging               |
| **GitHub Actions** | Automated build and release pipeline       |

---

# 🚀 Running the Project

## Requirements

Make sure Python 3.11+ is installed.

Install the dependencies:

```bash
pip install -r requirements.txt
```

Run the game:

```bash
python main.py
```

---

# 📦 Windows Executable

The project can also be distributed as a standalone Windows executable using **PyInstaller**.

Example build command:

```bash
pyinstaller --noconsole --onefile --clean --name "Neural Arena" main.py
```

The executable will be generated inside:

```text
dist/
```

---

# ⚙️ Automated Deployment

The project includes a **GitHub Actions CI/CD workflow**.

The workflow can:

1. Set up a Windows build environment
2. Install Python
3. Install project dependencies
4. Install PyInstaller
5. Build the executable
6. Upload the executable as an artifact
7. Create a GitHub Release when a version tag is used

This allows the project to be built and packaged without depending on the developer's local environment.

---

# 🎯 Learning Objectives

This project demonstrates practical applications of:

* Artificial Intelligence
* Adversarial search
* Minimax
* Alpha-Beta pruning
* Heuristic evaluation
* Recursion
* Game-tree exploration
* State management
* Data persistence
* Procedural audio generation
* UI/UX design
* Performance monitoring
* Software packaging
* CI/CD deployment

---

# 🔮 Future Improvements

Possible future enhancements include:

* 🌐 Online multiplayer
* 🏆 Global leaderboard
* 🧠 Reinforcement Learning-based AI
* 🌳 Monte Carlo Tree Search (MCTS)
* 🎥 Game replay system
* 📱 Mobile version
* ☁️ Cloud-based match statistics
* 🤝 Multiplayer matchmaking
* 📊 More advanced AI analytics

---

# 👨‍💻 Project

**CONNECT4: Neural Arena**

Developed as an Artificial Intelligence project demonstrating the practical implementation of game-playing AI algorithms using Python and Pygame.

### Core AI Techniques

**Minimax + Alpha-Beta Pruning + Heuristic Evaluation**

> *Think. Search. Predict. Connect.*

---
