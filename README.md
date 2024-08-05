# Suika - A Physics-Based Puzzle Game

**Key Features:**
- **Physics Simulation:** Implemented realistic ball dynamics using Pymunk's physics engine, including collision detection and response.
- **Color Transition and Mechanics:** Designed a color transition system where balls 'evolve' through a series of colors and sizes upon merging.
- **Player Interaction:** Enabled player control for shooting balls and moving the character horizontally, as well as a cooldown mechanism to prevent spamming shots.
- **Visuals:** Integrated color-coded balls, background graphics, and a scoring system.
- **Gameplay Mechanics:** Managed game state, ball creation, merging logic, scoring, as well as a general challenge.

**Technologies:**
- **Pygame:** Game development and graphics rendering.
- **Pymunk:** Physics logic and collision handling.
- **Python:** Core programming language and handles game logic and functionality.

**Demo:**
- Watch the demo video here: [Suika Demo](https://www.youtube.com/watch?v=go4F76_QFy0)

# Installation Guide

To set up and run the Suika game on your local machine, follow these steps:

## Prerequisites

1. **Python**: Ensure you have Python installed on your system. You can download it from the [official Python website](https://www.python.org/downloads/).

2. **Pygame** and **Pymunk**: You will need to install these Python libraries to run the game.

## Installation Steps

### 1. Install Python

1. Download the Python installer from the [Python Downloads](https://www.python.org/downloads/) page.
2. Run the installer and follow the installation prompts.
3. Make sure to check the box that says **Add Python to PATH** during the installation.

### 2. Install Pygame and Pymunk

1. Open a Command Prompt (Windows) or Terminal (macOS/Linux).

2. Install Pygame and Pymunk using pip by running the following commands:

    ```bash
    pip install pygame pymunk
    ```

### 3. Clone the Repository

1. If you haven’t already, clone the repository containing the Suika game:

    ```bash
    git clone https://github.com/bgar324/suika
    ```

2. Navigate to the project directory:

    ```bash
    cd suika
    ```

### 4. Run the Game

1. Ensure you are in the project directory.
2. Run the game script:

    ```bash
    python suika2.py
    ```

    Make sure `suika2.py` is the correct name of your game file.

## Troubleshooting

- **Issue: Python not found**: Ensure Python is added to your system's PATH. You can verify this by running `python --version` in the Command Prompt or Terminal.
- **Issue: pip not found**: Ensure pip is installed and added to your PATH. If not, you may need to install it or use `python -m ensurepip` to install it.

Feel free to reach out if you encounter any issues or have questions about the setup.
