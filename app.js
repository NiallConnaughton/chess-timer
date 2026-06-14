const WARNING_MS  = 30_000;
const CRITICAL_MS = 10_000;
const TICK_MS     = 100;

// ── State ──────────────────────────────────────────────────────────────────

const state = {
  mode:         'two-player',  // 'two-player' | 'single-clock'
  times:        [0, 0],        // ms remaining per player
  active:       0,             // 0 | 1
  running:      false,
  over:         false,
  tickId:       null,
  lastSettings: null,          // { mode, times: [ms, ms] }
};

// ── DOM ────────────────────────────────────────────────────────────────────

const setupScreen = document.getElementById('setup-screen');
const gameScreen  = document.getElementById('game-screen');
const gameOverEl  = document.getElementById('game-over');
const panels      = [document.getElementById('p1-panel'), document.getElementById('p2-panel')];
const timerEls    = [document.getElementById('p1-time'),  document.getElementById('p2-time')];
const pauseBtn    = document.getElementById('pause-btn');
const gameOverMsg = document.getElementById('game-over-msg');
const configs     = [document.getElementById('p1-config'), document.getElementById('p2-config')];
const customs     = [document.getElementById('p1-custom'), document.getElementById('p2-custom')];

// ── Rendering ──────────────────────────────────────────────────────────────

function fmt(ms) {
  if (ms <= 0) return '0:00';
  const s = Math.ceil(ms / 1000);
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
}

function render() {
  const noP2 = state.mode === 'single-clock';

  timerEls.forEach((el, i) => {
    if (i === 1 && noP2) {
      el.textContent = '—';
      el.className = 'timer no-clock';
    } else {
      el.textContent = fmt(state.times[i]);
      const ms = state.times[i];
      el.className = 'timer' +
        (ms <= CRITICAL_MS ? ' critical' : ms <= WARNING_MS ? ' warning' : '');
    }
  });

  panels.forEach((el, i) =>
    el.classList.toggle('active', i === state.active && state.running)
  );

  pauseBtn.textContent = state.running ? 'Pause' : 'Resume';
}

// ── Game logic ─────────────────────────────────────────────────────────────

function tick() {
  // In single-clock mode, child's turn doesn't count down.
  if (state.mode === 'single-clock' && state.active === 1) return;

  state.times[state.active] -= TICK_MS;

  if (state.times[state.active] <= 0) {
    state.times[state.active] = 0;
    render();
    endGame();
    return;
  }
  render();
}

function startTicking() {
  if (state.tickId || state.over) return;
  state.running = true;
  state.tickId  = setInterval(tick, TICK_MS);
  render();
}

function stopTicking() {
  clearInterval(state.tickId);
  state.tickId = null;
  state.running = false;
}

function switchPlayer() {
  if (!state.running || state.over) return;
  state.active = 1 - state.active;
  render();
}

function endGame() {
  stopTicking();
  state.over = true;
  gameOverMsg.textContent =
    `${state.active === 0 ? 'Player 1' : 'Player 2'}'s time is up!`;
  gameOverEl.classList.remove('hidden');
  render();
}

// ── Screen transitions ─────────────────────────────────────────────────────

function showGame(settings) {
  state.lastSettings = settings;
  state.mode   = settings.mode;
  state.times  = [...settings.times];
  state.active = 0;
  state.over   = false;
  stopTicking();

  setupScreen.classList.add('hidden');
  gameOverEl.classList.add('hidden');
  gameScreen.classList.remove('hidden');

  render();
  startTicking();
}

function showSetup() {
  stopTicking();
  state.over = false;
  gameScreen.classList.add('hidden');
  gameOverEl.classList.add('hidden');
  setupScreen.classList.remove('hidden');
  if (state.lastSettings) restoreSettings(state.lastSettings);
}

// ── Setup UI ───────────────────────────────────────────────────────────────

const selMinutes = [5, 5];
let selMode = 'two-player';

function getMs(idx) {
  const v = parseInt(customs[idx].value, 10);
  return v > 0 ? v * 60_000 : selMinutes[idx] * 60_000;
}

function setMode(mode) {
  selMode = mode;
  document.getElementById('btn-two-player')
    .classList.toggle('selected', mode === 'two-player');
  document.getElementById('btn-single-clock')
    .classList.toggle('selected', mode === 'single-clock');
  configs[1].classList.toggle('disabled', mode === 'single-clock');
}

function restoreSettings(s) {
  setMode(s.mode);
  [0, 1].forEach(i => {
    const mins = s.times[i] / 60_000;
    const group = document.querySelector(`.presets[data-player="${i + 1}"]`);
    group.querySelectorAll('.preset-btn').forEach(btn =>
      btn.classList.toggle('selected', Number(btn.dataset.minutes) === mins)
    );
    if ([1, 3, 5, 10, 15, 30].includes(mins)) {
      selMinutes[i]   = mins;
      customs[i].value = '';
    } else {
      customs[i].value = mins;
    }
  });
}

document.querySelectorAll('.presets').forEach(group => {
  const idx = Number(group.dataset.player) - 1;
  group.querySelectorAll('.preset-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      group.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');
      selMinutes[idx]   = Number(btn.dataset.minutes);
      customs[idx].value = '';
    });
  });
});

customs.forEach((inp, idx) => {
  inp.addEventListener('input', () => {
    document.querySelector(`.presets[data-player="${idx + 1}"]`)
      .querySelectorAll('.preset-btn').forEach(b => b.classList.remove('selected'));
  });
});

document.getElementById('btn-two-player')
  .addEventListener('click', () => setMode('two-player'));
document.getElementById('btn-single-clock')
  .addEventListener('click', () => setMode('single-clock'));

document.getElementById('start-btn').addEventListener('click', () =>
  showGame({ mode: selMode, times: [getMs(0), getMs(1)] })
);

// ── Game screen controls ───────────────────────────────────────────────────

document.getElementById('pause-btn').addEventListener('click', () => {
  if (state.over) return;
  if (state.running) { stopTicking(); render(); }
  else startTicking();
});

document.getElementById('new-game-btn').addEventListener('click', showSetup);

document.getElementById('play-again-btn').addEventListener('click', () => {
  if (state.lastSettings) showGame(state.lastSettings);
});

panels.forEach((panel, idx) => {
  panel.addEventListener('click', () => {
    if (state.over || !state.running) return;
    if (state.active === idx) switchPlayer();
  });
});

// ── Keyboard ───────────────────────────────────────────────────────────────

document.addEventListener('keydown', e => {
  if (e.code !== 'Space') return;
  e.preventDefault();

  if (!setupScreen.classList.contains('hidden')) {
    showGame({ mode: selMode, times: [getMs(0), getMs(1)] });
    return;
  }

  if (state.over) return;
  if (state.running) switchPlayer();
  else startTicking();
});
