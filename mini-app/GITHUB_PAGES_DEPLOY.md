# Deploying Death Note Mini-App to GitHub Pages

This guide provides step-by-step instructions for deploying the Death Note Mini-App to GitHub Pages and integrating it with your Telegram bot.

## Step 1: Set Up a GitHub Repository

1. Create a new GitHub repository (or use an existing one)
   - Go to [GitHub](https://github.com/) and click the "+" icon in the top right
   - Select "New repository"
   - Name it `death-note-mini-app` (or another name of your choice)
   - Make it public (required for GitHub Pages on free accounts)
   - Initialize with a README
   - Click "Create repository"

2. Clone the repository to your local machine:
   ```bash
   git clone https://github.com/yourusername/death-note-mini-app.git
   cd death-note-mini-app
   ```

3. Copy your mini-app files to the repository:
   ```bash
   # Copy the entire mini-app folder
   cp -r /path/to/mini-app/* ./
   ```

## Step 2: Adjust File Paths for GitHub Pages

GitHub Pages requires all paths to be relative to the repository root. We need to modify the paths in our HTML and CSS files:

1. Update `index.html` paths:
   ```html
   <!-- Change from -->
   <link rel="stylesheet" href="../src/styles/main.css">
   <img src="../src/assets/images/death_note_cover.jpg" alt="Death Note" class="loading-image" id="loadingImage">
   
   <!-- To -->
   <link rel="stylesheet" href="./src/styles/main.css">
   <img src="./src/assets/images/death_note_cover.jpg" alt="Death Note" class="loading-image" id="loadingImage">
   
   <!-- Script paths as well -->
   <script src="./src/utils/telegramApp.js"></script>
   <script src="./src/utils/gameLogic.js"></script>
   <script src="./src/index.js"></script>
   ```

2. Update `main.css` paths:
   ```css
   /* Change from */
   background-image: url('../assets/images/death_note_bg.jpg');
   
   /* To */
   background-image: url('../assets/images/death_note_bg.jpg');
   /* This path should work as-is because it's relative to the CSS file */
   ```

## Step 3: Configure for GitHub Pages

1. Create a `.nojekyll` file in the root directory to bypass Jekyll processing:
   ```bash
   touch .nojekyll
   ```

2. Move `index.html` to the root directory if it's not already there:
   ```bash
   # If index.html is in public/
   mv public/index.html ./
   ```

## Step 4: Commit and Push to GitHub

1. Add all files to Git:
   ```bash
   git add .
   ```

2. Commit the changes:
   ```bash
   git commit -m "Add Death Note mini-app files"
   ```

3. Push to GitHub:
   ```bash
   git push origin main
   ```

## Step 5: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click "Settings" tab
3. Scroll down to "GitHub Pages" section
4. Under "Source", select "main" branch
5. Click "Save"
6. Wait a few minutes for your site to deploy
7. GitHub will provide you with a URL (typically `https://yourusername.github.io/death-note-mini-app/`)

## Step 6: Register Your Mini-App with BotFather

1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send the `/newapp` command
3. Select your bot
4. Provide a title: "Death Note: Justice Awaits"
5. Provide a short description: "Play as Light Yagami and catch criminals using the Death Note"
6. Upload a photo (optional - you can use one of your Death Note images)
7. Provide the GitHub Pages URL to your mini-app
8. BotFather will confirm and provide your mini-app link

## Step 7: Update Your Bot Code

1. In `simple_ruke_bot.py`, update the placeholder URL in the `handle_play_command` function:

   ```python
   # Replace with your actual GitHub Pages URL
   mini_app_url = "https://yourusername.github.io/death-note-mini-app/"
   ```

## Step 8: Test Everything

1. Start your bot (`python simple_ruke_bot.py`)
2. Send the `/play` command to your bot in Telegram
3. Click the "Запустить игру Death Note" button
4. The mini-app should open within Telegram

## Troubleshooting

- **404 errors**: Make sure all file paths are correct and the `.nojekyll` file exists
- **Blank page**: Check browser console for JavaScript errors
- **Images not loading**: Verify image paths are correct and files are in the right location
- **CSS not applied**: Ensure CSS paths are correctly referenced

## Updating Your Mini-App

When you make changes to your mini-app:

1. Make your changes locally
2. Test them thoroughly
3. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update mini-app with new features"
   git push origin main
   ```
4. GitHub Pages will automatically update within a few minutes 