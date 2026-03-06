const boardEl = document.getElementById('board');
const statusText = document.getElementById('statusText');
const evaluationText = document.getElementById('evaluationText');
const moveList = document.getElementById('moveList');
const depthSelect = document.getElementById('depthSelect');
const newGameBtn = document.getElementById('newGameBtn');

const files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
const PIECE_ICONS = {
  P: '♙', R: '♖', N: '♘', B: '♗', Q: '♕', K: '♔',
  p: '♟', r: '♜', n: '♞', b: '♝', q: '♛', k: '♚',
};

const baseValues = { p: 100, n: 320, b: 330, r: 500, q: 900, k: 20000 };
const modelWeights = { material: 1.0, placement: 0.14, mobility: 0.08, kingPressure: 0.06 };

const psqt = {
  p: [0,0,0,0,0,0,0,0,4,4,5,6,6,5,4,4,1,1,2,4,4,2,1,1,0,0,0,3,3,0,0,0,0,0,0,-2,-2,0,0,0,0,-1,-1,1,1,-1,-1,0,0,1,1,-3,-3,1,1,0,0,0,0,0,0,0,0,0],
  n: [-5,-3,-2,-2,-2,-2,-3,-5,-3,-1,0,0,0,0,-1,-3,-2,0,2,2,2,2,0,-2,-2,0,2,3,3,2,0,-2,-2,0,2,3,3,2,0,-2,-2,0,2,2,2,2,0,-2,-3,-1,0,0,0,0,-1,-3,-5,-3,-2,-2,-2,-2,-3,-5],
  b: [-2,-1,-1,-1,-1,-1,-1,-2,-1,1,0,0,0,0,1,-1,-1,0,2,1,1,2,0,-1,-1,1,1,2,2,1,1,-1,-1,0,2,2,2,2,0,-1,-1,2,2,1,1,2,2,-1,-1,1,0,0,0,0,1,-1,-2,-1,-1,-1,-1,-1,-1,-2],
  r: [0,0,1,2,2,1,0,0,-1,0,0,0,0,0,0,-1,-1,0,0,0,0,0,0,-1,-1,0,0,0,0,0,0,-1,-1,0,0,0,0,0,0,-1,-1,0,0,0,0,0,0,-1,2,3,3,3,3,3,3,2,0,0,1,2,2,1,0,0],
  q: [-2,-1,-1,0,0,-1,-1,-2,-1,0,0,0,0,0,0,-1,-1,0,1,1,1,1,0,-1,0,0,1,1,1,1,0,-1,-1,0,1,1,1,1,0,-1,-1,1,1,1,1,1,0,-1,-1,0,1,0,0,0,0,-1,-2,-1,-1,0,0,-1,-1,-2],
  k: [-4,-5,-5,-5,-5,-5,-5,-4,-3,-4,-4,-4,-4,-4,-4,-3,-2,-3,-3,-4,-4,-3,-3,-2,-1,-2,-2,-2,-2,-2,-2,-1,0,0,-1,-2,-2,-1,0,0,2,2,0,0,0,0,2,2,3,3,1,0,0,1,3,3,2,3,1,0,0,1,3,2],
};

const initialState = () => ({
  board: [
    ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
    ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
    [null, null, null, null, null, null, null, null],
    [null, null, null, null, null, null, null, null],
    [null, null, null, null, null, null, null, null],
    [null, null, null, null, null, null, null, null],
    ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
    ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
  ],
  turn: 'w',
  castling: { wk: true, wq: true, bk: true, bq: true },
  enPassant: null,
  history: [],
});

let state = initialState();
let selectedSquare = null;
let aiThinking = false;

function cloneState(src) {
  return {
    board: src.board.map((row) => [...row]),
    turn: src.turn,
    castling: { ...src.castling },
    enPassant: src.enPassant ? { ...src.enPassant } : null,
    history: [...src.history],
  };
}

const inBounds = (r, c) => r >= 0 && r < 8 && c >= 0 && c < 8;
const isWhite = (p) => p && p === p.toUpperCase();
const colorOf = (p) => (isWhite(p) ? 'w' : 'b');
const toSq = (r, c) => `${files[c]}${8 - r}`;
const fromSq = (sq) => ({ r: 8 - Number(sq[1]), c: files.indexOf(sq[0]) });

