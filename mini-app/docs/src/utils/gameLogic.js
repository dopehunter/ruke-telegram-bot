/**
 * Death Note Mini-App
 * Game Logic Module
 */

// Game state
let gameState = {
    currentCase: null,
    casesSolved: 0,
    daysLeft: 5,
    deathNoteUses: 3,
    suspects: [],
    evidence: [],
    killedSuspects: []
};

// Case database
const cases = [
    {
        id: 1,
        title: "Case #1: The Serial Killer",
        description: "A series of murders has occurred in Tokyo. All victims died of heart attacks, but they were all criminals who had escaped justice. The police are baffled.",
        days: 5,
        deathNoteUses: 3,
        culprit: "Higuchi Kyosuke",
        evidence: [
            {
                id: "e1",
                title: "Crime Scene Photos",
                description: "Photos showing victims died clutching their chests. No signs of struggle or forced entry."
            },
            {
                id: "e2",
                title: "Victim List",
                description: "All victims were criminals who had escaped prosecution or received light sentences."
            },
            {
                id: "e3",
                title: "Surveillance Footage",
                description: "One victim was caught on camera dying suddenly at a cafe. A businessman in a suit was watching from across the street."
            }
        ],
        suspects: [
            {
                id: "s1",
                name: "Higuchi Kyosuke",
                description: "A businessman who works at Yotsuba Group. Has expressed extreme views about justice on social media.",
                isGuilty: true,
                clues: ["Was seen near the location of the third murder.", "Has access to criminal records through company database.", "Recent promotion coincided with start of killings."]
            },
            {
                id: "s2",
                name: "Misa Amane",
                description: "A popular model whose parents were murdered. The killer was never brought to justice.",
                isGuilty: false,
                clues: ["Publicly supports the mysterious killings.", "Has an alibi for two of the murder times.", "Shows no signs of the calculated planning evident in the crimes."]
            },
            {
                id: "s3",
                name: "Teru Mikami",
                description: "A prosecutor who has lost several high-profile cases against obvious criminals.",
                isGuilty: false,
                clues: ["Was out of the country during two of the killings.", "Has expressed frustration with the justice system.", "Works within legal channels despite his frustration."]
            }
        ]
    },
    {
        id: 2,
        title: "Case #2: The Corporate Conspiracy",
        description: "CEOs of competing companies are dying in mysterious accidents. All companies are now being acquired by Yotsuba Group.",
        days: 6,
        deathNoteUses: 2,
        culprit: "Reiji Namikawa",
        evidence: [
            {
                id: "e1",
                title: "Financial Records",
                description: "Yotsuba Group's stock rises after each CEO's death."
            },
            {
                id: "e2",
                title: "Meeting Minutes",
                description: "Secret meetings held by Yotsuba executives discussing 'removing obstacles'."
            },
            {
                id: "e3",
                title: "Accident Reports",
                description: "All deaths appeared to be accidents but occurred in statistically improbable ways."
            }
        ],
        suspects: [
            {
                id: "s1",
                name: "Reiji Namikawa",
                description: "Yotsuba's Director of Sales. Known for his ruthless business tactics.",
                isGuilty: true,
                clues: ["Was present at all meetings where 'obstacles' were discussed.", "Received largest bonus after acquisitions.", "Has personal grudges against two of the deceased CEOs."]
            },
            {
                id: "s2",
                name: "Shingo Mido",
                description: "Yotsuba's Marketing Director. Stands to gain from company expansion.",
                isGuilty: false,
                clues: ["Opposed aggressive acquisition strategies in private emails.", "Was on vacation during two deaths.", "Has family connections to one of the victim's companies."]
            },
            {
                id: "s3",
                name: "Suguru Shimura",
                description: "Yotsuba's Personnel Director. Has access to all company information.",
                isGuilty: false,
                clues: ["No direct benefit from the acquisitions.", "Expressed ethical concerns in private communications.", "Had alibis for three of the deaths."]
            }
        ]
    }
];

