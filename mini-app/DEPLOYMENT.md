# Deployment Guide for Death Note Mini-App

This guide provides instructions for deploying the Death Note Mini-App and integrating it with your Telegram bot.

## Step 1: Host the Mini-App

You have several options for hosting the mini-app:

### Option 1: GitHub Pages (Free)

1. Push your mini-app to a GitHub repository
2. Go to repository Settings → Pages
3. Set source to main branch and the `/docs` folder
4. Before pushing, build your app and copy all files to the `/docs` folder:
   ```
   npm run build
   mkdir -p docs
   cp -r dist/* docs/
   ```
5. Your mini-app will be available at `https://yourusername.github.io/your-repo-name/`

### Option 2: Netlify, Vercel, or Render (Free Tiers)

1. Create an account on [Netlify](https://www.netlify.com/), [Vercel](https://vercel.com/), or [Render](https://render.com/)
2. Connect your GitHub repository
3. Configure the build settings (typically detected automatically)
4. Deploy your site
5. Your mini-app will be available at the provided URL

### Option 3: Manual Hosting

If you have your own web server:

1. Build the mini-app: `npm run build`
2. Upload all files from the `dist` folder to your web server
3. Configure your web server to serve static files
4. Ensure HTTPS is enabled (required by Telegram)

## Step 2: Register Your Mini-App with BotFather

1. Open Telegram and find [@BotFather](https://t.me/BotFather)
2. Send the `/newapp` command
3. Select your bot
4. Provide a title: "Death Note: Justice Awaits"
5. Provide a short description: "Play as Light Yagami and catch criminals using the Death Note"
6. Upload a photo (optional)
7. Provide the URL to your hosted mini-app
8. Wait for BotFather to confirm and provide your mini-app link

## Step 3: Update Your Bot Code

1. In `simple_ruke_bot.py`, replace the placeholder URL in the `handle_play_command` function:

   ```python
   # Replace this URL with your actual deployed mini-app URL from BotFather
   mini_app_url = "https://example.com/death-note-game"
   ```

2. Replace with your actual mini-app URL from BotFather

## Step 4: Optionally Add a Menu Button

You can also add a permanent menu button to your bot:

1. Open Telegram and find [@BotFather](https://t.me/BotFather)
2. Send the `/mybots` command
3. Select your bot
4. Go to "Bot Settings" → "Menu Button"
5. Set a menu button with the text "Play Death Note Game" and the URL to your mini-app

## Step 5: Test Your Integration

1. Start your bot: `python simple_ruke_bot.py`
2. Open Telegram and send the `/play` command to your bot
3. Click the "Launch Death Note Game" button
4. The mini-app should open within Telegram

## Troubleshooting

- **Mini-app doesn't open**: Ensure your URL is accessible and uses HTTPS
- **Images don't load**: Check the paths in HTML and CSS files
- **Telegram Web App API errors**: Make sure you're using the latest Telegram Web App JS file
- **Game doesn't work properly**: Check browser console for JavaScript errors 