function isSquareAttacked(board, r, c, byColor) {
  const pawnDir = byColor === 'w' ? -1 : 1;
  const pawn = byColor === 'w' ? 'P' : 'p';
  for (const dc of [-1, 1]) {
    const rr = r - pawnDir;
    const cc = c + dc;
    if (inBounds(rr, cc) && board[rr][cc] === pawn) return true;
  }

  const knight = byColor === 'w' ? 'N' : 'n';
  const jumps = [[-2,-1],[-2,1],[-1,-2],[-1,2],[1,-2],[1,2],[2,-1],[2,1]];
  for (const [dr, dc] of jumps) {
    const rr = r + dr;
    const cc = c + dc;
    if (inBounds(rr, cc) && board[rr][cc] === knight) return true;
  }

  const sliders = [
    { dirs: [[-1,0],[1,0],[0,-1],[0,1]], pieces: byColor === 'w' ? ['R','Q'] : ['r','q'] },
    { dirs: [[-1,-1],[-1,1],[1,-1],[1,1]], pieces: byColor === 'w' ? ['B','Q'] : ['b','q'] },
  ];
  for (const group of sliders) {
    for (const [dr, dc] of group.dirs) {
      let rr = r + dr;
      let cc = c + dc;
      while (inBounds(rr, cc)) {
        const p = board[rr][cc];
        if (p) {
          if (group.pieces.includes(p)) return true;
          break;
        }
        rr += dr;
        cc += dc;
      }
    }
  }

  const king = byColor === 'w' ? 'K' : 'k';
  for (let dr = -1; dr <= 1; dr += 1) {
    for (let dc = -1; dc <= 1; dc += 1) {
      if (!dr && !dc) continue;
      const rr = r + dr;
      const cc = c + dc;
      if (inBounds(rr, cc) && board[rr][cc] === king) return true;
    }
  }

  return false;
}

function kingPosition(board, color) {
  const king = color === 'w' ? 'K' : 'k';
  for (let r = 0; r < 8; r += 1) {
    for (let c = 0; c < 8; c += 1) {
      if (board[r][c] === king) return { r, c };
    }
  }
  return null;
}

function inCheck(board, color) {
  const kp = kingPosition(board, color);
  if (!kp) return false;
  return isSquareAttacked(board, kp.r, kp.c, color === 'w' ? 'b' : 'w');
}

function makeMove(st, move) {
  const next = cloneState(st);
  const piece = next.board[move.from.r][move.from.c];
  const target = next.board[move.to.r][move.to.c];

  next.board[move.from.r][move.from.c] = null;

  if (move.enPassantCapture) {
    next.board[move.from.r][move.to.c] = null;
  }

  let placed = piece;
  if (move.promotion) placed = move.promotion;
  next.board[move.to.r][move.to.c] = placed;

  if (piece === 'K') {
    next.castling.wk = false;
    next.castling.wq = false;
  }
  if (piece === 'k') {
    next.castling.bk = false;
    next.castling.bq = false;
  }
  if (piece === 'R' && move.from.r === 7 && move.from.c === 0) next.castling.wq = false;
  if (piece === 'R' && move.from.r === 7 && move.from.c === 7) next.castling.wk = false;
  if (piece === 'r' && move.from.r === 0 && move.from.c === 0) next.castling.bq = false;
  if (piece === 'r' && move.from.r === 0 && move.from.c === 7) next.castling.bk = false;

  if (target === 'R' && move.to.r === 7 && move.to.c === 0) next.castling.wq = false;
  if (target === 'R' && move.to.r === 7 && move.to.c === 7) next.castling.wk = false;
  if (target === 'r' && move.to.r === 0 && move.to.c === 0) next.castling.bq = false;
  if (target === 'r' && move.to.r === 0 && move.to.c === 7) next.castling.bk = false;

  if (move.castle === 'wk') {
    next.board[7][7] = null;
    next.board[7][5] = 'R';
  } else if (move.castle === 'wq') {
    next.board[7][0] = null;
    next.board[7][3] = 'R';
  } else if (move.castle === 'bk') {
    next.board[0][7] = null;
    next.board[0][5] = 'r';
  } else if (move.castle === 'bq') {
    next.board[0][0] = null;
    next.board[0][3] = 'r';
  }

  next.enPassant = null;
  if ((piece === 'P' || piece === 'p') && Math.abs(move.to.r - move.from.r) === 2) {
    next.enPassant = { r: (move.to.r + move.from.r) / 2, c: move.from.c };
  }

  next.turn = st.turn === 'w' ? 'b' : 'w';
  return next;
}

