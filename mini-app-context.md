# Death Note Mini-App Game

## Concept Overview
A Telegram Mini-App game where players assume the role of Light Yagami from Death Note. The primary goal is to solve crimes and catch killers using the Death Note, demonstrating strategic thinking and moral judgment.

## Game Mechanics

### Core Gameplay
- **Crime Solving**: Players are presented with case files containing clues, evidence, and suspect lists
- **Deduction**: Players must analyze evidence to identify the true culprit
- **Death Note Usage**: Limited opportunities to write names in the Death Note (resource management)
- **Moral Choices**: Decisions affect the game's outcome and narrative path
- **Time Management**: Some actions consume in-game time, creating urgency

### Game Progression
1. **Level 1**: Simple cases with obvious culprits to introduce mechanics
2. **Level 2**: More complex cases requiring deeper analysis
3. **Level 3**: Cases with false leads and red herrings
4. **Level 4**: Cases intersecting with each other, requiring strategic thinking
5. **Final Challenge**: A case involving L or another major character from Death Note

### "Who is Kira?" Mini-Game
- Bot provides clues about Kira's identity based on Death Note lore
- Clues can be contextually related to recent conversations with the bot
- Players guess the identity from a list of characters
- Difficulty adjusts based on player performance

## Technical Implementation

### Frontend Components
- **Main Interface**: Crime board with cases, evidence, and Death Note
- **Case Files**: Interactive documents with images, text, and clues
- **Death Note Interface**: Digital recreation of the Death Note for name entry
- **Results Screen**: Displays outcomes of player decisions
- **Progress Tracker**: Shows solved cases and current level

### Backend Requirements
- **Game State Management**: Track player progress, decisions, and resources
- **Scoring System**: Calculate performance based on correct deductions and time
- **Bot Integration**: Allow the Telegram bot to launch the game and receive results
- **User Profile**: Save player progress for continuing games later

### Data Structure
- **Cases**: JSON objects containing crime details, evidence, and solutions
- **Suspects**: Character profiles with details, alibis, and guilt status
- **Player Actions**: Record of decisions and Death Note usage
- **Game Progress**: Current level, solved cases, and remaining resources

## User Experience Flow

1. **Introduction**: Ryuk introduces the game concept and basic rules
2. **Tutorial**: Guided walkthrough of the first simple case
3. **Main Gameplay**: Player progresses through increasingly difficult cases
4. **Intermissions**: Between cases, Ryuk provides commentary and hints
5. **Conclusion**: Game ending varies based on player performance and choices

## Integration with Ryuk Bot

- Bot can suggest playing the game during conversation lulls
- Game results can influence future conversations with Ryuk
- Ryuk can reference player's in-game decisions during chats
- Game can incorporate topics or themes from recent conversations
- Bot can provide exclusive hints for difficult cases based on chat history 