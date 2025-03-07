# Integrating Death Note Mini-App with n8n Workflow

This guide explains how to update your n8n workflow to add support for the Death Note mini-app.

## Overview

We'll modify the Ryuk n8n workflow to:
1. Add a command handler for `/play`
2. Create a response with a mini-app launch button
3. Enhance Ryuk's AI prompt to occasionally suggest the game

## Steps to Update n8n Workflow

### Step 1: Log into n8n

1. Access your n8n instance where your Ryuk bot workflow is deployed
2. Locate and edit your "Ryuk test" workflow

### Step 2: Add a Command Handler for /play

1. Add a new branch to your workflow starting from the Telegram Trigger node
2. Add a new "IF" node to check for the `/play` command:
   - Set condition to: `{{$node["Telegram Trigger"].json["message"]["text"].startsWith("/play")}}`

### Step 3: Create the Mini-App Launch Response

1. After the IF node (on the "true" branch), add a new "Telegram" node
2. Configure the node with these settings:
   - **Operation**: Send Message
   - **Chat ID**: `{{$node["Telegram Trigger"].json["message"]["chat"]["id"]}}`
   - **Text**: 
     ```
     Хе-хе-хе... Хочешь примерить роль Лайта Ягами? В этой игре ты сможешь раскрывать преступления и вершить правосудие с помощью Тетради Смерти.
     ```
   - **Parse Mode**: Markdown
   - **Reply Markup**: JSON, with this content:
     ```json
     {
       "inline_keyboard": [
         [
           {
             "text": "Запустить игру Death Note",
             "web_app": {
               "url": "https://yourusername.github.io/death-note-mini-app/"
             }
           }
         ]
       ]
     }
     ```
   - Make sure to replace the URL with your actual mini-app URL

3. Add a second "Telegram" node connected to the first one to send additional information:
   - **Operation**: Send Message
   - **Chat ID**: `{{$node["Telegram Trigger"].json["message"]["chat"]["id"]}}`
   - **Text**:
     ```
     В игре тебе предстоит:
     • Анализировать улики и выявлять подозреваемых
     • Использовать Тетрадь Смерти, чтобы устранять преступников
     • Принимать сложные моральные решения
     • Раскрыть все дела до истечения времени
     
     Я буду наблюдать за твоими решениями... *хехехе*
     ```
   - **Parse Mode**: Markdown

### Step 4: Update the AI Agent Prompt

1. Locate your "AI Agent" node in the workflow
2. Edit the prompt to include mentions of the Death Note game:
   - Add the following to the system message:
     ```
     Ты создал мини-игру для Telegram, в которой люди могут играть роль Лайта Ягами и ловить преступников с помощью Тетради Смерти. Время от времени предлагай сыграть в эту игру, используя команду /play.
     ```
3. This will prompt Ryuk to occasionally suggest the game during conversations

### Step 5: Create a Workflow for Game Results (Optional)

If you want your mini-app to send results back to the bot:

1. Create a separate webhook endpoint in n8n for receiving game results
2. Use the Telegram sendData API in the mini-app to send results to this webhook
3. Process the results and have Ryuk respond accordingly

### Step 6: Save and Deploy

1. Save your workflow
2. Test the integration by sending the `/play` command to your bot
3. Click the game launch button to verify it opens your mini-app

## Example Diagram

```
┌───────────────┐
│               │
│  Telegram     │
│  Trigger      │
│               │
└───────┬───────┘
        │
┌───────▼───────┐     ┌───────────────┐
│               │     │               │
│  IF           │─Yes─►  Telegram     │
│  /play?       │     │  Send Button  │
│               │     │               │
└───────┬───────┘     └───────┬───────┘
        │                     │
        │No                   │
        │             ┌───────▼───────┐
┌───────▼───────┐     │               │
│               │     │  Telegram     │
│  Continue     │     │  Send Info    │
│  Regular Flow │     │               │
│               │     └───────────────┘
└───────────────┘
```

## Troubleshooting

- If the button doesn't appear, check your JSON formatting in the Reply Markup field
- If the mini-app doesn't load, verify the URL is correct and publicly accessible
- If Ryuk doesn't suggest the game, make sure you've updated the AI Agent prompt correctly

## After Integration

Once integrated, your n8n workflow will:
1. Respond to the `/play` command with a button to launch the mini-app
2. Have Ryuk occasionally suggest the game to users
3. Process game results if you implemented the optional webhook 