function generatePseudoMoves(st, color) {
  const moves = [];
  const ownWhite = color === 'w';

  for (let r = 0; r < 8; r += 1) {
    for (let c = 0; c < 8; c += 1) {
      const piece = st.board[r][c];
      if (!piece || isWhite(piece) !== ownWhite) continue;
      const lower = piece.toLowerCase();

      if (lower === 'p') {
        const dir = ownWhite ? -1 : 1;
        const startRow = ownWhite ? 6 : 1;
        const promoteRow = ownWhite ? 0 : 7;
        const one = r + dir;
        if (inBounds(one, c) && !st.board[one][c]) {
          moves.push({ from: { r, c }, to: { r: one, c }, promotion: one === promoteRow ? (ownWhite ? 'Q' : 'q') : null });
          const two = r + dir * 2;
          if (r === startRow && !st.board[two][c]) {
            moves.push({ from: { r, c }, to: { r: two, c }, promotion: null });
          }
        }
        for (const dc of [-1, 1]) {
          const cc = c + dc;
          if (!inBounds(one, cc)) continue;
          const target = st.board[one][cc];
          if (target && isWhite(target) !== ownWhite) {
            moves.push({ from: { r, c }, to: { r: one, c: cc }, promotion: one === promoteRow ? (ownWhite ? 'Q' : 'q') : null });
          }
          if (st.enPassant && st.enPassant.r === one && st.enPassant.c === cc) {
            moves.push({ from: { r, c }, to: { r: one, c: cc }, enPassantCapture: true, promotion: null });
          }
        }
      }

      if (lower === 'n') {
        const jumps = [[-2,-1],[-2,1],[-1,-2],[-1,2],[1,-2],[1,2],[2,-1],[2,1]];
        for (const [dr, dc] of jumps) {
          const rr = r + dr;
          const cc = c + dc;
          if (!inBounds(rr, cc)) continue;
          const target = st.board[rr][cc];
          if (!target || isWhite(target) !== ownWhite) {
            moves.push({ from: { r, c }, to: { r: rr, c: cc }, promotion: null });
          }
        }
      }

      if (lower === 'b' || lower === 'r' || lower === 'q') {
        const dirs = [];
        if (lower === 'b' || lower === 'q') dirs.push([-1,-1],[-1,1],[1,-1],[1,1]);
        if (lower === 'r' || lower === 'q') dirs.push([-1,0],[1,0],[0,-1],[0,1]);
        for (const [dr, dc] of dirs) {
          let rr = r + dr;
          let cc = c + dc;
          while (inBounds(rr, cc)) {
            const target = st.board[rr][cc];
            if (!target) {
              moves.push({ from: { r, c }, to: { r: rr, c: cc }, promotion: null });
            } else {
              if (isWhite(target) !== ownWhite) moves.push({ from: { r, c }, to: { r: rr, c: cc }, promotion: null });
              break;
            }
            rr += dr;
            cc += dc;
          }
        }
      }

      if (lower === 'k') {
        for (let dr = -1; dr <= 1; dr += 1) {
          for (let dc = -1; dc <= 1; dc += 1) {
            if (!dr && !dc) continue;
            const rr = r + dr;
            const cc = c + dc;
            if (!inBounds(rr, cc)) continue;
            const target = st.board[rr][cc];
            if (!target || isWhite(target) !== ownWhite) {
              moves.push({ from: { r, c }, to: { r: rr, c: cc }, promotion: null });
            }
          }
        }

        if (ownWhite && r === 7 && c === 4 && !inCheck(st.board, 'w')) {
          if (st.castling.wk && !st.board[7][5] && !st.board[7][6]
            && !isSquareAttacked(st.board, 7, 5, 'b') && !isSquareAttacked(st.board, 7, 6, 'b')) {
            moves.push({ from: { r, c }, to: { r: 7, c: 6 }, castle: 'wk', promotion: null });
          }
          if (st.castling.wq && !st.board[7][1] && !st.board[7][2] && !st.board[7][3]
            && !isSquareAttacked(st.board, 7, 3, 'b') && !isSquareAttacked(st.board, 7, 2, 'b')) {
            moves.push({ from: { r, c }, to: { r: 7, c: 2 }, castle: 'wq', promotion: null });
          }
        }

        if (!ownWhite && r === 0 && c === 4 && !inCheck(st.board, 'b')) {
          if (st.castling.bk && !st.board[0][5] && !st.board[0][6]
            && !isSquareAttacked(st.board, 0, 5, 'w') && !isSquareAttacked(st.board, 0, 6, 'w')) {
            moves.push({ from: { r, c }, to: { r: 0, c: 6 }, castle: 'bk', promotion: null });
          }
          if (st.castling.bq && !st.board[0][1] && !st.board[0][2] && !st.board[0][3]
            && !isSquareAttacked(st.board, 0, 3, 'w') && !isSquareAttacked(st.board, 0, 2, 'w')) {
            moves.push({ from: { r, c }, to: { r: 0, c: 2 }, castle: 'bq', promotion: null });
          }
        }
      }
    }
  }

  return moves;
}

