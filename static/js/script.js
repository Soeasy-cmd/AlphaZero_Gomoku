const canvas = document.getElementById('board');
const ctx = canvas.getContext('2d');
const statusBar = document.getElementById('game-status');
const restartBtn = document.getElementById('restart-btn');
const modal = document.getElementById('modal');
const modalTitle = document.getElementById('modal-title');
const modalMessage = document.getElementById('modal-message');
const modalRestart = document.getElementById('modal-restart');

// Game constants matching the backend model
const BOARD_SIZE = 8;
const PADDING = 30; // 边距
// Calculate grid size dynamically
const BOARD_PIXEL_SIZE = 450;
const GRID_SIZE = (BOARD_PIXEL_SIZE - 2 * PADDING) / (BOARD_SIZE - 1);

let moves = []; // Store move history (0-63)
let isPlayerTurn = true;
let isGameOver = false;

// Initialize
function init() {
    // Reset state
    moves = [];
    isPlayerTurn = true;
    isGameOver = false;
    statusBar.textContent = "轮到你下棋 (黑棋)";
    modal.style.display = 'none';
    
    drawBoard();
}

function drawBoard() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw grid lines
    ctx.beginPath();
    ctx.strokeStyle = "#5d4037";
    ctx.lineWidth = 2;
    
    // Horizontal & Vertical lines
    for (let i = 0; i < BOARD_SIZE; i++) {
        // Horizontal
        ctx.moveTo(PADDING, PADDING + i * GRID_SIZE);
        ctx.lineTo(BOARD_PIXEL_SIZE - PADDING, PADDING + i * GRID_SIZE);
        
        // Vertical
        ctx.moveTo(PADDING + i * GRID_SIZE, PADDING);
        ctx.lineTo(PADDING + i * GRID_SIZE, BOARD_PIXEL_SIZE - PADDING);
    }
    ctx.stroke();

    // Draw pieces
    moves.forEach((move, index) => {
        const isBlack = (index % 2 === 0); // First move (index 0) is black
        drawPiece(move, isBlack, index === moves.length - 1);
    });
}

function drawPiece(move, isBlack, isLast) {
    const row = Math.floor(move / BOARD_SIZE);
    const col = move % BOARD_SIZE;
    
    const x = PADDING + col * GRID_SIZE;
    const y = PADDING + row * GRID_SIZE;
    
    ctx.beginPath();
    ctx.arc(x, y, GRID_SIZE * 0.4, 0, 2 * Math.PI);
    
    // Gradient for 3D effect
    const gradient = ctx.createRadialGradient(x - 5, y - 5, 2, x, y, GRID_SIZE * 0.4);
    if (isBlack) {
        gradient.addColorStop(0, "#666");
        gradient.addColorStop(1, "#000");
    } else {
        gradient.addColorStop(0, "#fff");
        gradient.addColorStop(1, "#ddd");
    }
    
    ctx.fillStyle = gradient;
    ctx.fill();
    
    // Shadow
    ctx.shadowColor = "rgba(0, 0, 0, 0.5)";
    ctx.shadowBlur = 4;
    ctx.shadowOffsetX = 2;
    ctx.shadowOffsetY = 2;
    
    // Marker for last move
    if (isLast) {
        ctx.beginPath();
        ctx.strokeStyle = isBlack ? "white" : "black";
        ctx.lineWidth = 2;
        ctx.moveTo(x - 5, y);
        ctx.lineTo(x + 5, y);
        ctx.moveTo(x, y - 5);
        ctx.lineTo(x, y + 5);
        ctx.stroke();
    }
    
    // Reset shadow
    ctx.shadowColor = "transparent";
}

function handleCanvasClick(event) {
    if (!isPlayerTurn || isGameOver) return;

    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    const x = (event.clientX - rect.left) * scaleX;
    const y = (event.clientY - rect.top) * scaleY;

    // Convert pixel to grid index
    // We want to find the nearest intersection
    let col = Math.round((x - PADDING) / GRID_SIZE);
    let row = Math.round((y - PADDING) / GRID_SIZE);

    // Check bounds
    if (col < 0 || col >= BOARD_SIZE || row < 0 || row >= BOARD_SIZE) return;

    // Check availability
    const move = row * BOARD_SIZE + col;
    if (moves.includes(move)) return;

    // Execute User Move
    moves.push(move);
    drawBoard();
    isPlayerTurn = false;
    statusBar.textContent = "AI 思考中...";

    // Send to server
    fetch('/api/move', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ moves: moves })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert("Error: " + data.error);
            return;
        }

        if (data.game_over) {
            handleGameOver(data.winner);
            return;
        }

        const aiMove = data.move;
        moves.push(aiMove);
        drawBoard();
        
        if (data.game_over) {
            handleGameOver(data.winner);
        } else {
            isPlayerTurn = true;
            statusBar.textContent = "轮到你下棋 (黑棋)";
        }
    })
    .catch(err => {
        console.error("Error:", err);
        statusBar.textContent = "连接错误，请重试";
        moves.pop(); // Revert valid move if server fails? Or keep it? Simpler to let user restart.
    });
}

function handleGameOver(winner) {
    isGameOver = true;
    let message = "";
    if (winner === -1) {
        message = "平局！";
    } else if (winner === 1) { // Assuming player starts first and is 1 ? Wait, server logic checks winner relative to players list
        // In this simple setup, let's just look at the last move made.
        // If computer made the last move and won, computer wins.
        // Actually, the server returns "winner".
        // In the game.py logic: self.players = [1, 2].
        // If player starts first (Black), players[0] is 1. AI is 2.
        // The backend `board.has_a_winner()` returns the winner player ID.
        // Since we force start_player=0 (Human) in backend, Human is 1, AI is 2.
        if (winner === 1) message = "恭喜你！你赢了！";
        else message = "遗憾，AI 赢了。";
    } else {
        // Fallback
         message = "游戏结束";
    }
    
    statusBar.textContent = message;
    
    modalTitle.textContent = "游戏结束";
    modalMessage.textContent = message;
    modal.style.display = 'flex';
}

canvas.addEventListener('click', handleCanvasClick);
restartBtn.addEventListener('click', init);
modalRestart.addEventListener('click', init);

// Start
init();
