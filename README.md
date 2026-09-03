# Kurtz AI Agents 🎖️

A three-part intelligent agents project — a logic-based knowledge agent, a Bayesian agent under uncertainty, and a Markov Decision Process solver — wrapped in an *Apocalypse Now*–themed game. Built as the final project for *Fundamentos de la Inteligencia Artificial* (Foundations of AI), second year of the Bachelor's Degree in Mathematical Engineering and Artificial Intelligence at ICAI – Universidad Pontificia Comillas.

Captain Willard must cross a palace grid to find Colonel Kurtz and then escape across a river, avoiding cliffs and a sleeping soldier along the way. The same scenario is solved with three different AI paradigms, one per stage of the game.

## The three agents

### 1. Logic-based agent — `src/kurtz_1.py`
A **Wumpus-World-style** knowledge agent with full information about percepts: adjacent cells reveal themselves through *brisa* (breeze → cliff nearby), *ronquido* (snoring → soldier nearby) and *resplandor* (glow → exit nearby). Two modes:
- **Interactive**: move with `W`/`A`/`S`/`D`, throw a grenade at a soldier with `G`, try to exit with `X`.
- **Automatic**: a **BFS** search plans a guaranteed-safe path from the start, through Kurtz, to the exit, using only cells proven safe by the percepts.

### 2. Bayesian agent — `src/palacio.py`
The same palace, but under **uncertainty**: instead of deterministic percepts, the agent maintains a belief distribution (`dicc_creencias`) over which cells are dangerous, updates it as it senses each percept, and either moves to the lowest-risk neighbor or runs a risk-thresholded BFS (only cells below a chosen danger probability `p` are considered safe to plan through).

### 3. Markov Decision Process — `src/river_mdp.py`
After escaping the palace, the agent must cross a river with columns of varying, randomly generated current strength. Transitions are **stochastic** (the current can sweep the agent sideways), so the optimal policy is computed with **value iteration** over the full state space, rather than searched for directly.

### Entry point — `src/kurtz.py`
A small menu that lets you choose between playing the logic-based version (Part 1) or the Bayesian version (Part 2); both continue into the river MDP (Part 3) once you escape the palace.

```bash
cd src
python kurtz.py
```

## Tech stack

Python, NumPy (for the logic-based agent's board math). Everything else — BFS, belief updates, value iteration — is implemented from scratch.

## Report

The full write-up — modeling decisions, belief-update formulas, and the value iteration derivation — is in [`docs/report.pdf`](docs/report.pdf).

## Author

- **Javier Arraiza Arribas** — [GitHub](https://github.com/javier13arraiza)

## License

This project is licensed under the [MIT License](LICENSE).
