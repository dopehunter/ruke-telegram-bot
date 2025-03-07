/**
 * Death Note Mini-App
 * Telegram Mini App Integration
 */

// Get Telegram Web App instance
const telegramApp = window.Telegram?.WebApp;

// Initialize Telegram Mini App
function initTelegramApp() {
    if (!telegramApp) {
        console.warn('Telegram Web App is not available. Running in standalone mode.');
        return false;
    }
    
    console.log('Telegram Web App initialized');
    
    // Set color theme
    document.documentElement.classList.add(telegramApp.colorScheme === 'dark' ? 'dark-theme' : 'light-theme');
    
    // Set up event listeners for Telegram UI elements
    setupTelegramAppEvents();
    
    // Notify telegram that the Mini App is ready
    telegramApp.ready();
    
    // Expand the Mini App to fullscreen
    telegramApp.expand();
    
    return true;
}

// Set up Telegram event listeners
function setupTelegramAppEvents() {
    if (!telegramApp) return;
    
    // Handle back button
    telegramApp.BackButton.onClick(() => {
        // Handle back button based on current screen
        const currentScreen = getCurrentScreen();
        
        switch (currentScreen) {
            case 'gameScreen':
                hideAllScreens();
                document.getElementById('menuScreen').classList.remove('hide');
                telegramApp.BackButton.hide();
                break;
            case 'rulesScreen':
                hideAllScreens();
                document.getElementById('menuScreen').classList.remove('hide');
                telegramApp.BackButton.hide();
                break;
            case 'resultsScreen':
                hideAllScreens();
                document.getElementById('menuScreen').classList.remove('hide');
                telegramApp.BackButton.hide();
                break;
            default:
                telegramApp.close();
        }
    });
    
    // Handle main button
    telegramApp.MainButton.onClick(() => {
        const currentScreen = getCurrentScreen();
        
        switch (currentScreen) {
            case 'menuScreen':
                startGame();
                break;
            case 'gameScreen':
                attemptSolve();
                break;
            case 'resultsScreen':
                shareResults();
                break;
            default:
                // Do nothing
        }
    });
}

// Get the current visible screen
function getCurrentScreen() {
    if (!document.getElementById('loading').classList.contains('hide')) {
        return 'loadingScreen';
    }
    if (!document.getElementById('menuScreen').classList.contains('hide')) {
        return 'menuScreen';
    }
    if (!document.getElementById('gameScreen').classList.contains('hide')) {
        return 'gameScreen';
    }
    if (!document.getElementById('rulesScreen').classList.contains('hide')) {
        return 'rulesScreen';
    }
    if (!document.getElementById('resultsScreen').classList.contains('hide')) {
        return 'resultsScreen';
    }
    
    return null;
}

// Update Telegram BackButton visibility
function updateBackButton() {
    if (!telegramApp) return;
    
    const currentScreen = getCurrentScreen();
    
    if (currentScreen === 'menuScreen' || currentScreen === 'loadingScreen') {
        telegramApp.BackButton.hide();
    } else {
        telegramApp.BackButton.show();
    }
}

// Update Telegram MainButton visibility and text
function updateMainButton(screen) {
    if (!telegramApp) return;
    
    switch (screen) {
        case 'menuScreen':
            telegramApp.MainButton.setText('START GAME');
            telegramApp.MainButton.show();
            break;
        case 'gameScreen':
            telegramApp.MainButton.setText('SOLVE CASE');
            telegramApp.MainButton.show();
            break;
        case 'resultsScreen':
            telegramApp.MainButton.setText('SHARE RESULTS');
            telegramApp.MainButton.show();
            break;
        default:
            telegramApp.MainButton.hide();
    }
}

// Share results with the Telegram chat
function shareTelegramResults(results) {
    if (!telegramApp) return;
    
    // Format the results
    const formattedResults = {
        action: 'share_game_results',
        case_id: gameState.currentCase?.id || 1,
        solved: results.solved,
        score: results.score,
        days_used: results.daysUsed,
        death_note_uses: results.deathNoteUses
    };
    
    // Send to the bot via Telegram Mini App
    telegramApp.sendData(JSON.stringify(formattedResults));
}

// Handle incoming data from the bot
function handleBotData(data) {
    try {
        const parsedData = JSON.parse(data);
        
        if (parsedData.action === 'start_game') {
            hideAllScreens();
            document.getElementById('menuScreen').classList.remove('hide');
            
            if (parsedData.case_id) {
                // Auto-start specific case
                startGame(parsedData.case_id);
            }
        }
        
    } catch (error) {
        console.error('Error parsing bot data:', error);
    }
}

// Check if running inside Telegram
function isTelegramApp() {
    return !!telegramApp;
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const isInTelegram = initTelegramApp();
    
    // Add additional class if running outside of Telegram
    if (!isInTelegram) {
        document.body.classList.add('standalone-mode');
    }
}); 