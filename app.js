const boardEl = document.getElementById('board');
const statusText = document.getElementById('statusText');
const evaluationText = document.getElementById('evaluationText');
const moveList = document.getElementById('moveList');
const depthSelect = document.getElementById('depthSelect');
const newGameBtn = document.getElementById('newGameBtn');

const game = new Chess();
let selectedSquare = null;
let aiThinking = false;

const PIECE_ICONS = {
  wp: '♙', wr: '♖', wn: '♘', wb: '♗', wq: '♕', wk: '♔',
  bp: '♟', br: '♜', bn: '♞', bb: '♝', bq: '♛', bk: '♚',
};

const files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];

const psqt = {
  p: [
    0, 0, 0, 0, 0, 0, 0, 0,
    4, 4, 5, 6, 6, 5, 4, 4,
    1, 1, 2, 4, 4, 2, 1, 1,
    0, 0, 0, 3, 3, 0, 0, 0,
    0, 0, 0, -2, -2, 0, 0, 0,
    0, -1, -1, 1, 1, -1, -1, 0,
    0, 1, 1, -3, -3, 1, 1, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
  ],
  n: [
    -5, -3, -2, -2, -2, -2, -3, -5,
    -3, -1, 0, 0, 0, 0, -1, -3,
    -2, 0, 2, 2, 2, 2, 0, -2,
    -2, 0, 2, 3, 3, 2, 0, -2,
    -2, 0, 2, 3, 3, 2, 0, -2,
    -2, 0, 2, 2, 2, 2, 0, -2,
    -3, -1, 0, 0, 0, 0, -1, -3,
    -5, -3, -2, -2, -2, -2, -3, -5,
  ],
  b: [
    -2, -1, -1, -1, -1, -1, -1, -2,
    -1, 1, 0, 0, 0, 0, 1, -1,
    -1, 0, 2, 1, 1, 2, 0, -1,
    -1, 1, 1, 2, 2, 1, 1, -1,
    -1, 0, 2, 2, 2, 2, 0, -1,
    -1, 2, 2, 1, 1, 2, 2, -1,
    -1, 1, 0, 0, 0, 0, 1, -1,
    -2, -1, -1, -1, -1, -1, -1, -2,
  ],
  r: [
    0, 0, 1, 2, 2, 1, 0, 0,
    -1, 0, 0, 0, 0, 0, 0, -1,
    -1, 0, 0, 0, 0, 0, 0, -1,
    -1, 0, 0, 0, 0, 0, 0, -1,
    -1, 0, 0, 0, 0, 0, 0, -1,
    -1, 0, 0, 0, 0, 0, 0, -1,
    2, 3, 3, 3, 3, 3, 3, 2,
    0, 0, 1, 2, 2, 1, 0, 0,
  ],
  q: [
    -2, -1, -1, 0, 0, -1, -1, -2,
    -1, 0, 0, 0, 0, 0, 0, -1,
    -1, 0, 1, 1, 1, 1, 0, -1,
    0, 0, 1, 1, 1, 1, 0, -1,
    -1, 0, 1, 1, 1, 1, 0, -1,
    -1, 1, 1, 1, 1, 1, 0, -1,
    -1, 0, 1, 0, 0, 0, 0, -1,
    -2, -1, -1, 0, 0, -1, -1, -2,
  ],
  k: [
    -4, -5, -5, -5, -5, -5, -5, -4,
    -3, -4, -4, -4, -4, -4, -4, -3,
    -2, -3, -3, -4, -4, -3, -3, -2,
    -1, -2, -2, -2, -2, -2, -2, -1,
    0, 0, -1, -2, -2, -1, 0, 0,
    2, 2, 0, 0, 0, 0, 2, 2,
    3, 3, 1, 0, 0, 1, 3, 3,
    2, 3, 1, 0, 0, 1, 3, 2,
  ],
};

const modelWeights = {
  material: 1.0,
  placement: 0.14,
  mobility: 0.08,
  kingPressure: 0.06,
};

const baseValues = { p: 100, n: 320, b: 330, r: 500, q: 900, k: 20000 };

function squareName(fileIndex, rankIndex) {
  return `${files[fileIndex]}${8 - rankIndex}`;
}

function renderBoard() {
  boardEl.innerHTML = '';

  for (let rank = 0; rank < 8; rank += 1) {
    for (let file = 0; file < 8; file += 1) {
      const sq = squareName(file, rank);
      const cell = document.createElement('button');
      cell.type = 'button';
      cell.className = `square ${(rank + file) % 2 === 0 ? 'light' : 'dark'}`;
      cell.dataset.square = sq;

      if (selectedSquare === sq) {
        cell.classList.add('selected');
      }

      const movesFromSelected = selectedSquare
        ? game.moves({ square: selectedSquare, verbose: true }).map((m) => m.to)
        : [];
      if (movesFromSelected.includes(sq)) {
        cell.classList.add('legal');
      }

      const piece = game.get(sq);
      if (piece) {
        const pieceSpan = document.createElement('span');
        pieceSpan.className = 'piece';
        pieceSpan.textContent = PIECE_ICONS[`${piece.color}${piece.type}`];
        cell.appendChild(pieceSpan);
      }

      if (rank === 7) {
        const fileCoord = document.createElement('span');
        fileCoord.className = 'coord file';
        fileCoord.textContent = files[file];
        cell.appendChild(fileCoord);
      }

      if (file === 0) {
        const rankCoord = document.createElement('span');
        rankCoord.className = 'coord rank';
        rankCoord.textContent = `${8 - rank}`;
        cell.appendChild(rankCoord);
      }

      cell.addEventListener('click', () => onSquareClick(sq));
      boardEl.appendChild(cell);
    }
  }

  updateStatus();
}

