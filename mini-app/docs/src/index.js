/**
 * Death Note Mini-App
 * Main entry point
 */

// Initialize when DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize Telegram Mini App
    const telegramApp = window.Telegram?.WebApp;
    
    // Set up the app
    initApp();
    
    // Initialize the game
    initGame();
    
    // Show the game interface after a short loading delay
    setTimeout(() => {
        document.getElementById('loading').classList.add('hide');
        document.getElementById('menuScreen').classList.remove('hide');
        document.getElementById('menuScreen').classList.add('fade-in');
        
        // Get user info from Telegram if available
        if (telegramApp) {
            const user = telegramApp.initDataUnsafe?.user;
            if (user) {
                const userInfoElement = document.getElementById('userInfo');
                userInfoElement.textContent = `Player: ${user.first_name || 'Kira'}`;
            }
            
            // Set Telegram theme
            document.body.style.setProperty('--dn-black', telegramApp.themeParams.bg_color || '#0a0a0a');
            document.body.style.setProperty('--dn-white', telegramApp.themeParams.text_color || '#f0f0f0');
            
            // Expand the app to fullscreen
            telegramApp.expand();
            
            // Set main button for actions later
            telegramApp.MainButton.setParams({
                text: 'JOIN THE GAME',
                color: '#b20000',
                text_color: '#ffffff',
                is_visible: false
            });
        }
    }, 2000);
});

// Initialize app event listeners
function initApp() {
    // Menu buttons
    document.getElementById('startGameBtn').addEventListener('click', startGame);
    document.getElementById('rulesBtn').addEventListener('click', showRules);
    document.getElementById('backToChatBtn').addEventListener('click', backToChat);
    
    // Rules screen
    document.getElementById('backFromRulesBtn').addEventListener('click', backFromRules);
    
    // Game screen buttons
    document.getElementById('viewEvidenceBtn').addEventListener('click', viewEvidence);
    document.getElementById('viewSuspectsBtn').addEventListener('click', viewSuspects);
    document.getElementById('useDeathNoteBtn').addEventListener('click', toggleDeathNote);
    document.getElementById('solveBtn').addEventListener('click', attemptSolve);
    
    // Death Note actions
    document.getElementById('writeNameBtn').addEventListener('click', writeNameInDeathNote);
    
    // Results screen
    document.getElementById('nextCaseBtn').addEventListener('click', nextCase);
    document.getElementById('shareResultsBtn').addEventListener('click', shareResults);
    document.getElementById('returnToMenuBtn').addEventListener('click', returnToMenu);
}

// Show the rules screen
function showRules() {
    hideAllScreens();
    document.getElementById('rulesScreen').classList.remove('hide');
}

// Go back from rules to menu
function backFromRules() {
    hideAllScreens();
    document.getElementById('menuScreen').classList.remove('hide');
}

// Close the app and return to chat
function backToChat() {
    const telegramApp = window.Telegram?.WebApp;
    if (telegramApp) {
        telegramApp.close();
    }
}

// Start the game
function startGame() {
    hideAllScreens();
    document.getElementById('gameScreen').classList.remove('hide');
    loadCase(1); // Load the first case
}

// Hide all screens
function hideAllScreens() {
    const screens = document.querySelectorAll('.screen');
    screens.forEach(screen => {
        screen.classList.add('hide');
    });
}

// Toggle the Death Note panel
function toggleDeathNote() {
    const deathNotePanel = document.getElementById('deathNotePanel');
    if (deathNotePanel.classList.contains('hide')) {
        deathNotePanel.classList.remove('hide');
        document.getElementById('useDeathNoteBtn').textContent = 'Close Death Note';
    } else {
        deathNotePanel.classList.add('hide');
        document.getElementById('useDeathNoteBtn').textContent = 'Use Death Note';
    }
}

// Write a name in the Death Note
function writeNameInDeathNote() {
    const nameInput = document.getElementById('nameInput');
    const name = nameInput.value.trim();
    
    if (name) {
        // Add the name to the written names
        const writtenNames = document.getElementById('writtenNames');
        const nameEntry = document.createElement('p');
        nameEntry.textContent = name;
        writtenNames.appendChild(nameEntry);
        
        // Clear the input
        nameInput.value = '';
        
        // Update game state
        updateDeathNoteUses();
        
        // Check if this was the correct suspect
        checkDeathNoteTarget(name);
    }
}

// Update the Death Note uses counter
function updateDeathNoteUses() {
    // For now, just decrement the counter
    const usesElement = document.getElementById('noteUses');
    const currentUses = parseInt(usesElement.textContent.split(': ')[1]);
    if (currentUses > 0) {
        usesElement.textContent = `Death Note uses: ${currentUses - 1}`;
    }
    
    // Disable the Death Note if no uses left
    if (currentUses <= 1) {
        document.getElementById('writeNameBtn').disabled = true;
        document.getElementById('nameInput').disabled = true;
    }
}

// Go to the results screen after solving a case
function showResults(solved) {
    hideAllScreens();
    
    const resultsSummary = document.getElementById('resultsSummary');
    resultsSummary.innerHTML = '';
    
    if (solved) {
        const successMessage = document.createElement('h3');
        successMessage.textContent = 'Case Solved Successfully!';
        successMessage.style.color = '#4CAF50';
        resultsSummary.appendChild(successMessage);
        
        const detailsMessage = document.createElement('p');
        detailsMessage.textContent = 'You have eliminated the criminal and brought justice to the world.';
        resultsSummary.appendChild(detailsMessage);
    } else {
        const failureMessage = document.createElement('h3');
        failureMessage.textContent = 'Case Failed';
        failureMessage.style.color = '#b20000';
        resultsSummary.appendChild(failureMessage);
        
        const detailsMessage = document.createElement('p');
        detailsMessage.textContent = 'You failed to identify the true criminal or eliminated an innocent person.';
        resultsSummary.appendChild(detailsMessage);
    }
    
    document.getElementById('resultsScreen').classList.remove('hide');
}

// Go to the next case
function nextCase() {
    // For demo, just go back to menu
    returnToMenu();
}

// Share results with the Telegram chat
function shareResults() {
    const telegramApp = window.Telegram?.WebApp;
    if (telegramApp) {
        telegramApp.sendData(JSON.stringify({
            action: 'share_results',
            case_solved: true, // Replace with actual result
            case_id: 1 // Replace with actual case ID
        }));
    }
}

// Return to the main menu
function returnToMenu() {
    hideAllScreens();
    document.getElementById('menuScreen').classList.remove('hide');
} 