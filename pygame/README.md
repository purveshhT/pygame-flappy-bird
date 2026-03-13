# Flapp Bird 🐦

A complete 2D side-scrolling game inspired by Flappy Bird, built with Python and Pygame. Features unique mouse-cursor-based controls and power-ups!

## 🎮 Game Features

### Controls
- **Spacebar**: Quick flap (small jump)
- **Click**: Quick flap (small jump)
- **Hold**: Charge a stronger flap (higher jump)
- **Drag and Release**: Slingshot motion (directional impulse)
- **Click on Bird**: Power boost when hovering over the bird

### Gameplay
- Endless side-scrolling gameplay
- Avoid pipes to score points
- Difficulty increases every 10 points (faster pipes, smaller gaps)
- Power-ups spawn occasionally for enhanced gameplay

### Power-ups
- **Shield** (Blue): Protects from one collision
- **Slow Motion** (Yellow): Reduces gravity and pipe speed
- **Magnet** (Red): Attracts nearby power-ups

### Visual Features
- Custom cursor with trail effects
- Animated bird sprite with 3-frame wing flapping
- Charge bar when holding mouse
- Slingshot line when dragging
- Beautiful sky gradient background
- Power-up indicators in HUD

### Audio
- Flap sound effects
- Score sound when passing pipes
- Game over sound
- Power-up collection sound

## 🚀 How to Run

1. **Install Dependencies**:
   ```bash
   pip install pygame numpy
   ```

2. **Run the Game**:
   ```bash
   python main.py
   ```

3. **Generate Assets** (if needed):
   ```bash
   python create_assets.py
   python create_sounds.py
   ```

## 📁 Project Structure

```
pygame/
├── main.py              # Main game file
├── create_assets.py     # Asset generation script
├── create_sounds.py     # Sound effect generation script
├── assets/              # Game assets
│   ├── cursor.png       # Custom cursor sprite
│   ├── bird_0.png       # Bird animation frame 1
│   ├── bird_1.png       # Bird animation frame 2
│   ├── bird_2.png       # Bird animation frame 3
│   ├── pipe.png         # Pipe sprite
│   ├── background.png   # Background image
│   ├── flap.wav         # Flap sound effect
│   ├── score.wav        # Score sound effect
│   ├── game_over.wav    # Game over sound
│   └── power_up.wav     # Power-up sound
├── best_score.json      # Best score storage
└── README.md           # This file
```

## 🎯 Game Mechanics

### Physics
- Gravity affects the bird continuously
- Flapping provides upward velocity
- Slingshot adds directional momentum
- Air resistance gradually slows horizontal movement

### Scoring
- +1 point for each pipe pair passed
- Best score is automatically saved
- Score persists between game sessions

### Difficulty Scaling
- Every 10 points: pipe speed increases by 0.5
- Every 10 points: gap height decreases by 10 (minimum 100)
- Power-ups spawn every 10 seconds with 10% chance

### Collision Detection
- Precise collision with pipe boundaries
- Shield power-up provides one-time protection
- Game over on collision or screen boundaries

## 🎨 Customization

The game is designed to be easily customizable:

- **Colors**: Modify color constants at the top of `main.py`
- **Physics**: Adjust gravity, jump strength, and air resistance
- **Difficulty**: Change pipe spawn rates and speed increments
- **Power-ups**: Modify duration and spawn rates
- **Assets**: Replace sprite files in the `assets/` folder

## 🛠️ Technical Details

- **Resolution**: 288×512 pixels (classic mobile game size)
- **Frame Rate**: 60 FPS
- **Engine**: Pygame 2.6.1+
- **Python**: 3.7+
- **Dependencies**: pygame, numpy

## 🎵 Sound System

The game includes procedurally generated sound effects:
- **Flap**: Short chirp sound
- **Score**: Upward ascending tones
- **Game Over**: Downward descending tones
- **Power-up**: Magical chime sequence

## 🏆 High Scores

Your best score is automatically saved to `best_score.json` and will persist between game sessions.

## 🎮 Controls Summary

| Action | Effect |
|--------|--------|
| Spacebar | Small upward flap |
| Quick Click | Small upward flap |
| Hold & Release | Charged flap (stronger) |
| Drag & Release | Slingshot in direction |
| Click on Bird | Power boost |
| Click "Play" | Start game |
| Click "Restart" | Restart after game over |

Enjoy playing Flapp Bird! 🐦✨