// Initialize the game
function initGame() {
    // Reset game state
    gameState = {
        currentCase: null,
        casesSolved: 0,
        daysLeft: 5,
        deathNoteUses: 3,
        suspects: [],
        evidence: [],
        killedSuspects: []
    };
    
    console.log("Game initialized");
}

// Load a specific case
function loadCase(caseId) {
    // Find the case
    const caseData = cases.find(c => c.id === caseId);
    
    if (!caseData) {
        console.error(`Case ${caseId} not found`);
        return;
    }
    
    // Update game state
    gameState.currentCase = caseData;
    gameState.daysLeft = caseData.days;
    gameState.deathNoteUses = caseData.deathNoteUses;
    gameState.suspects = caseData.suspects;
    gameState.evidence = caseData.evidence;
    gameState.killedSuspects = [];
    
    // Update UI
    document.getElementById('caseTitle').textContent = caseData.title;
    document.getElementById('daysLeft').textContent = `Days left: ${caseData.days}`;
    document.getElementById('noteUses').textContent = `Death Note uses: ${caseData.deathNoteUses}`;
    
    // Load the case board
    loadCaseBoard(caseData);
    
    console.log(`Case ${caseId} loaded:`, caseData);
}

// Load the case board with case description
function loadCaseBoard(caseData) {
    const caseBoard = document.getElementById('caseBoard');
    caseBoard.innerHTML = '';
    
    // Case description
    const description = document.createElement('div');
    description.className = 'case-description';
    description.innerHTML = `
        <h3>Case Brief</h3>
        <p>${caseData.description}</p>
        <div class="case-instructions">
            <p>As Light Yagami, your goal is to:</p>
            <ol>
                <li>Review the evidence carefully</li>
                <li>Identify the culprit among the suspects</li>
                <li>Use the Death Note to eliminate the culprit</li>
                <li>Solve the case within the time limit</li>
            </ol>
        </div>
    `;
    caseBoard.appendChild(description);
}

// View evidence for the current case
function viewEvidence() {
    if (!gameState.currentCase) return;
    
    const caseBoard = document.getElementById('caseBoard');
    caseBoard.innerHTML = '';
    
    // Create evidence header
    const header = document.createElement('h3');
    header.textContent = 'Evidence';
    caseBoard.appendChild(header);
    
    // Create evidence list
    const evidenceList = document.createElement('div');
    evidenceList.className = 'evidence-list';
    
    gameState.currentCase.evidence.forEach(item => {
        const evidenceItem = document.createElement('div');
        evidenceItem.className = 'evidence-item';
        evidenceItem.innerHTML = `
            <h4>${item.title}</h4>
            <p>${item.description}</p>
        `;
        evidenceList.appendChild(evidenceItem);
    });
    
    caseBoard.appendChild(evidenceList);
    
    // Add back button
    const backButton = document.createElement('button');
    backButton.className = 'secondary-button';
    backButton.textContent = 'Back to Case';
    backButton.addEventListener('click', () => loadCaseBoard(gameState.currentCase));
    caseBoard.appendChild(backButton);
    
    // Consume a day
    consumeDay();
}

