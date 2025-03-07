# Ryuk Telegram Bot Project

## Overview
This project implements a Telegram bot that personifies Ryuk, the death god (shinigami) from the anime/manga Death Note. The bot is designed to interact with users in a conversational manner, adopting Ryuk's personality traits and speech patterns.

## Core Components

### 1. Ryuk Conversational Bot
- Implemented on n8n platform
- Uses OpenRouter API with Google Gemini 2.0 Flash model
- Communicates in Russian with occasional German phrases
- Preserves chat history using Postgres database
- Features Ryuk's cynical, playful personality

### 2. Death Note Mini-Game
- Telegram Mini-App format
- Players take on the role of Light Yagami
- Gameplay involves solving crimes and catching killers using the Death Note
- Multiple levels with increasing difficulty
- Context-aware clues and challenges

## Technical Stack

### n8n Workflow
- Processes incoming Telegram messages
- Manages conversation state and user tracking
- Provides AI model integration
- Handles proactive messaging for user engagement

### Database (PostgreSQL)
- Stores conversation history
- Tracks user information and activity
- Maintains game progress and stats

### Telegram Bot API
- Handles message delivery
- Manages Mini-App launching
- Processes user commands

### Mini-App Framework
- HTML/CSS/JavaScript for frontend
- Backend API for game logic
- Integration with the Telegram Mini-App API

## User Experience

The bot interaction is designed to mimic Ryuk's character from Death Note, with:
- Cynical and sarcastic tone
- Occasional mentions of apples (but not overused)
- Philosophical musings about life and death
- Playful interactions and games
- Use of simple German phrases
- Engagement with topics popular among teenage users

The mini-game extends this experience by allowing users to immerse themselves in the Death Note universe as Light Yagami, making moral choices and strategic decisions. 