function onSquareClick(square) {
  if (aiThinking || game.game_over()) return;

  const piece = game.get(square);
  if (selectedSquare && tryHumanMove(selectedSquare, square)) {
    selectedSquare = null;
    renderBoard();
    window.setTimeout(makeAIMove, 120);
    return;
  }

  if (piece && piece.color === 'w' && game.turn() === 'w') {
    selectedSquare = square;
  } else {
    selectedSquare = null;
  }

  renderBoard();
}

function tryHumanMove(from, to) {
  const move = game.move({ from, to, promotion: 'q' });
  if (!move) return false;
  appendMove(move.san);
  return true;
}

function appendMove(san) {
  const history = game.history();
  if (history.length % 2 === 1) {
    const item = document.createElement('li');
    item.textContent = `${Math.ceil(history.length / 2)}. ${san}`;
    moveList.appendChild(item);
  } else {
    const item = moveList.lastElementChild;
    item.textContent += ` ${san}`;
  }
  moveList.scrollTop = moveList.scrollHeight;
}

function evaluatePosition() {
  let material = 0;
  let placement = 0;

  for (let rank = 0; rank < 8; rank += 1) {
    for (let file = 0; file < 8; file += 1) {
      const sq = squareName(file, rank);
      const piece = game.get(sq);
      if (!piece) continue;

      const sign = piece.color === 'w' ? 1 : -1;
      const index = piece.color === 'w' ? (rank * 8 + file) : ((7 - rank) * 8 + file);

      material += sign * baseValues[piece.type];
      placement += sign * psqt[piece.type][index];
    }
  }

  const currentTurn = game.turn();
  const legalCount = game.moves().length;
  const mobility = currentTurn === 'w' ? legalCount : -legalCount;

  const checkPressure = game.in_check() ? (currentTurn === 'w' ? -1 : 1) : 0;

  return (
    modelWeights.material * material +
    modelWeights.placement * placement * 10 +
    modelWeights.mobility * mobility * 10 +
    modelWeights.kingPressure * checkPressure * 100
  );
}

function minimax(depth, alpha, beta, maximizingPlayer) {
  if (depth === 0 || game.game_over()) {
    return { score: evaluatePosition() };
  }

  const moves = game.moves({ verbose: true });
  let bestMove = null;

  if (maximizingPlayer) {
    let maxEval = -Infinity;
    for (const move of moves) {
      game.move(move);
      const score = minimax(depth - 1, alpha, beta, false).score;
      game.undo();

      if (score > maxEval) {
        maxEval = score;
        bestMove = move;
      }
      alpha = Math.max(alpha, score);
      if (beta <= alpha) break;
    }
    return { score: maxEval, move: bestMove };
  }

  let minEval = Infinity;
  for (const move of moves) {
    game.move(move);
    const score = minimax(depth - 1, alpha, beta, true).score;
    game.undo();

    if (score < minEval) {
      minEval = score;
      bestMove = move;
    }
    beta = Math.min(beta, score);
    if (beta <= alpha) break;
  }
  return { score: minEval, move: bestMove };
}

function makeAIMove() {
  if (game.game_over() || game.turn() !== 'b') return;

  aiThinking = true;
  statusText.textContent = 'AI is thinking...';

  window.setTimeout(() => {
    const depth = Number(depthSelect.value);
    const result = minimax(depth, -Infinity, Infinity, false);

    if (result.move) {
      const move = game.move(result.move);
      appendMove(move.san);
    }

    aiThinking = false;
    selectedSquare = null;
    renderBoard();
  }, 80);
}

function updateStatus() {
  if (game.in_checkmate()) {
    statusText.textContent = game.turn() === 'w' ? 'Checkmate! Black wins.' : 'Checkmate! White wins.';
  } else if (game.in_draw()) {
    statusText.textContent = 'Draw game.';
  } else {
    const turnText = game.turn() === 'w' ? 'White to move' : 'Black to move';
    const checkText = game.in_check() ? ' (check)' : '';
    statusText.textContent = `${turnText}${checkText}`;
  }

  const evalCp = evaluatePosition() / 100;
  evaluationText.textContent = `Evaluation: ${evalCp.toFixed(2)}`;
}

newGameBtn.addEventListener('click', () => {
  game.reset();
  moveList.innerHTML = '';
  selectedSquare = null;
  aiThinking = false;
  renderBoard();
});

renderBoard();