// View suspects for the current case
function viewSuspects() {
    if (!gameState.currentCase) return;
    
    const caseBoard = document.getElementById('caseBoard');
    caseBoard.innerHTML = '';
    
    // Create suspects header
    const header = document.createElement('h3');
    header.textContent = 'Suspects';
    caseBoard.appendChild(header);
    
    // Create suspects list
    const suspectsList = document.createElement('div');
    suspectsList.className = 'suspects-list';
    
    gameState.currentCase.suspects.forEach(suspect => {
        // Check if the suspect is already killed
        const isKilled = gameState.killedSuspects.includes(suspect.name);
        
        const suspectItem = document.createElement('div');
        suspectItem.className = `suspect-item ${isKilled ? 'killed' : ''}`;
        
        let cluesHtml = '';
        if (!isKilled) {
            cluesHtml = `
                <div class="suspect-clues">
                    <h5>Clues:</h5>
                    <ul>
                        ${suspect.clues.map(clue => `<li>${clue}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        suspectItem.innerHTML = `
            <h4>${suspect.name} ${isKilled ? '(Deceased)' : ''}</h4>
            <p>${suspect.description}</p>
            ${cluesHtml}
        `;
        suspectsList.appendChild(suspectItem);
    });
    
    caseBoard.appendChild(suspectsList);
    
    // Add back button
    const backButton = document.createElement('button');
    backButton.className = 'secondary-button';
    backButton.textContent = 'Back to Case';
    backButton.addEventListener('click', () => loadCaseBoard(gameState.currentCase));
    caseBoard.appendChild(backButton);
    
    // Consume a day
    consumeDay();
}

// Attempt to solve the case
function attemptSolve() {
    if (!gameState.currentCase) return;
    
    const caseBoard = document.getElementById('caseBoard');
    caseBoard.innerHTML = '';
    
    // Create solve header
    const header = document.createElement('h3');
    header.textContent = 'Solve the Case';
    caseBoard.appendChild(header);
    
    // Create solve form
    const solveForm = document.createElement('div');
    solveForm.className = 'solve-form';
    solveForm.innerHTML = `
        <p>Who do you believe is the culprit behind these crimes?</p>
        <div class="suspect-options">
            ${gameState.currentCase.suspects.map(suspect => `
                <div class="suspect-option">
                    <input type="radio" id="suspect-${suspect.id}" name="culprit" value="${suspect.name}" ${gameState.killedSuspects.includes(suspect.name) ? 'disabled' : ''}>
                    <label for="suspect-${suspect.id}">${suspect.name} ${gameState.killedSuspects.includes(suspect.name) ? '(Deceased)' : ''}</label>
                </div>
            `).join('')}
        </div>
        <button id="submitSolution" class="main-button">Submit Solution</button>
    `;
    caseBoard.appendChild(solveForm);
    
    // Add back button
    const backButton = document.createElement('button');
    backButton.className = 'secondary-button';
    backButton.textContent = 'Cancel';
    backButton.addEventListener('click', () => loadCaseBoard(gameState.currentCase));
    caseBoard.appendChild(backButton);
    
    // Add event listener for the submit button
    document.getElementById('submitSolution').addEventListener('click', () => {
        const selectedCulprit = document.querySelector('input[name="culprit"]:checked')?.value;
        
        if (!selectedCulprit) {
            alert('Please select a suspect');
            return;
        }
        
        // Check if the selected culprit is correct
        const isCorrect = selectedCulprit === gameState.currentCase.culprit;
        
        // Check if the culprit is dead
        const isCulpritKilled = gameState.killedSuspects.includes(gameState.currentCase.culprit);
        
        // Determine if the case is solved
        const isSolved = isCorrect && isCulpritKilled;
        
        // Show results
        showResults(isSolved);
        
        // Update game state
        if (isSolved) {
            gameState.casesSolved++;
        }
    });
}

// Check if a name written in the Death Note matches a suspect
function checkDeathNoteTarget(name) {
    if (!gameState.currentCase) return;
    
    // Find the suspect
    const suspect = gameState.currentCase.suspects.find(s => 
        s.name.toLowerCase() === name.toLowerCase()
    );
    
    if (suspect) {
        // Mark as killed
        gameState.killedSuspects.push(suspect.name);
        
        // Show notification
        const notification = document.createElement('div');
        notification.className = 'death-note-notification';
        notification.textContent = `${suspect.name} has died of a heart attack.`;
        document.body.appendChild(notification);
        
        // Remove notification after a few seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
        
        // If innocent person killed, penalize
        if (!suspect.isGuilty) {
            consumeDay(2); // Penalty: lose 2 days
        }
    }
}

// Consume days and check for game over
function consumeDay(days = 1) {
    if (!gameState.currentCase) return;
    
    // Update days left
    gameState.daysLeft -= days;
    document.getElementById('daysLeft').textContent = `Days left: ${gameState.daysLeft}`;
    
    // Check for game over
    if (gameState.daysLeft <= 0) {
        // Time's up!
        showResults(false);
    }
} 