function legalMoves(st, color = st.turn) {
  return generatePseudoMoves(st, color).filter((move) => {
    const next = makeMove(st, move);
    return !inCheck(next.board, color);
  });
}

function moveString(move) {
  return `${toSq(move.from.r, move.from.c)}-${toSq(move.to.r, move.to.c)}`;
}

function evaluate(st) {
  let material = 0;
  let placement = 0;
  for (let r = 0; r < 8; r += 1) {
    for (let c = 0; c < 8; c += 1) {
      const piece = st.board[r][c];
      if (!piece) continue;
      const white = isWhite(piece);
      const sign = white ? 1 : -1;
      const lower = piece.toLowerCase();
      const index = white ? (r * 8 + c) : ((7 - r) * 8 + c);
      material += sign * baseValues[lower];
      placement += sign * psqt[lower][index];
    }
  }
  const mobility = legalMoves(st, st.turn).length * (st.turn === 'w' ? 1 : -1);
  const checkPressure = inCheck(st.board, st.turn) ? (st.turn === 'w' ? -1 : 1) : 0;

  return modelWeights.material * material
    + modelWeights.placement * placement * 10
    + modelWeights.mobility * mobility * 10
    + modelWeights.kingPressure * checkPressure * 100;
}

function minimax(st, depth, alpha, beta, maximizingPlayer) {
  const color = maximizingPlayer ? 'w' : 'b';
  const moves = legalMoves(st, color);
  if (depth === 0 || moves.length === 0) return { score: evaluate(st) };

  let bestMove = null;
  if (maximizingPlayer) {
    let best = -Infinity;
    for (const mv of moves) {
      const score = minimax(makeMove(st, mv), depth - 1, alpha, beta, false).score;
      if (score > best) {
        best = score;
        bestMove = mv;
      }
      alpha = Math.max(alpha, score);
      if (beta <= alpha) break;
    }
    return { score: best, move: bestMove };
  }

  let best = Infinity;
  for (const mv of moves) {
    const score = minimax(makeMove(st, mv), depth - 1, alpha, beta, true).score;
    if (score < best) {
      best = score;
      bestMove = mv;
    }
    beta = Math.min(beta, score);
    if (beta <= alpha) break;
  }
  return { score: best, move: bestMove };
}

