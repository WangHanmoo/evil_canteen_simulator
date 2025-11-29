# Evil Canteen Simulator

A dark humor simulation game developed with Python and Pygame, exploring themes of moral dilemmas and institutional corruption through satirical gameplay.

## Project Overview

Evil Canteen Simulator is a single-player game where the player assumes the role of a school canteen manager facing daily ethical choices. The game employs black comedy to critique real-world food safety issues in institutional dining facilities.

### Inspiration

The concept for this game originated from personal experiences with my university's canteen:
- My roommate frequently suffered from stomach issues after eating canteen food
- I often noticed a distinct "freezer taste" in supposedly fresh dishes
- Social media posts from fellow students documented disturbing discoveries in their meals—hair strands, insect remains, and other foreign objects

These experiences inspired me to create a satirical game that transforms frustrating real-life situations into darkly humorous gameplay scenarios.

### Design Influences

The game draws mechanical inspiration from:
- Papers, Please — Moral decision-making under institutional pressure
- Mr.TomatoS — Unsettling character design and atmospheric horror elements

### Key Features

- 【Conscience System】: A visual heart-based indicator that transitions from red (virtuous) → gray (numb) → black (corrupted) based on player decisions
- 【Interactive Boss Character】: An animated "heartless boss" with real-time eye-tracking that follows the cursor, dynamic mood expressions, and satirical dialogue
- 【Multiple Endings】: Five distinct endings determined by the player's conscience level and accumulated wealth
- 【Archive System】: A collectible achievement system that tracks unlocked endings
- 【Event System】: Random events including health inspections, customer complaints, and supply chain issues

## Gameplay

### Game Flow

1. 【Title Screen】 → Start a new day or access the Archive to view unlocked endings
2. 【Preparation Phase】 → Make decisions about ingredient quality and food preparation methods
3. 【Business Phase】 → Handle daily operations and respond to random events
4. 【Ending Sequence】 → Receive one of five endings based on accumulated choices

### Decision Mechanics

Each choice affects two primary metrics:
- Conscience Value: Moral standing (0-100)
- Money: Financial resources

Negative choices (using expired ingredients, accepting bribes, etc.) increase money but decrease conscience. Positive choices maintain or restore conscience but often reduce profits.

## Endings

| Ending |      Title    | Trigger Condition |
|--------|---------------|-------------------|
| A | Termination of Business | Conscience drops to critical level (forced shutdown) |
| B | Late Repentance | Attempted moral recovery after significant wrongdoing |
| C | The Final Fall | Financial success achieved through complete moral corruption |
| D | The Art of Moderate Survival | Balanced approach between ethics and profit |
| E | The Collapse of Idealism | Maintained high conscience but suffered financial failure |

## Technical Implementation

### Architecture

The game is built as a single-file application (`main.py`, ~2,700 lines) using Pygame's game loop structure with state-based scene management.

```
evil_canteen_demo/
├── main.py                 # Core game logic and all scene implementations
├── requirements.txt        # Python dependencies
├── assets/
│   ├── fonts/              # Pixel art font (m6x11)
│   ├── sounds/             # Sound effects and background music
│   ├── images/             # Character and background assets
│   └── ui/                 # UI elements and icon generation scripts
├── states/                 # Scene template files (reserved for future modularization)
└── utils/                  # Utility modules
```

### Core Components

#### CanteenBoss Class
- Eye-tracking algorithm that calculates pupil position based on cursor coordinates
- Mood state machine with visual transitions (happy, angry, neutral, creepy)
- Dialogue system with 60+ satirical lines triggered by player actions
- Automatic idle chat system (5-second intervals)

#### Scene
- `TitleScene`: Main menu with animated boss character
- `ArchiveScene`: Ending collection display
- `PrepScene`: Ingredient selection and preparation choices
- `BusinessScene`: Main gameplay loop with random event system
- `EndingScene`: Narrative conclusion based on player performance

#### Sound
- Background music playback
- UI feedback sounds (click, select)
- Contextual sound effects (cash register for negative choices)

### Configuration

- **Window Resolution**: 1280 × 720 pixels
- **Frame Rate**: 60 FPS
- **Event Interval**: 8-15 seconds between random events
- **First Event Threshold**: Triggers after 4 player actions

## Installation and Execution

### Requirements
- Python 3.8+
- Pygame 2.0+

### Setup

```bash
# Clone or download the project
cd evil_canteen_demo

# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py
```

## Asset Credits

| Asset Type | Source | License |
|------------|--------|---------|
| Font | [m6x11](https://managore.itch.io/m6x11) by Daniel Linssen | Free for personal/commercial use |
| Sound Effects | [Freesound.org](https://freesound.org/) | CC0 / Attribution licenses |
| UI Graphics | Procedurally generated via Pygame | Original |

## Development Notes

### Design Philosophy

The game intentionally presents morally gray situations without clear "correct" answers, reflecting real-world ethical complexity. The boss character serves as both an antagonist and a dark mirror of the player's choices—his approval indicates moral compromise.

### Known Limitations

I acknowledge that the current numerical balancing requires further refinement. The relationship between game duration and value progression is not yet optimized, which may result in repetitive clicking during extended play sessions. I sincerely apologize if this affects your gameplay experience. Improving this balance system remains a priority for future development.

