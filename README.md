# 🎮 CONNECT 4: Neural Arena

> A cinematic Connect 4 experience combining classical game-playing AI, real-time search telemetry, adaptive difficulty, and a fully interactive Pygame interface.

**Neural Arena** is a feature-rich Connect 4 game built in Python and Pygame. It goes beyond simply playing against an AI by exposing the decision-making process behind every move.

The project implements multiple AI search strategies, ranging from randomized play to iterative-deepening Alpha-Beta search with transposition tables, while providing live statistics such as nodes explored, branches pruned, search depth, evaluation time, and nodes per second.

---

## ✨ Features

### 🤖 Multi-Level AI

Five AI difficulty levels progressively increase the depth and sophistication of the search:

| Difficulty | Strategy | Search |
|------------|----------|--------|
| 🟢 Easy | Random / Shallow | Randomized moves |
| 🟡 Medium | Minimax | Depth 3 |
| 🟠 Hard | Alpha-Beta | Depth 5 |
| 🔴 Expert | Alpha-Beta + Move Ordering | Depth 6 |
| 🟣 Impossible | Iterative Deepening + Transposition Table | Up to Depth 7 |

The AI also introduces controlled move variation so that games do not always follow the exact same sequence when multiple moves have equivalent evaluations.

---

### 🧠 AI Search & Optimization

The AI engine demonstrates several fundamental game-playing techniques:

- **Minimax Search**
- **Alpha-Beta Pruning**
- **Iterative Deepening**
- **Transposition Tables**
- **Center-first Move Ordering**
- **Heuristic Board Evaluation**
- **Terminal-state detection**
- **Search-depth management**
- **Move selection with controlled randomness**

The Impossible difficulty reuses search information through a transposition table while progressively increasing the search depth.

---

### 📊 Real-Time AI Telemetry

One of the main goals of Neural Arena is to make the AI's decision-making visible.

During an AI turn, the interface can display:

- Algorithm being used
- Current search depth
- Nodes explored
- Branches pruned
- Evaluation time
- Nodes per second
- Best move score
- Current thinking column
- Live evaluation bar

This turns the game into more than a playable application — it also acts as a visual demonstration of how classical game-search algorithms work.

---

### 🎯 Multiple Game Modes

Neural Arena supports:

- 👤 **Human vs Human**
- 👤🤖 **Human vs AI**
- 🤖🤖 **AI vs AI**

AI-vs-AI mode is particularly useful for observing how different search strategies perform against each other.

---

### 🎨 Cinematic Interface

The game features a custom Pygame interface designed around a modern arcade/strategy aesthetic.

Features include:

- Cinematic intro
- Animated interface elements
- Responsive/resizable window
- Fullscreen mode
- Dynamic visual effects
- AI thinking indicators
- Evaluation visualization
- Game statistics
- Custom themes

### 🎨 Available Themes

- 🌌 Space
- 🟣 Cyberpunk
- 🟢 Neon
- 🕹️ Retro Arcade
- ⚪ Minimalist

---

### 🔊 Dynamic Audio

The project includes an integrated audio system with:

- Menu ambience
- Gameplay ambience
- Programmatically generated audio
- Audio transitions between game states

The project does not depend on external audio assets.

---

### 📜 Match History

Completed matches are automatically recorded in:

```text
match_history.json