function appendMove(text) {
  if (state.history.length % 2 === 1) {
    const li = document.createElement('li');
    li.textContent = `${Math.ceil(state.history.length / 2)}. ${text}`;
    moveList.appendChild(li);
  } else {
    moveList.lastElementChild.textContent += ` ${text}`;
  }
  moveList.scrollTop = moveList.scrollHeight;
}

function updateStatus() {
  const moves = legalMoves(state, state.turn);
  const turnText = state.turn === 'w' ? 'White to move' : 'Black to move';

  if (moves.length === 0) {
    if (inCheck(state.board, state.turn)) {
      statusText.textContent = state.turn === 'w' ? 'Checkmate! Black wins.' : 'Checkmate! White wins.';
    } else {
      statusText.textContent = 'Draw game (stalemate).';
    }
  } else {
    statusText.textContent = `${turnText}${inCheck(state.board, state.turn) ? ' (check)' : ''}`;
  }

  evaluationText.textContent = `Evaluation: ${(evaluate(state) / 100).toFixed(2)}`;
}

function renderBoard() {
  boardEl.innerHTML = '';
  const legalTo = selectedSquare
    ? legalMoves(state, 'w')
      .filter((m) => toSq(m.from.r, m.from.c) === selectedSquare)
      .map((m) => toSq(m.to.r, m.to.c))
    : [];

  for (let r = 0; r < 8; r += 1) {
    for (let c = 0; c < 8; c += 1) {
      const sq = toSq(r, c);
      const cell = document.createElement('button');
      cell.type = 'button';
      cell.className = `square ${(r + c) % 2 === 0 ? 'light' : 'dark'}`;
      if (selectedSquare === sq) cell.classList.add('selected');
      if (legalTo.includes(sq)) cell.classList.add('legal');

      const p = state.board[r][c];
      if (p) {
        const pieceSpan = document.createElement('span');
        pieceSpan.className = 'piece';
        pieceSpan.textContent = PIECE_ICONS[p];
        cell.appendChild(pieceSpan);
      }

      if (r === 7) {
        const fileCoord = document.createElement('span');
        fileCoord.className = 'coord file';
        fileCoord.textContent = files[c];
        cell.appendChild(fileCoord);
      }
      if (c === 0) {
        const rankCoord = document.createElement('span');
        rankCoord.className = 'coord rank';
        rankCoord.textContent = `${8 - r}`;
        cell.appendChild(rankCoord);
      }

      cell.addEventListener('click', () => onSquareClick(sq));
      boardEl.appendChild(cell);
    }
  }

  updateStatus();
}

function onSquareClick(square) {
  if (aiThinking || state.turn !== 'w') return;
  const { r, c } = fromSq(square);
  const piece = state.board[r][c];

  if (selectedSquare) {
    const humanMoves = legalMoves(state, 'w');
    const chosen = humanMoves.find((m) => toSq(m.from.r, m.from.c) === selectedSquare && toSq(m.to.r, m.to.c) === square);
    if (chosen) {
      state = makeMove(state, chosen);
      state.history.push(moveString(chosen));
      appendMove(moveString(chosen));
      selectedSquare = null;
      renderBoard();
      window.setTimeout(makeAIMove, 120);
      return;
    }
  }

  if (piece && colorOf(piece) === 'w') {
    selectedSquare = square;
  } else {
    selectedSquare = null;
  }
  renderBoard();
}

function makeAIMove() {
  if (state.turn !== 'b') return;
  const moves = legalMoves(state, 'b');
  if (!moves.length) {
    renderBoard();
    return;
  }

  aiThinking = true;
  statusText.textContent = 'AI is thinking...';
  window.setTimeout(() => {
    const depth = Number(depthSelect.value);
    const result = minimax(state, depth, -Infinity, Infinity, false);
    const move = result.move || moves[0];
    state = makeMove(state, move);
    state.history.push(moveString(move));
    appendMove(moveString(move));
    aiThinking = false;
    renderBoard();
  }, 80);
}

newGameBtn.addEventListener('click', () => {
  state = initialState();
  selectedSquare = null;
  aiThinking = false;
  moveList.innerHTML = '';
  renderBoard();
});

renderBoard();
