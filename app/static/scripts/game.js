const gameConfigScript = document.getElementById('game-config');
const currentUserScript = document.getElementById('current-user');
window.GAME_CONFIG = gameConfigScript ? JSON.parse(gameConfigScript.textContent || '{}') : {};
window.CURRENT_USER = currentUserScript ? JSON.parse(currentUserScript.textContent || '{}') : { id: 0, username: '' };

document.addEventListener('DOMContentLoaded', () => {
    // Programmatic Web Audio Synthesizer
    const SoundEffects = {
        ctx: null,
        init() {
            if (!this.ctx) {
                this.ctx = new (window.AudioContext || window.webkitAudioContext)();
            }
            if (this.ctx.state === 'suspended') {
                this.ctx.resume();
            }
        },
        playClick() {
            try {
                this.init();
                const osc = this.ctx.createOscillator();
                const gain = this.ctx.createGain();
                osc.connect(gain);
                gain.connect(this.ctx.destination);
                osc.frequency.setValueAtTime(580, this.ctx.currentTime);
                gain.gain.setValueAtTime(0.08, this.ctx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + 0.08);
                osc.start();
                osc.stop(this.ctx.currentTime + 0.08);
            } catch (e) {}
        },
        playCorrect() {
            try {
                this.init();
                const now = this.ctx.currentTime;
                const playTone = (freq, start, duration) => {
                    const osc = this.ctx.createOscillator();
                    const gain = this.ctx.createGain();
                    osc.connect(gain);
                    gain.connect(this.ctx.destination);
                    osc.frequency.setValueAtTime(freq, start);
                    gain.gain.setValueAtTime(0.12, start);
                    gain.gain.exponentialRampToValueAtTime(0.01, start + duration);
                    osc.start(start);
                    osc.stop(start + duration);
                };
                playTone(523.25, now, 0.12); // C5
                playTone(659.25, now + 0.08, 0.12); // E5
                playTone(783.99, now + 0.16, 0.25); // G5
            } catch (e) {}
        },
        playWrong() {
            try {
                this.init();
                const osc = this.ctx.createOscillator();
                const gain = this.ctx.createGain();
                osc.connect(gain);
                gain.connect(this.ctx.destination);
                osc.frequency.setValueAtTime(220, this.ctx.currentTime);
                osc.frequency.linearRampToValueAtTime(110, this.ctx.currentTime + 0.35);
                gain.gain.setValueAtTime(0.15, this.ctx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + 0.35);
                osc.start();
                osc.stop(this.ctx.currentTime + 0.35);
            } catch (e) {}
        },
        playStreak() {
            try {
                this.init();
                const now = this.ctx.currentTime;
                const osc = this.ctx.createOscillator();
                const gain = this.ctx.createGain();
                osc.type = 'triangle';
                osc.connect(gain);
gain.connect(this.ctx.destination);
                osc.frequency.setValueAtTime(440, now);
                osc.frequency.exponentialRampToValueAtTime(987.77, now + 0.4); // B5
                gain.gain.setValueAtTime(0.1, now);
                gain.gain.exponentialRampToValueAtTime(0.01, now + 0.4);
                osc.start();
                osc.stop(now + 0.4);
            } catch (e) {}
        },
        playTick() {
            try {
                this.init();
                const osc = this.ctx.createOscillator();
                const gain = this.ctx.createGain();
                osc.connect(gain);
                gain.connect(this.ctx.destination);
                osc.frequency.setValueAtTime(800, this.ctx.currentTime);
                gain.gain.setValueAtTime(0.02, this.ctx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.05);
                osc.start();
                osc.stop(this.ctx.currentTime + 0.05);
            } catch (e) {}
        }
    };

    // Canvas Confetti System
    const Confetti = {
        canvas: null,
        ctx: null,
        particles: [],
        animationFrame: null,
        init() {
            if (!this.canvas) {
                this.canvas = document.createElement('canvas');
                this.canvas.style.position = 'fixed';
                this.canvas.style.top = '0';
                this.canvas.style.left = '0';
                this.canvas.style.width = '100vw';
                this.canvas.style.height = '100vh';
                this.canvas.style.pointerEvents = 'none';
                this.canvas.style.zIndex = '9999';
                document.body.appendChild(this.canvas);
                this.ctx = this.canvas.getContext('2d');
                window.addEventListener('resize', () => {
                    this.canvas.width = window.innerWidth;
                    this.canvas.height = window.innerHeight;
                });
            }
            this.canvas.width = window.innerWidth;
            this.canvas.height = window.innerHeight;
        },
        burst() {
            this.init();
            this.particles = [];
            const colors = ['#1a56db', '#fbbf24', '#10b981', '#ef4444', '#8b5cf6'];
            for (let i = 0; i < 100; i++) {
                this.particles.push({
                    x: window.innerWidth / 2,
                    y: window.innerHeight / 2,
                    vx: (Math.random() - 0.5) * 14,
                    vy: (Math.random() - 0.75) * 18,
                    radius: Math.random() * 5 + 3,
                    color: colors[Math.floor(Math.random() * colors.length)],
                    alpha: 1.0,
                    decay: Math.random() * 0.015 + 0.01
                });
            }
            if (!this.animationFrame) {
                this.loop();
            }
        },
        loop() {
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
let active = false;
            this.particles.forEach(p => {
                if (p.alpha > 0) {
                    active = true;
                    p.x += p.vx;
                    p.y += p.vy;
                    p.vy += 0.4; // gravity
                    p.alpha -= p.decay;
                    this.ctx.beginPath();
                    this.ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                    this.ctx.fillStyle = p.color;
                    this.ctx.globalAlpha = p.alpha;
                    this.ctx.fill();
                }
            });
            if (active) {
                this.animationFrame = requestAnimationFrame(() => this.loop());
            } else {
                this.animationFrame = null;
                this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
            }
        }
    };

    // Basic UI Elements
    const screenLobby = document.getElementById('screen-lobby');
    const screenScene = document.getElementById('screen-scene');
    const screenRoundIntro = document.getElementById('screen-round-intro');
    const screenGame = document.getElementById('screen-game');
    const screenBreak = document.getElementById('screen-break');
    const screenResults = document.getElementById('screen-results');
    const sceneCountdown = document.getElementById('scene-countdown');
    const roundIntroCountdown = document.getElementById('round-intro-countdown');
    const roundIntroKicker = document.getElementById('round-intro-kicker');
    const roundIntroTitle = document.getElementById('round-intro-title');
    const roundIntroDescription = document.getElementById('round-intro-description');
    
    const lobbyPlayers = document.getElementById('lobby-players');
    const playerCount = document.getElementById('player-count');
    const btnReady = document.getElementById('btn-ready');
    const btnStart = document.getElementById('btn-start');
    const teamSelector = document.getElementById('team-selector');
    const selectedTeamStatus = document.getElementById('selected-team-status');
    
    // Game Elements
    const qArticle = document.getElementById('q-article');
    const qText = document.getElementById('q-text');
    const answersContainer = document.getElementById('answers-container');
    const gameTimer = document.getElementById('game-timer');
    const gameProgress = document.getElementById('game-progress');
    const gameLeaderboard = document.getElementById('game-leaderboard');
    const gameRoundInfo = document.getElementById('game-round-info');
    const roundBadge = document.getElementById('round-badge');
    const roundDesc = document.getElementById('round-desc');
    const streakDisplay = document.getElementById('streak-display');
    const streakCount = document.getElementById('streak-count');
    const btn5050 = document.getElementById('btn-5050');
    const btnHint = document.getElementById('btn-hint');
    
    // Popups
    const expPopup = document.getElementById('explanation-popup');
    const expTitle = document.getElementById('exp-title');
    const expText = document.getElementById('exp-text');
    const hintPopup = document.getElementById('hint-popup');
    const hintText = document.getElementById('hint-text');
    const badgeModal = document.getElementById('badge-modal');
    
    // Results
    const podium = document.getElementById('results-podium');
    const resScore = document.getElementById('res-score');
const resCorrect = document.getElementById('res-correct');
    const resStreak = document.getElementById('res-streak');
    const btnPlayAgain = document.getElementById('btn-play-again');
    const breakCountdown = document.getElementById('break-countdown');
    const breakRankings = document.getElementById('break-rankings');
    const breakAdvancing = document.getElementById('break-advancing');
    const breakEliminated = document.getElementById('break-eliminated');
    const breakTitle = document.getElementById('break-title');
    const breakSubtitle = document.getElementById('break-subtitle');
    const tournamentWinnerBanner = document.getElementById('tournament-winner-banner');
    const winnerTeamName = document.getElementById('winner-team-name');
    const mvpPlayerName = document.getElementById('mvp-player-name');
    const mvpPlayerScore = document.getElementById('mvp-player-score');
    // Round 3 Detective Elements
    const round3GameLayout = document.getElementById('round3-game-layout');
    const r3Timer = document.getElementById('r3-timer');
    const r3CaseTitle = document.getElementById('r3-case-title');
    const r3Score = document.getElementById('r3-score');
    const r3Streak = document.getElementById('r3-streak');
    const r3Rank = document.getElementById('r3-rank');
    const r3MyTeam = document.getElementById('r3-my-team');
    const r3Instruction = document.getElementById('r3-instruction');
    const btnR3Submit = document.getElementById('btn-r3-submit');
    const btnR3Next = document.getElementById('btn-r3-next');
    const r3InteractionLayer = document.getElementById('r3-interaction-layer');
    const r3CaseImage = document.getElementById('r3-case-image');
    const r3ImageWrapper = document.getElementById('r3-image-wrapper');
    let r3CurrentHandler = null;

    // Round 4 Incident Response Elements
    const round4GameLayout = document.getElementById('round4-game-layout');
    const r4Timer = document.getElementById('r4-timer');
    const r4IncidentTitle = document.getElementById('r4-incident-title');
    const r4ActiveTeam = document.getElementById('r4-active-team');
    const r4CurrentMissionIndex = document.getElementById('r4-current-mission-index');
    const r4Instruction = document.getElementById('r4-instruction');
    const r4InteractionLayer = document.getElementById('r4-interaction-layer');
    const r4CaseImage = document.getElementById('r4-case-image');
    const r4ImageWrapper = document.getElementById('r4-image-wrapper');
    const r4TeammateList = document.getElementById('r4-teammate-list');
    const r4SpectatorOverlay = document.getElementById('r4-spectator-overlay');
    const r4ActivePlayerNameOverlay = document.getElementById('r4-active-player-name-overlay');
    const r4OpponentTeamName = document.getElementById('r4-opponent-team-name');
    const r4OpponentScore = document.getElementById('r4-opponent-score');
    const r4OpponentProgressDots = document.getElementById('r4-opponent-progress-dots');
    const r4TeamScore = document.getElementById('r4-team-score');
    const btnR4Submit = document.getElementById('btn-r4-submit');
    const btnR4Hint = document.getElementById('btn-r4-hint');
    let r4CurrentHandler = null;
    let r4ActivePlayerSid = null;
    let r4HintUsed = false;

    // State
    let socket;
    let myAvatar = '👤';
    let myTournamentMode = true;
    let myTeam = null;
    let isReady = false;
    let hasAnswered = false;
    let currentLifelines = { fifty_fifty: true, hint: true };
    let tournamentMode = true;
    let currentRound = 0;
    let currentTimeLimit = 20;
    let isEliminated = false;
    let currentPlayers = [];
    let currentAnswersProgress = [];
    let sceneCountdownTimer = null;
    let roundIntroTimer = null;
    let isAnswerLocked = false;

    const TOURNAMENT_ROUNDS = {
        1: { name: 'Vòng 1 — Loại sơ' },
        2: { name: 'Vòng 2 — Bán kết' },
        3: { name: 'Vòng 3 — Chung kết' },
        4: { name: 'Vòng 4 — Đối kháng' },
    };

    const teamLocked = Boolean(window.GAME_CONFIG.playerTeam);

    // ==========================================================================
    // CYBER DETECTIVE ENGINE - INTERACTION HANDLERS
    // ==========================================================================

    class BaseInteractionHandler {
        constructor(container, caseData, onAnswerChange) {
            this.container = container;
            this.caseData = caseData;
            this.onAnswerChange = onAnswerChange;
            this.submitted = false;
        }

        render() {
            this.container.innerHTML = '';
        }

        getAnswerPayload() {
            return null;
        }

        disable() {
            this.submitted = true;
        }

        showCorrectAnswer(correctDetails) {
        }
    }

    class ClickAreaHandler extends BaseInteractionHandler {
        constructor(container, caseData, onAnswerChange) {
            super(container, caseData, onAnswerChange);
            this.clickCoord = null;
        }

        render() {
            super.render();
            const overlay = document.createElement('div');
            overlay.style.cssText = 'position: absolute; top:0; left:0; width:100%; height:100%; cursor: pointer;';
            overlay.addEventListener('click', (e) => {
                if (this.submitted) return;
                const rect = overlay.getBoundingClientRect();
                const x = ((e.clientX - rect.left) / rect.width) * 800;
                const y = ((e.clientY - rect.top) / rect.height) * 600;
                this.clickCoord = { x, y };

                this.drawMarker(x, y);
                if (this.onAnswerChange) this.onAnswerChange(this.clickCoord);
                SoundEffects.playClick();
            });
            this.container.appendChild(overlay);
        }

        drawMarker(x, y, isCorrect = false) {
            const existing = this.container.querySelector('.r3-marker');
            if (existing) existing.remove();

            const marker = document.createElement('div');
            marker.className = 'r3-marker' + (isCorrect ? ' correct-marker' : '');
            marker.style.left = (x / 800 * 100) + '%';
            marker.style.top = (y / 600 * 100) + '%';
            this.container.appendChild(marker);
        }

        getAnswerPayload() {
            return this.clickCoord;
        }

        showCorrectAnswer(correctDetails) {
            this.disable();
            if (correctDetails && correctDetails.x !== undefined && correctDetails.y !== undefined) {
                this.drawMarker(correctDetails.x, correctDetails.y, true);
            }
        }
    }

    class ImageHotspotHandler extends ClickAreaHandler {}

    class HighlightRegionHandler extends BaseInteractionHandler {
        constructor(container, caseData, onAnswerChange) {
            super(container, caseData, onAnswerChange);
            this.startPt = null;
            this.endPt = null;
            this.isDrawing = false;
            this.boxEl = null;
        }

        render() {
            super.render();
            const overlay = document.createElement('div');
            overlay.style.cssText = 'position: absolute; top:0; left:0; width:100%; height:100%; cursor: crosshair; user-select: none;';
            
            const handleStart = (clientX, clientY, rect) => {
                if (this.submitted) return;
                this.isDrawing = true;
                const startX = ((clientX - rect.left) / rect.width) * 800;
                const startY = ((clientY - rect.top) / rect.height) * 600;
                this.startPt = { x: startX, y: startY };
                this.endPt = { x: startX, y: startY };

                if (this.boxEl) this.boxEl.remove();
                this.boxEl = document.createElement('div');
                this.boxEl.className = 'r3-highlight-box';
                this.updateBoxDOM();
                this.container.appendChild(this.boxEl);
            };

            const handleMove = (clientX, clientY, rect) => {
                if (!this.isDrawing || this.submitted) return;
                const currentX = ((clientX - rect.left) / rect.width) * 800;
                const currentY = ((clientY - rect.top) / rect.height) * 600;
                this.endPt = { x: currentX, y: currentY };
                this.updateBoxDOM();
            };

            const handleEnd = () => {
                if (!this.isDrawing || this.submitted) return;
                this.isDrawing = false;
                if (this.onAnswerChange) this.onAnswerChange(this.getAnswerPayload());
            };

            overlay.addEventListener('mousedown', (e) => {
                const rect = overlay.getBoundingClientRect();
                handleStart(e.clientX, e.clientY, rect);
            });

            overlay.addEventListener('mousemove', (e) => {
                const rect = overlay.getBoundingClientRect();
                handleMove(e.clientX, e.clientY, rect);
            });

            window.addEventListener('mouseup', handleEnd);

            overlay.addEventListener('touchstart', (e) => {
                if (e.touches.length === 1) {
                    const rect = overlay.getBoundingClientRect();
                    handleStart(e.touches[0].clientX, e.touches[0].clientY, rect);
                    e.preventDefault();
                }
            });

            overlay.addEventListener('touchmove', (e) => {
                if (e.touches.length === 1) {
                    const rect = overlay.getBoundingClientRect();
                    handleMove(e.touches[0].clientX, e.touches[0].clientY, rect);
                    e.preventDefault();
                }
            });

            overlay.addEventListener('touchend', handleEnd);

            this.container.appendChild(overlay);
        }

        updateBoxDOM() {
            if (!this.boxEl || !this.startPt || !this.endPt) return;
            const x1 = Math.min(this.startPt.x, this.endPt.x);
            const y1 = Math.min(this.startPt.y, this.endPt.y);
            const x2 = Math.max(this.startPt.x, this.endPt.x);
            const y2 = Math.max(this.startPt.y, this.endPt.y);

            this.boxEl.style.left = (x1 / 800 * 100) + '%';
            this.boxEl.style.top = (y1 / 600 * 100) + '%';
            this.boxEl.style.width = ((x2 - x1) / 800 * 100) + '%';
            this.boxEl.style.height = ((y2 - y1) / 600 * 100) + '%';
        }

        getAnswerPayload() {
            if (!this.startPt || !this.endPt) return null;
            return {
                x1: Math.min(this.startPt.x, this.endPt.x),
                y1: Math.min(this.startPt.y, this.endPt.y),
                x2: Math.max(this.startPt.x, this.endPt.x),
                y2: Math.max(this.startPt.y, this.endPt.y)
            };
        }

        showCorrectAnswer(correctDetails) {
            this.disable();
            if (correctDetails && correctDetails.x1 !== undefined) {
                const cBox = document.createElement('div');
                cBox.className = 'r3-highlight-box correct-box';
                cBox.style.left = (correctDetails.x1 / 800 * 100) + '%';
                cBox.style.top = (correctDetails.y1 / 600 * 100) + '%';
                cBox.style.width = ((correctDetails.x2 - correctDetails.x1) / 800 * 100) + '%';
                cBox.style.height = ((correctDetails.y2 - correctDetails.y1) / 600 * 100) + '%';
                this.container.appendChild(cBox);
            }
        }
    }

    class DragDropHandler extends BaseInteractionHandler {
        constructor(container, caseData, onAnswerChange) {
            super(container, caseData, onAnswerChange);
            this.mapping = {};
        }

        render() {
            super.render();
            const dragContainer = document.createElement('div');
            dragContainer.className = 'r3-drag-container';

            const itemsContainer = document.createElement('div');
            itemsContainer.className = 'r3-drag-items';
            
            (this.caseData.items || []).forEach(item => {
                const itemEl = document.createElement('div');
                itemEl.className = 'r3-drag-item';
                itemEl.textContent = item.label;
                itemEl.draggable = true;
                itemEl.id = `drag-${item.id}`;
                itemEl.addEventListener('dragstart', (e) => {
                    if (this.submitted) { e.preventDefault(); return; }
                    e.dataTransfer.setData('text/plain', item.id);
                    itemEl.classList.add('dragging');
                });
                itemEl.addEventListener('dragend', () => {
                    itemEl.classList.remove('dragging');
                });
                itemsContainer.appendChild(itemEl);
            });

            const dropzonesContainer = document.createElement('div');
            dropzonesContainer.className = 'r3-dropzones';

            (this.caseData.targets || []).forEach(target => {
                const dropzone = document.createElement('div');
                dropzone.className = 'r3-dropzone';
                dropzone.id = `dropzone-${target.id}`;
                dropzone.innerHTML = `<div class="r3-dropzone-label">${target.label}</div>`;

                dropzone.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    if (!this.submitted) dropzone.classList.add('dragover');
                });

                dropzone.addEventListener('dragleave', () => {
                    dropzone.classList.remove('dragover');
                });

                dropzone.addEventListener('drop', (e) => {
                    e.preventDefault();
                    dropzone.classList.remove('dragover');
                    if (this.submitted) return;

                    const itemId = e.dataTransfer.getData('text/plain');
                    const itemEl = document.getElementById(`drag-${itemId}`);
                    if (itemEl) {
                        dropzone.appendChild(itemEl);
                        this.mapping[itemId] = target.id;
                        if (this.onAnswerChange) this.onAnswerChange(this.mapping);
                        SoundEffects.playClick();
                    }
                });

                dropzonesContainer.appendChild(dropzone);
            });

            dragContainer.appendChild(itemsContainer);
            dragContainer.appendChild(dropzonesContainer);
            this.container.appendChild(dragContainer);
        }

        getAnswerPayload() {
            return this.mapping;
        }

        showCorrectAnswer(correctDetails) {
            this.disable();
            if (correctDetails) {
                Object.entries(correctDetails).forEach(([itemId, targetId]) => {
                    const itemEl = document.getElementById(`drag-${itemId}`);
                    const dropzoneEl = document.getElementById(`dropzone-${targetId}`);
                    if (itemEl && dropzoneEl) {
                        dropzoneEl.appendChild(itemEl);
                        itemEl.draggable = false;
                        itemEl.style.borderColor = 'var(--success)';
                        itemEl.style.background = 'rgba(16, 185, 129, 0.1)';
                    }
                });
            }
        }
    }

    class ConnectObjectsHandler extends BaseInteractionHandler {
        constructor(container, caseData, onAnswerChange) {
            super(container, caseData, onAnswerChange);
            this.connections = {};
            this.selectedLeft = null;
            this.nodes = {};
        }

        render() {
            super.render();
            const connectContainer = document.createElement('div');
            connectContainer.className = 'r3-connect-container';

            const leftCol = document.createElement('div');
            leftCol.className = 'r3-connect-column left';
            const rightCol = document.createElement('div');
            rightCol.className = 'r3-connect-column right';

            (this.caseData.left_items || []).forEach(item => {
                const node = document.createElement('div');
                node.className = 'r3-connect-node';
                node.textContent = item.label;
                node.id = `node-${item.id}`;
                node.innerHTML += '<span class="r3-connect-dot"></span>';

                node.addEventListener('click', () => {
                    if (this.submitted) return;
                    SoundEffects.playClick();
                    if (this.selectedLeft) {
                        const prevNode = document.getElementById(`node-${this.selectedLeft}`);
                        if (prevNode) prevNode.classList.remove('selected');
                    }
                    this.selectedLeft = item.id;
                    node.classList.add('selected');
                });

                leftCol.appendChild(node);
                this.nodes[item.id] = node;
            });

            (this.caseData.right_items || []).forEach(item => {
                const node = document.createElement('div');
                node.className = 'r3-connect-node';
                node.textContent = item.label;
                node.id = `node-${item.id}`;
                node.innerHTML = '<span class="r3-connect-dot"></span>' + node.innerHTML;

                node.addEventListener('click', () => {
                    if (this.submitted || !this.selectedLeft) return;
                    SoundEffects.playClick();
                    
                    this.connections[this.selectedLeft] = item.id;
                    
                    const leftNode = document.getElementById(`node-${this.selectedLeft}`);
                    if (leftNode) leftNode.classList.remove('selected');
                    this.selectedLeft = null;

                    this.drawLines();
                    if (this.onAnswerChange) this.onAnswerChange(this.connections);
                });

                rightCol.appendChild(node);
                this.nodes[item.id] = node;
            });

            const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            svg.setAttribute('class', 'r3-connections-svg');
            this.svg = svg;

            connectContainer.appendChild(leftCol);
            connectContainer.appendChild(rightCol);
            this.container.appendChild(svg);
            this.container.appendChild(connectContainer);

            window.addEventListener('resize', () => this.drawLines());
            setTimeout(() => this.drawLines(), 100);
        }

        drawLines(correctAnswer = null) {
            if (!this.svg) return;
            this.svg.innerHTML = '';

            const rect = this.container.getBoundingClientRect();
            if (rect.width === 0) return;

            Object.entries(this.connections).forEach(([leftId, rightId]) => {
                const leftDot = this.nodes[leftId]?.querySelector('.r3-connect-dot');
                const rightDot = this.nodes[rightId]?.querySelector('.r3-connect-dot');

                if (leftDot && rightDot) {
                    const lRect = leftDot.getBoundingClientRect();
                    const rRect = rightDot.getBoundingClientRect();

                    const x1 = lRect.left + lRect.width / 2 - rect.left;
                    const y1 = lRect.top + lRect.height / 2 - rect.top;
                    const x2 = rRect.left + rRect.width / 2 - rect.left;
                    const y2 = rRect.top + rRect.height / 2 - rect.top;

                    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                    line.setAttribute('x1', x1);
                    line.setAttribute('y1', y1);
                    line.setAttribute('x2', x2);
                    line.setAttribute('y2', y2);

                    let cName = 'r3-connection-line';
                    if (correctAnswer) {
                        if (correctAnswer[leftId] === rightId) {
                            cName += ' correct';
                        } else {
                            cName += ' wrong';
                        }
                    }
                    line.setAttribute('class', cName);
                    this.svg.appendChild(line);
                }
            });
        }

        getAnswerPayload() {
            return this.connections;
        }

        showCorrectAnswer(correctDetails) {
            this.disable();
            if (correctDetails) {
                this.drawLines(correctDetails);
                Object.entries(correctDetails).forEach(([leftId, rightId]) => {
                    if (this.connections[leftId] !== rightId) {
                        this.connections[leftId] = rightId;
                    }
                });
                this.drawLines(correctDetails);
            }
        }
    }

    class TimelineOrderingHandler extends BaseInteractionHandler {
        constructor(container, caseData, onAnswerChange) {
            super(container, caseData, onAnswerChange);
            this.events = [...(this.caseData.events || [])];
        }

        render() {
            super.render();
            const timelineContainer = document.createElement('div');
            timelineContainer.className = 'r3-timeline-container';

            const listEl = document.createElement('div');
            listEl.className = 'r3-timeline-list';
            this.listEl = listEl;

            this.renderListItems();
            timelineContainer.appendChild(listEl);
            this.container.appendChild(timelineContainer);
        }

        renderListItems(correctAnswer = null) {
            if (!this.listEl) return;
            this.listEl.innerHTML = '';

            this.events.forEach((ev, idx) => {
                const item = document.createElement('div');
                item.className = 'r3-timeline-item';
                if (correctAnswer && correctAnswer[idx] === ev.id) {
                    item.className += ' correct-item';
                }
                item.textContent = `${idx + 1}. ${ev.label}`;

                const controls = document.createElement('div');
                controls.className = 'r3-item-controls';

                const btnUp = document.createElement('button');
                btnUp.className = 'r3-btn-arrow';
                btnUp.textContent = '▲';
                btnUp.disabled = this.submitted || idx === 0;
                btnUp.addEventListener('click', () => {
                    SoundEffects.playClick();
                    const temp = this.events[idx - 1];
                    this.events[idx - 1] = this.events[idx];
                    this.events[idx] = temp;
                    this.renderListItems();
                    if (this.onAnswerChange) this.onAnswerChange(this.getAnswerPayload());
                });

                const btnDown = document.createElement('button');
                btnDown.className = 'r3-btn-arrow';
                btnDown.textContent = '▼';
                btnDown.disabled = this.submitted || idx === this.events.length - 1;
                btnDown.addEventListener('click', () => {
                    SoundEffects.playClick();
                    const temp = this.events[idx + 1];
                    this.events[idx + 1] = this.events[idx];
                    this.events[idx] = temp;
                    this.renderListItems();
                    if (this.onAnswerChange) this.onAnswerChange(this.getAnswerPayload());
                });

                controls.appendChild(btnUp);
                controls.appendChild(btnDown);
                item.appendChild(controls);
                this.listEl.appendChild(item);
            });
        }

        getAnswerPayload() {
            return this.events.map(ev => ev.id);
        }

        showCorrectAnswer(correctDetails) {
            this.disable();
            if (correctDetails) {
                const sorted = [];
                correctDetails.forEach(id => {
                    const ev = this.events.find(e => e.id === id);
                    if (ev) sorted.push(ev);
                });
                this.events = sorted;
                this.renderListItems(correctDetails);
            }
        }
    }

    class TextInputHandler extends BaseInteractionHandler {
        constructor(container, caseData, onAnswerChange) {
            super(container, caseData, onAnswerChange);
            this.textVal = '';
        }

        render() {
            super.render();
            const inputContainer = document.createElement('div');
            inputContainer.className = 'r3-text-input-container';

            const field = document.createElement('input');
            field.type = 'text';
            field.className = 'r3-text-field';
            field.placeholder = 'Nhập mật mã/đáp án trinh thám...';
            field.id = 'r3-input-field';
            
            field.addEventListener('input', (e) => {
                this.textVal = e.target.value;
                if (this.onAnswerChange) this.onAnswerChange(this.textVal);
            });

            inputContainer.appendChild(field);
            this.container.appendChild(inputContainer);
        }

        getAnswerPayload() {
            return this.textVal;
        }

        showCorrectAnswer(correctDetails) {
            this.disable();
            const field = document.getElementById('r3-input-field');
            if (field && correctDetails) {
                field.disabled = true;
                field.value = correctDetails;
                field.style.borderColor = 'var(--success)';
                field.style.color = 'var(--success)';
                field.style.background = 'rgba(16, 185, 129, 0.05)';
            }
        }
    }

    class MultipleHotspotsHandler extends BaseInteractionHandler {
        constructor(container, caseData, onAnswerChange) {
            super(container, caseData, onAnswerChange);
            this.clickedPts = [];
        }

        render() {
            super.render();
            const counter = document.createElement('div');
            counter.className = 'r3-hotspots-counter';
            counter.id = 'r3-hotspots-counter';
            counter.textContent = `Đã chọn: 0 / ${this.caseData.hotspots ? this.caseData.hotspots.length : 3}`;
            this.container.appendChild(counter);

            const overlay = document.createElement('div');
            overlay.style.cssText = 'position: absolute; top:0; left:0; width:100%; height:100%; cursor: pointer;';
            overlay.addEventListener('click', (e) => {
                if (this.submitted) return;
                const rect = overlay.getBoundingClientRect();
                const x = ((e.clientX - rect.left) / rect.width) * 800;
                const y = ((e.clientY - rect.top) / rect.height) * 600;

                SoundEffects.playClick();
                this.addMarker(x, y);
                if (this.onAnswerChange) this.onAnswerChange(this.getAnswerPayload());
            });
            this.container.appendChild(overlay);
        }

        addMarker(x, y, isCorrect = false) {
            const marker = document.createElement('div');
            marker.className = 'r3-marker' + (isCorrect ? ' correct-marker' : '');
            marker.style.left = (x / 800 * 100) + '%';
            marker.style.top = (y / 600 * 100) + '%';
            
            if (!isCorrect && !this.submitted) {
                marker.style.pointerEvents = 'auto';
                marker.addEventListener('click', (e) => {
                    e.stopPropagation();
                    if (this.submitted) return;
                    marker.remove();
                    this.clickedPts = this.clickedPts.filter(pt => pt.x !== x || pt.y !== y);
                    this.updateCounter();
                    if (this.onAnswerChange) this.onAnswerChange(this.getAnswerPayload());
                });
            }

            this.clickedPts.push({ x, y });
            this.container.appendChild(marker);
            this.updateCounter();
        }

        updateCounter() {
            const counter = document.getElementById('r3-hotspots-counter');
            if (counter) {
                const total = this.caseData.hotspots ? this.caseData.hotspots.length : 3;
                const count = this.container.querySelectorAll('.r3-marker:not(.correct-marker)').length;
                counter.textContent = `Đã chọn: ${count} / ${total}`;
            }
        }

        getAnswerPayload() {
            const markers = this.container.querySelectorAll('.r3-marker:not(.correct-marker)');
            const coords = [];
            markers.forEach(m => {
                const x = parseFloat(m.style.left) / 100 * 800;
                const y = parseFloat(m.style.top) / 100 * 600;
                coords.push({ x, y });
            });
            return coords;
        }

        showCorrectAnswer(correctDetails) {
            this.disable();
            this.container.querySelectorAll('.r3-marker:not(.correct-marker)').forEach(m => m.remove());
            
            if (correctDetails && correctDetails.hotspots) {
                correctDetails.hotspots.forEach(h => {
                    const marker = document.createElement('div');
                    marker.className = 'r3-marker correct-marker';
                    marker.style.left = (h.x / 800 * 100) + '%';
                    marker.style.top = (h.y / 600 * 100) + '%';
                    this.container.appendChild(marker);
                });
            }
        }
    }

    // ── Sequence Builder Handler (Vòng 4) ──
    class SequenceBuilderHandler extends BaseInteractionHandler {
        constructor(container, caseData, onAnswerChange) {
            super(container, caseData, onAnswerChange);
            this.events = [...(caseData.events || [])];
            for (let i = this.events.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [this.events[i], this.events[j]] = [this.events[j], this.events[i]];
            }
        }

        render() {
            super.render();
            const wrapper = document.createElement('div');
            wrapper.className = 'r4-sequence-container';
            this.listEl = wrapper;
            this.renderItems();
            this.container.appendChild(wrapper);
        }

        renderItems() {
            this.listEl.innerHTML = '';
            this.events.forEach((ev, idx) => {
                const item = document.createElement('div');
                item.className = 'r4-sequence-item';
                item.innerHTML = `
                    <span>${idx + 1}. ${ev.label}</span>
                    <span class="r3-timeline-arrows">
                        <button class="r3-btn-arrow" data-dir="up" data-idx="${idx}" ${idx === 0 ? 'disabled' : ''}>▲</button>
                        <button class="r3-btn-arrow" data-dir="down" data-idx="${idx}" ${idx === this.events.length - 1 ? 'disabled' : ''}>▼</button>
                    </span>`;
                this.listEl.appendChild(item);
            });
            this.listEl.querySelectorAll('.r3-btn-arrow').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    if (this.submitted) return;
                    const i = parseInt(e.target.dataset.idx);
                    const dir = e.target.dataset.dir;
                    if (dir === 'up' && i > 0) {
                        [this.events[i], this.events[i - 1]] = [this.events[i - 1], this.events[i]];
                    } else if (dir === 'down' && i < this.events.length - 1) {
                        [this.events[i], this.events[i + 1]] = [this.events[i + 1], this.events[i]];
                    }
                    this.renderItems();
                    if (this.onAnswerChange) this.onAnswerChange(this.getAnswerPayload());
                });
            });
        }

        getAnswerPayload() {
            return this.events.map(e => e.id);
        }

        showCorrectAnswer(correctDetails) {
            this.disable();
            if (Array.isArray(correctDetails)) {
                const correctMap = {};
                correctDetails.forEach((id, i) => correctMap[id] = i);
                this.listEl.querySelectorAll('.r4-sequence-item').forEach(item => {
                    const idx = parseInt(item.querySelector('span').textContent);
                    const evId = this.events[idx - 1]?.id;
                    if (evId && correctMap[evId] === idx - 1) {
                        item.classList.add('correct-item');
                    }
                });
            }
        }
    }

    // ── Image Comparison Handler (Vòng 4) ──
    class ImageComparisonHandler extends BaseInteractionHandler {
        constructor(container, caseData, onAnswerChange) {
            super(container, caseData, onAnswerChange);
            this.clickCoord = null;
            this.modView = null;
        }

        render() {
            super.render();
            const comp = document.createElement('div');
            comp.className = 'r4-comparison-container';

            // Left: original
            const origPanel = document.createElement('div');
            origPanel.className = 'r4-comparison-panel';
            origPanel.innerHTML = `<div class="r4-comparison-label">Bản gốc</div>
                <div class="r4-comparison-view"><img src="/static/images/${this.caseData.image_left || this.caseData.image}" alt="Original" /></div>`;

            // Right: modified (clickable)
            const modPanel = document.createElement('div');
            modPanel.className = 'r4-comparison-panel';
            const label = document.createElement('div');
            label.className = 'r4-comparison-label';
            label.textContent = 'Bản đã sửa đổi';
            modPanel.appendChild(label);

            const view = document.createElement('div');
            view.className = 'r4-comparison-view';
            view.style.cursor = 'crosshair';
            view.style.position = 'relative';
            const img = document.createElement('img');
            img.src = `/static/images/${this.caseData.image_right || this.caseData.image}`;
            view.appendChild(img);

            view.addEventListener('click', (e) => {
                if (this.submitted) return;
                const rect = view.getBoundingClientRect();
                const x = Math.round((e.clientX - rect.left) / rect.width * 800);
                const y = Math.round((e.clientY - rect.top) / rect.height * 600);
                this.clickCoord = { x, y };
                this.drawMarker(view, x, y);
                if (this.onAnswerChange) this.onAnswerChange(this.clickCoord);
                SoundEffects.playClick();
            });

            modPanel.appendChild(view);
            comp.appendChild(origPanel);
            comp.appendChild(modPanel);
            this.container.appendChild(comp);
            this.modView = view;
        }

        drawMarker(view, x, y, isCorrect = false) {
            const existing = view.querySelector('.r3-marker');
            if (existing) existing.remove();
            const marker = document.createElement('div');
            marker.className = 'r3-marker' + (isCorrect ? ' correct-marker' : '');
            marker.style.left = (x / 800 * 100) + '%';
            marker.style.top = (y / 600 * 100) + '%';
            marker.style.position = 'absolute';
            view.appendChild(marker);
        }

        getAnswerPayload() { return this.clickCoord; }

        showCorrectAnswer(correctDetails) {
            this.disable();
            if (correctDetails && correctDetails.x !== undefined && this.modView) {
                this.drawMarker(this.modView, correctDetails.x, correctDetails.y, true);
            }
        }
    }

    // Initialization
    function init() {
        setupSocket();
        setupLobbyUI();
        setupGameListeners();
    }

    function setupSocket() {
        socket = io({
            reconnectionAttempts: 5,
            reconnectionDelay: 1000
        });

        socket.on('connect', () => {
            console.log('Connected to server');
            socket.emit('join_room', { 
                room_code: window.GAME_CONFIG.roomCode,
                avatar: myAvatar,
                name: window.GAME_CONFIG.playerName || window.CURRENT_USER.username || 'Người chơi',
                team: window.GAME_CONFIG.playerTeam
            });
        });

        socket.on('player_list_update', (players) => {
            currentPlayers = players;
            updatePlayerList(players);
            updateLeaderboard(players);
            updateMyTeamState(players);
            
            // Host có thể bắt đầu khi tất cả người chơi (kể cả host) đã chọn đội và sẵn sàng
            if (window.GAME_CONFIG.isHost) {
                const allReady = players.length > 0 && players.every(p => p.ready && p.team);
                if (allReady) {
                    btnStart.classList.remove('hidden');
                } else {
                    btnStart.classList.add('hidden');
                }
            }
        });

        socket.on('team_list_update', (teams) => {
            updateTeamGrid(teams);
        });

        socket.on('settings_updated', (data) => {
            if (!window.GAME_CONFIG.isHost) {
                if (data.tournament_mode !== undefined) {
                    myTournamentMode = Boolean(data.tournament_mode);
                    tournamentMode = myTournamentMode;
                    updateModeUI(myTournamentMode);
                }
            }
        });

        socket.on('round_started', (data) => {
            tournamentMode = true;
            currentRound = data.round;
            currentTimeLimit = data.time_per_question || 20;
            isEliminated = myTeam ? !(data.teams_active || []).includes(myTeam) : false;
            updateRoundUI(data);
            if (isEliminated) {
                showToast('Đội của bạn đã bị loại. Bạn có thể theo dõi các vòng tiếp theo.', 'info');
            }
        });

        socket.on('round_end', (data) => {
            if (data.is_final) return;
            showRoundBreakSummary(data);
        });

        socket.on('round_break', (data) => {
            showScreen('break');
            breakTitle.textContent = `Kết quả ${TOURNAMENT_ROUNDS[data.completed_round]?.name || 'vòng ' + data.completed_round}`;
            breakSubtitle.textContent = data.next_round_description || '';
            updateBreakCountdown(data.break_seconds);
            renderBreakRankings(data.team_rankings || []);
            renderBreakTeams(data.active_teams || [], breakAdvancing, 'advancing');
            renderBreakTeams(data.eliminated_teams || [], breakEliminated, 'eliminated');
        });

        socket.on('break_tick', (data) => {
            updateBreakCountdown(data.remaining);
        });

        socket.on('tournament_over', (data) => {
            displayTournamentResults(data);
            Confetti.burst();
            setTimeout(() => Confetti.burst(), 500);
            setTimeout(() => Confetti.burst(), 1000);
        });

        socket.on('force_redirect', (data) => {
            window.location.href = data.url || '/';
        });

        socket.on('show_scene', (data) => {
            showSceneIntro(data);
        });

        socket.on('game_started', (data) => {
            stopSceneCountdown();
            const shouldShowRoundIntro = Boolean(data.tournament_mode) && data.round;
            if (shouldShowRoundIntro) {
                showRoundIntro(data);
            } else {
                showScreen('game');
                document.querySelector('.game-layout')?.classList.remove('hidden');
                document.getElementById('host-dashboard')?.classList.add('hidden');
            }
            tournamentMode = Boolean(data.tournament_mode);
            if (data.round) {
                currentRound = data.round;
                updateRoundUI(data);
            } else if (gameRoundInfo) {
                gameRoundInfo.classList.add('hidden');
            }
            // Reset lifelines based on server config
            const lifelines = (data && data.lifelines) ? data.lifelines : [];
            currentLifelines = {
                fifty_fifty: lifelines.includes('fifty_fifty'),
                hint: lifelines.includes('hint')
            };
            if (!currentLifelines.fifty_fifty) {
                btn5050.disabled = true;
                btn5050.style.opacity = '0.3';
                btn5050.title = 'Không khả dụng';
            }
            if (!currentLifelines.hint) {
                btnHint.disabled = true;
                btnHint.style.opacity = '0.3';
                btnHint.title = 'Không khả dụng';
            }
        });

        socket.on('new_question', (data) => {
            stopRoundIntroCountdown();
            showScreen('game');
            hasAnswered = false;
            
            currentAnswersProgress = currentPlayers.map(p => ({
                sid: p.sid,
                name: p.username,
                team: p.team,
                answered: false
            }));

            const isRound3 = Number(data.round) === 3;
            
            if (isRound3) {
                round3GameLayout.classList.remove('hidden');
                document.querySelector('.game-layout').classList.add('hidden');
                
                r3CaseTitle.textContent = data.title || "Vụ Án Trinh Thám";
                r3Instruction.textContent = data.question || "";
                r3CaseImage.src = `/static/images/${data.image}`;
                r3Timer.textContent = data.time_per_question || 30;
                
                btnR3Submit.classList.remove('hidden');
                btnR3Submit.disabled = false;
                btnR3Next.classList.add('hidden');

                if (r3InteractionLayer) {
                    const type = data.type;
                    if (type === 'click') {
                        r3CurrentHandler = new ClickAreaHandler(r3InteractionLayer, data, () => {});
                    } else if (type === 'image_hotspot') {
                        r3CurrentHandler = new ImageHotspotHandler(r3InteractionLayer, data, () => {});
                    } else if (type === 'highlight') {
                        r3CurrentHandler = new HighlightRegionHandler(r3InteractionLayer, data, () => {});
                    } else if (type === 'drag_drop') {
                        r3CurrentHandler = new DragDropHandler(r3InteractionLayer, data, () => {});
                    } else if (type === 'connect') {
                        r3CurrentHandler = new ConnectObjectsHandler(r3InteractionLayer, data, () => {});
                    } else if (type === 'timeline') {
                        r3CurrentHandler = new TimelineOrderingHandler(r3InteractionLayer, data, () => {});
                    } else if (type === 'text_input') {
                        r3CurrentHandler = new TextInputHandler(r3InteractionLayer, data, () => {});
                    } else if (type === 'multiple_hotspots') {
                        r3CurrentHandler = new MultipleHotspotsHandler(r3InteractionLayer, data, () => {});
                    } else if (type === 'sequence_builder') {
                        r3CurrentHandler = new SequenceBuilderHandler(r3InteractionLayer, data, () => {});
                    } else if (type === 'image_comparison') {
                        r3CurrentHandler = new ImageComparisonHandler(r3InteractionLayer, data, () => {});
                    } else {
                        r3CurrentHandler = null;
                        r3InteractionLayer.innerHTML = '';
                    }
                    if (r3CurrentHandler) r3CurrentHandler.render();
                }
            } else {
                round3GameLayout.classList.add('hidden');
                document.querySelector('.game-layout')?.classList.remove('hidden');
                displayQuestion(data);
            }

            if (window.GAME_CONFIG.isHost) {
                document.getElementById('host-dashboard')?.classList.add('hidden');
                updateHostProgressDashboard();
            }
        });

        socket.on('reading_tick', (data) => {
            const remaining = Number(data.remaining || 0);
            gameTimer.textContent = remaining;
            gameTimer.classList.remove('danger');
            gameTimer.classList.add('warning');
            if (qArticle) {
                qArticle.textContent = `Đọc câu hỏi: ${remaining}s`;
            }
        });

        socket.on('answer_phase_started', (data) => {
            isAnswerLocked = false;
            currentTimeLimit = Number(data.seconds || 5);
            gameTimer.textContent = currentTimeLimit;
            gameTimer.classList.remove('warning');
            document.querySelectorAll('.answer-btn').forEach(btn => {
                btn.classList.remove('disabled');
                btn.disabled = false;
            });
            if (qArticle) {
                qArticle.textContent = 'Chọn đáp án';
            }
        });

        socket.on('timer_tick', (timeLeft) => {
            gameTimer.textContent = timeLeft;
            if (r3Timer) r3Timer.textContent = timeLeft;
            SoundEffects.playTick();
            if (timeLeft <= 5) {
                gameTimer.classList.add('danger');
                if (r3Timer) r3Timer.classList.add('danger');
            } else {
                gameTimer.classList.remove('danger');
                gameTimer.classList.remove('warning');
                if (r3Timer) r3Timer.classList.remove('danger');
            }
        });

        socket.on('answer_result', (data) => {
            const isRound3 = data.round === 3 || (currentRound === 3);

            if (isRound3) {
                // Round 3 detective result - correct/wrong notifications and explanation popups removed
                btnR3Submit.classList.add('hidden');
                if (window.GAME_CONFIG.isHost) {
                    btnR3Next.classList.remove('hidden');
                }
                return;
            }

            // Normal rounds
            if (!data.correct_answer) return;
            const correctLetter = data.correct_answer.toLowerCase();
            const correctIdx = ['a', 'b', 'c', 'd'].indexOf(correctLetter);
            
            const btns = document.querySelectorAll('.answer-btn');
            let mySelectedIdx = -1;
            
            btns.forEach(btn => {
                const idx = parseInt(btn.dataset.idx);
                if (btn.classList.contains('selected')) {
                    mySelectedIdx = idx;
                }
                
                if (idx === correctIdx) {
                    btn.classList.add('correct');
                }
            });

            if (mySelectedIdx !== -1 && mySelectedIdx !== correctIdx) {
                const myBtn = document.querySelector(`.answer-btn[data-idx="${mySelectedIdx}"]`);
                if (myBtn) myBtn.classList.add('wrong');
            }

            const isCorrect = (mySelectedIdx === correctIdx);
            
            if (isCorrect) {
                SoundEffects.playCorrect();
                Confetti.burst();
            } else {
                SoundEffects.playWrong();
            }

            // Show explanation
            expTitle.textContent = isCorrect ? "✅ Chính xác!" : "❌ Sai rồi!";
            expText.textContent = data.explanation;
            expPopup.className = `explanation-popup show ${isCorrect ? 'correct' : 'wrong'}`;
        });

        socket.on('streak_update', (data) => {
            if (data.is_correct) {
                streakDisplay.classList.remove('streak-wrong');
                streakDisplay.classList.add('streak-correct');
                if (data.streak >= 3) {
                    SoundEffects.playStreak();
                }
            } else {
                streakDisplay.classList.remove('streak-correct');
                streakDisplay.classList.add('streak-wrong');
            }
            streakCount.textContent = data.streak;
            if (r3Streak) r3Streak.textContent = data.streak;
            if (data.new_badges && data.new_badges.length > 0) {
                showBadgeUnlock(data.new_badges[0]);
            }
        });

        socket.on('fifty_fifty_result', (data) => {
            if (data.remove_options) {
                data.remove_options.forEach(letter => {
                    const idx = ['a', 'b', 'c', 'd'].indexOf(letter);
                    const btn = document.querySelector(`.answer-btn[data-idx="${idx}"]`);
                    if (btn) {
                        btn.classList.add('eliminated');
                        btn.style.opacity = '0.2';
                        btn.style.pointerEvents = 'none';
                    }
                });
                currentLifelines.fifty_fifty = false;
                btn5050.disabled = true;
            }
        });

        socket.on('hint_result', (data) => {
            if (data.hint) {
                hintText.textContent = data.hint;
                hintPopup.classList.remove('hidden');
                setTimeout(() => hintPopup.classList.add('hidden'), 7000);
                currentLifelines.hint = false;
                btnHint.disabled = true;
            }
        });

        socket.on('leaderboard_update', (data) => {
            if (data.players) {
                updateLeaderboard(data.players, data.team_rankings);
                
                const me = data.players.find(p => p.sid === socket.id);
                if (me) {
                    if (r3Score) r3Score.textContent = me.score || 0;
                }
                
                if (data.team_rankings && myTeam) {
                    const myTeamRankIdx = data.team_rankings.findIndex(t => Number(t.team) === Number(myTeam));
                    if (myTeamRankIdx !== -1) {
                        if (r3Rank) r3Rank.textContent = myTeamRankIdx + 1;
                        if (r3MyTeam) r3MyTeam.textContent = `Đội ${myTeam}`;
                        const teamData = data.team_rankings[myTeamRankIdx];
                        if (r3Score && teamData) r3Score.textContent = teamData.score || 0;
                    }
                } else if (data.players) {
                    const sortedPlayers = [...data.players].sort((a,b) => b.score - a.score);
                    const myRankIdx = sortedPlayers.findIndex(p => p.sid === socket.id);
                    if (myRankIdx !== -1 && r3Rank) {
                        r3Rank.textContent = myRankIdx + 1;
                    }
                }
            }
        });

        socket.on('game_over', (data) => {
            if (tournamentMode) return;
            // final_scores is a sorted list from server
            const leaderboard = data.final_scores || [];
            // find my own entry
            const me = leaderboard.find(p => p.name === window.CURRENT_USER.username);
            const teamLeaderboard = buildTeamLeaderboard(leaderboard);
            const myTeamResult = myTeam ? teamLeaderboard.find(t => t.team === myTeam) : null;
            const myStats = {
                score: myTeamResult ? myTeamResult.score : (me ? me.score : 0),
                correct_answers: me ? (me.score > 0 ? '?' : 0) : 0,
                max_streak: me ? me.best_streak : 0
            };
            displayResults(teamLeaderboard.length ? teamLeaderboard : leaderboard, myStats);
            Confetti.burst();
            setTimeout(() => Confetti.burst(), 500);
        });

        socket.on('answers_progress_update', (data) => {
            currentAnswersProgress = data.progress || [];
            if (window.GAME_CONFIG.isHost) {
                updateHostProgressDashboard();
            }
        });

        socket.on('game_reset', () => {
            isReady = false;
            hasAnswered = false;
            isEliminated = false;
            
            if (btnReady) {
                btnReady.textContent = "Sẵn sàng";
                btnReady.className = "btn btn-primary btn-block btn-lg mt-2";
                btnReady.disabled = !myTeam;
            }
            
            if (expPopup) expPopup.classList.remove('show');
            if (hintPopup) hintPopup.classList.add('hidden');
            
            showScreen('lobby');
            showToast('Trò chơi đã được quản trị viên reset.', 'warning');
        });

        // ══════════════════════════════════════════════════════════
        // ROUND 4 — CYBER INCIDENT RESPONSE SOCKET LISTENERS
        // ══════════════════════════════════════════════════════════

        socket.on('new_round4_mission', (data) => {
            // Show Round 4 layout, hide others
            if (round4GameLayout) round4GameLayout.classList.remove('hidden');
            if (round3GameLayout) round3GameLayout.classList.add('hidden');
            document.querySelector('.game-layout')?.classList.add('hidden');

            // Top bar
            if (r4IncidentTitle) r4IncidentTitle.textContent = data.incident_title || 'Sự cố';
            if (r4ActiveTeam) r4ActiveTeam.textContent = `Đội ${myTeam}`;
            if (r4CurrentMissionIndex) r4CurrentMissionIndex.textContent = data.mission_index || 1;
            if (r4Timer) {
                r4Timer.textContent = data.time_limit || 20;
                r4Timer.classList.remove('danger');
            }

            // Instruction
            if (r4Instruction) r4Instruction.textContent = data.instruction || '';

            // Image
            if (r4CaseImage) r4CaseImage.src = `/static/images/${data.image || ''}`;

            // Active player
            r4ActivePlayerSid = data.active_player_sid;
            r4HintUsed = false;
            const iAmActive = (socket.id === r4ActivePlayerSid);

            // Spectator overlay
            if (r4SpectatorOverlay) {
                if (iAmActive) {
                    r4SpectatorOverlay.classList.add('hidden');
                } else {
                    r4SpectatorOverlay.classList.remove('hidden');
                    if (r4ActivePlayerNameOverlay) {
                        r4ActivePlayerNameOverlay.textContent = data.active_player_name || '...';
                    }
                }
            }

            // Buttons
            if (btnR4Submit) {
                btnR4Submit.classList.toggle('hidden', !iAmActive);
                btnR4Submit.disabled = false;
            }
            if (btnR4Hint) {
                btnR4Hint.classList.toggle('hidden', !iAmActive);
                btnR4Hint.disabled = false;
                btnR4Hint.textContent = 'Gợi ý';
            }

            // Team score
            if (r4TeamScore) r4TeamScore.textContent = data.team_score || 0;

            // Teammate progress (left panel)
            renderR4TeammateList(data.teammate_progress || []);

            // Opponent progress (right panel)
            renderR4OpponentProgress(data.opponent_progress);

            // Interaction handler
            r4CurrentHandler = null;
            if (r4InteractionLayer) {
                r4InteractionLayer.innerHTML = '';
                const type = data.type;
                const handlerContainer = r4InteractionLayer;
                const onAnswerChange = () => {};

                if (type === 'click') {
                    r4CurrentHandler = new ClickAreaHandler(handlerContainer, data, onAnswerChange);
                } else if (type === 'image_hotspot') {
                    r4CurrentHandler = new ImageHotspotHandler(handlerContainer, data, onAnswerChange);
                } else if (type === 'highlight') {
                    r4CurrentHandler = new HighlightRegionHandler(handlerContainer, data, onAnswerChange);
                } else if (type === 'drag_drop') {
                    r4CurrentHandler = new DragDropHandler(handlerContainer, data, onAnswerChange);
                } else if (type === 'connect') {
                    r4CurrentHandler = new ConnectObjectsHandler(handlerContainer, data, onAnswerChange);
                } else if (type === 'timeline') {
                    r4CurrentHandler = new TimelineOrderingHandler(handlerContainer, data, onAnswerChange);
                } else if (type === 'text_input') {
                    r4CurrentHandler = new TextInputHandler(handlerContainer, data, onAnswerChange);
                } else if (type === 'multiple_hotspots') {
                    r4CurrentHandler = new MultipleHotspotsHandler(handlerContainer, data, onAnswerChange);
                } else if (type === 'sequence_builder') {
                    r4CurrentHandler = new SequenceBuilderHandler(handlerContainer, data, onAnswerChange);
                } else if (type === 'image_comparison') {
                    r4CurrentHandler = new ImageComparisonHandler(handlerContainer, data, onAnswerChange);
                }

                if (r4CurrentHandler) {
                    r4CurrentHandler.render();
                    if (!iAmActive) {
                        r4CurrentHandler.disable();
                    }
                }
            }

            // Host vẫn chơi vòng 4 như người chơi thường
        });

        socket.on('round4_timer_tick', (data) => {
            const remaining = Number(data.remaining || 0);
            if (r4Timer) {
                r4Timer.textContent = remaining;
                if (remaining <= 5) {
                    r4Timer.classList.add('danger');
                } else {
                    r4Timer.classList.remove('danger');
                }
            }
            SoundEffects.playTick();
        });

        socket.on('round4_mission_result', (data) => {
            const score = data.score || 0;

            // Update team score
            const currentScore = parseInt(r4TeamScore?.textContent || '0');
            if (r4TeamScore) r4TeamScore.textContent = currentScore + score;

            // Disable controls
            if (btnR4Submit) btnR4Submit.disabled = true;
            if (btnR4Hint) btnR4Hint.disabled = true;
        });

        socket.on('round4_hint_result', (data) => {
            showToast(`💡 Gợi ý NV${data.mission_index}: ${data.hint}`, 'info', 5000);
        });

        socket.on('round4_game_over', (data) => {
            if (round4GameLayout) round4GameLayout.classList.add('hidden');

            const rankings = data.rankings || [];
            const champion = data.champion_team;
            const mvp = data.mvp || {};

            // Show winner banner
            if (tournamentWinnerBanner) tournamentWinnerBanner.classList.remove('hidden');
            if (winnerTeamName) winnerTeamName.textContent = `Đội ${champion}`;
            if (mvpPlayerName) mvpPlayerName.textContent = `${mvp.avatar || '🏆'} ${mvp.name || ''}`;
            if (mvpPlayerScore) mvpPlayerScore.textContent = `${mvp.score || 0} điểm`;

            showScreen('results');

            // Build results display
            if (podium) {
                podium.innerHTML = '';
                rankings.forEach((team, idx) => {
                    const medals = ['🥇', '🥈', '🥉'];
                    const medal = medals[idx] || `#${idx + 1}`;
                    const card = document.createElement('div');
                    card.className = `podium-card ${idx === 0 ? 'champion' : ''}`;
                    const membersHTML = (team.members || [])
                        .map(m => `<span class="r4-member-badge">${m.avatar || '👤'} ${m.name}: ${m.score}đ</span>`)
                        .join(' ');
                    card.innerHTML = `
                        <div class="podium-medal">${medal}</div>
                        <div class="podium-team">${team.name}</div>
                        <div class="podium-score">${team.score} điểm</div>
                        <div class="podium-stats">
                            <span>Chính xác: ${team.accuracy?.toFixed(0) || 0}%</span>
                            <span>TB thời gian: ${team.avg_time?.toFixed(1) || 0}s</span>
                            <span>NV hoàn hảo: ${team.perfect_missions || 0}/5</span>
                        </div>
                        <div class="podium-members">${membersHTML}</div>
                    `;
                    podium.appendChild(card);
                });
            }

            if (resScore) resScore.textContent = rankings.find(r => r.team === myTeam)?.score || 0;
            if (resCorrect) resCorrect.textContent = rankings.find(r => r.team === myTeam)?.perfect_missions || 0;

            displayTeamRankings(rankings);
            startAutoRedirectCountdown(15);

            Confetti.burst();
            setTimeout(() => Confetti.burst(), 600);
            setTimeout(() => Confetti.burst(), 1200);
        });

        socket.on('host_round4_update', (data) => {
            if (!window.GAME_CONFIG.isHost) return;
            const hostR4Title = document.getElementById('host-r4-incident-title');
            const hostR4Progress = document.getElementById('host-r4-teams-progress');
            if (hostR4Title) hostR4Title.textContent = data.incident_title || '';
            if (hostR4Progress) {
                hostR4Progress.innerHTML = '';
                const states = data.team_states || {};
                for (const [teamId, ts] of Object.entries(states)) {
                    const card = document.createElement('div');
                    card.className = 'host-team-progress-card';
                    const missionDots = (ts.scores || []).map((s, i) => {
                        let cls = 'waiting';
                        if (i < (ts.current_mission - 1)) cls = s > 0 ? 'correct' : 'wrong';
                        else if (i === (ts.current_mission - 1)) cls = 'current';
                        return `<span class="r4-dot ${cls}">NV${i+1}</span>`;
                    }).join('');
                    card.innerHTML = `
                        <div class="host-team-progress-header">
                            <span class="host-team-name">Đội ${teamId} ${ts.completed ? '✅' : ''}</span>
                            <span class="host-team-score">${ts.score} điểm</span>
                        </div>
                        <div class="host-team-members-progress">
                            <span>NV: ${ts.current_mission}/5 | Đang chơi: ${ts.active_player}</span>
                        </div>
                        <div style="display:flex;gap:6px;margin-top:6px">${missionDots}</div>
                    `;
                    hostR4Progress.appendChild(card);
                }
            }
            // Make host R4 section visible
            const hostR4Section = document.getElementById('host-round4-section');
            if (hostR4Section) hostR4Section.classList.remove('hidden');
        });

        socket.on('error', (data) => {
            const msg = typeof data === 'string' ? data : (data.message || 'Lỗi không xác định');
            showToast(msg, 'error');
            if (btnStart) {
                btnStart.disabled = false;
                btnStart.textContent = 'Bắt đầu Game';
            }
        });
    }

    // Lobby UI Setup
    function setupLobbyUI() {
        // Avatars
        const avatarContainer = document.getElementById('avatar-selector');
        window.GAME_CONFIG.avatars.forEach((emoji, i) => {
            const el = document.createElement('div');
            el.className = `avatar-option ${i === 0 ? 'selected' : ''}`;
            el.innerHTML = `<div class="avatar-emoji">${emoji}</div>`;
            el.addEventListener('click', () => {
                SoundEffects.playClick();
document.querySelectorAll('.avatar-option').forEach(e => e.classList.remove('selected'));
                el.classList.add('selected');
                myAvatar = emoji;
                if(socket && socket.connected) {
                    socket.emit('update_avatar', { avatar: myAvatar });
                }
            });
            avatarContainer.appendChild(el);
        });
        myAvatar = window.GAME_CONFIG.avatars[0];

        if (window.GAME_CONFIG.playerTeam) {
            myTeam = Number(window.GAME_CONFIG.playerTeam);
            if (selectedTeamStatus) {
                selectedTeamStatus.textContent = `Bạn đang ở Đội ${myTeam}`;
            }
            if (btnReady) {
                btnReady.disabled = false;
            }
        }

        if (window.GAME_CONFIG.isHost && btnStart) {
            btnStart.classList.add('hidden');
        }

        // Mode selector (Host only)
        if (window.GAME_CONFIG.isHost) {
            document.querySelectorAll('.mode-card').forEach(el => {
                el.addEventListener('click', () => {
                    SoundEffects.playClick();
                    myTournamentMode = el.dataset.mode === 'tournament';
                    tournamentMode = myTournamentMode;
                    updateModeUI(myTournamentMode);
                    socket.emit('update_settings', {
                        tournament_mode: myTournamentMode,
                    });
                });
            });
        } else {
            document.querySelectorAll('.mode-card').forEach(el => {
                el.style.pointerEvents = 'none';
            });
        }

        // Ready Button
        btnReady.addEventListener('click', () => {
            if (!myTeam) {
                showToast('Bạn cần chọn đội trước khi sẵn sàng!', 'error');
                return;
            }
            SoundEffects.playClick();
            isReady = !isReady;
            socket.emit('toggle_ready', { ready: isReady });
            if (isReady) {
                btnReady.textContent = "Hủy sẵn sàng";
                btnReady.className = "btn btn-outline btn-block btn-lg mt-2";
            } else {
                btnReady.textContent = "Sẵn sàng";
                btnReady.className = "btn btn-primary btn-block btn-lg mt-2";
            }
        });

        // Team selection
        if (teamSelector) {
            if (teamLocked) {
                teamSelector.classList.add('team-locked');
            }
            teamSelector.addEventListener('click', (e) => {
                const card = e.target.closest('.team-card');
                if (!card || card.classList.contains('full') || teamLocked) return;

                SoundEffects.playClick();
                socket.emit('select_team', { team: Number(card.dataset.team) });
            });
        }

        // Start Button
        if (btnStart) {
            btnStart.addEventListener('click', () => {
                SoundEffects.playClick();
                btnStart.disabled = true;
                btnStart.textContent = 'Đang khởi động...';
                socket.emit('start_game');
            });
        }
    }

    // Game Actions
    function setupGameListeners() {
        // Answer clicks
        answersContainer.addEventListener('click', (e) => {
            const btn = e.target.closest('.answer-btn');
            if (!btn || isAnswerLocked || hasAnswered || btn.classList.contains('disabled') || btn.classList.contains('eliminated')) return;

            SoundEffects.playClick();
            hasAnswered = true;
            btn.classList.add('selected');
            
            // Disable all buttons
            document.querySelectorAll('.answer-btn').forEach(b => b.classList.add('disabled'));

            const limit = currentTimeLimit;
            const timerVal = parseInt(gameTimer.textContent) || 0;
            const timeTaken = limit - timerVal;

            socket.emit('submit_answer', {
                answer: ['a', 'b', 'c', 'd'][parseInt(btn.dataset.idx)],
                time_taken: timeTaken
            });
        });

        // Lifelines
        btn5050.addEventListener('click', () => {
            if (!currentLifelines.fifty_fifty || hasAnswered) return;
            SoundEffects.playClick();
            socket.emit('use_lifeline', { type: 'fifty_fifty' });
        });

        btnHint.addEventListener('click', () => {
            if (!currentLifelines.hint || hasAnswered) return;
            SoundEffects.playClick();
            socket.emit('use_lifeline', { type: 'hint' });
        });
        
        btnPlayAgain.addEventListener('click', () => {
            SoundEffects.playClick();
            window.location.href = '/';
        });

        const btnHostReset = document.getElementById('btn-host-reset');
        if (btnHostReset) {
            btnHostReset.addEventListener('click', () => {
                if (confirm('Bạn có chắc chắn muốn dừng và reset lại trò chơi không? Tất cả điểm số sẽ được đặt lại về 0.')) {
                    SoundEffects.playClick();
                    socket.emit('reset_game');
                }
            });
        }

        // Round 3 controls
        if (btnR3Submit) {
            btnR3Submit.addEventListener('click', () => {
                if (!r3CurrentHandler || r3CurrentHandler.submitted) return;
                SoundEffects.playClick();
                const payload = r3CurrentHandler.getAnswerPayload();
                if (!payload) {
                    showToast('Hãy thực hiện tương tác trước khi nộp!', 'warning');
                    return;
                }
                r3CurrentHandler.disable();
                btnR3Submit.disabled = true;
                const timerVal = parseInt(r3Timer ? r3Timer.textContent : '0') || 0;
                socket.emit('submit_answer', {
                    round3_answer: payload,
                    time_taken: (currentTimeLimit || 30) - timerVal
                });
            });
        }

        if (btnR3Next) {
            btnR3Next.addEventListener('click', () => {
                if (!window.GAME_CONFIG.isHost) return;
                SoundEffects.playClick();
                socket.emit('next_round3_case');
            });
        }

        // Round 4 controls
        if (btnR4Submit) {
            btnR4Submit.addEventListener('click', () => {
                if (!r4CurrentHandler || r4CurrentHandler.submitted) return;
                SoundEffects.playClick();
                const payload = r4CurrentHandler.getAnswerPayload();
                if (!payload) {
                    showToast('Hãy thực hiện tương tác trước khi nộp!', 'warning');
                    return;
                }
                r4CurrentHandler.disable();
                btnR4Submit.disabled = true;
                const timerVal = parseInt(r4Timer ? r4Timer.textContent : '0') || 0;
                socket.emit('submit_answer', {
                    round3_answer: payload,
                    time_taken: 20 - timerVal
                });
            });
        }

        if (btnR4Hint) {
            btnR4Hint.addEventListener('click', () => {
                if (r4HintUsed) return;
                SoundEffects.playClick();
                r4HintUsed = true;
                btnR4Hint.disabled = true;
                btnR4Hint.textContent = 'Đã dùng gợi ý';
                socket.emit('use_lifeline', { type: 'hint' });
            });
        }
    }

    function displayQuestion(data) {
        hasAnswered = false;
        isAnswerLocked = Boolean(data.answer_locked);
        expPopup.classList.remove('show');
        hintPopup.classList.add('hidden');

        if (data.time_per_question) {
            currentTimeLimit = data.time_per_question;
        }
        if (data.round) {
            currentRound = data.round;
            updateRoundUI(data);
        }

        qArticle.textContent = isAnswerLocked
            ? `Đọc câu hỏi: ${data.read_seconds || 8}s`
            : (data.article || "NĐ 13/2023");
        qText.textContent = data.question;
        const roundLabel = tournamentMode && currentRound
            ? `[${TOURNAMENT_ROUNDS[currentRound]?.name || 'Vòng ' + currentRound}] `
            : '';
        gameProgress.textContent = `${roundLabel}Câu ${data.current_q} / ${data.total_q}`;

        if (currentLifelines.fifty_fifty) btn5050.disabled = false;
        if (currentLifelines.hint) btnHint.disabled = false;
answersContainer.innerHTML = '';
        if (isEliminated) {
            qText.textContent = `[Khán giả] ${data.question}`;
            answersContainer.innerHTML = '<p class="spectator-notice">Đội của bạn đã bị loại. Theo dõi các đội còn lại.</p>';
            return;
        }

        const labels = ['A', 'B', 'C', 'D'];
        data.options.forEach((opt, idx) => {
            const btn = document.createElement('button');
            btn.className = `answer-btn ${isAnswerLocked ? 'disabled' : ''}`;
            btn.disabled = isAnswerLocked;
            btn.dataset.idx = idx;
            btn.innerHTML = `
                <span class="answer-label">${labels[idx]}</span>
                <span class="answer-text">${opt}</span>
            `;
            answersContainer.appendChild(btn);
        });
    }

    function updatePlayerList(players) {
        lobbyPlayers.innerHTML = '';
        playerCount.textContent = `${players.length}/60`;
        
        players.forEach(p => {
            const el = document.createElement('div');
            el.className = 'player-item';
            el.innerHTML = `
                <div class="player-avatar">${p.avatar}</div>
                <div class="player-name">${p.username} ${p.is_host ? '👑' : ''}</div>
                <div class="player-team-badge">${p.team ? `Đội ${p.team}` : 'Chưa chọn đội'}</div>
                <div style="font-size: 0.8rem; font-weight: bold; color: ${p.ready ? 'var(--success)' : 'var(--text-muted)'}">
                    ${p.ready ? 'Sẵn sàng' : 'Chờ...'}
                </div>
            `;
            lobbyPlayers.appendChild(el);
        });
    }

    function updateMyTeamState(players) {
        const me = players.find(p => p.sid === socket.id);
        if (!me) return;

        myTeam = me.team || null;
        isEliminated = Boolean(me.is_eliminated);
        if (selectedTeamStatus) {
            const hostLabel = me.is_host ? ' · Host' : '';
            selectedTeamStatus.textContent = myTeam ? `Bạn đang ở Đội ${myTeam}${hostLabel}` : 'Chưa chọn đội';
        }

        if (btnReady) {
            btnReady.disabled = !myTeam;
            if (!myTeam) {
                isReady = false;
                btnReady.textContent = 'Chọn đội để sẵn sàng';
                btnReady.className = 'btn btn-primary btn-block btn-lg mt-2';
            } else {
                isReady = Boolean(me.ready);
                btnReady.textContent = isReady ? 'Hủy sẵn sàng' : 'Sẵn sàng';
                btnReady.className = isReady
                    ? 'btn btn-outline btn-block btn-lg mt-2'
                    : 'btn btn-primary btn-block btn-lg mt-2';
            }
        }

        document.querySelectorAll('.team-card').forEach(card => {
            card.classList.toggle('selected', Number(card.dataset.team) === myTeam);
        });
    }

    function updateTeamGrid(teams) {
        if (!teamSelector) return;

        teams.forEach(team => {
            const card = teamSelector.querySelector(`.team-card[data-team="${team.id}"]`);
            if (!card) return;
const count = card.querySelector('.team-count');
            const members = card.querySelector('.team-members');
            const isFull = team.count >= team.capacity;
            const names = team.members.map(member => member.username).join(', ');

            count.textContent = `${team.count}/${team.capacity}`;
            members.textContent = names || 'Đang chờ thành viên';
            card.classList.toggle('full', isFull);
            card.disabled = isFull && Number(card.dataset.team) !== myTeam;
        });
    }

    function updateLeaderboard(players, teamRankings) {
        let sorted;
        if (teamRankings && teamRankings.length) {
            sorted = teamRankings.map(t => ({
                team: t.team,
                name: t.name || `Đội ${t.team}`,
                score: t.score,
                members: t.members || [],
                eliminated: t.eliminated,
                active: t.active,
                rank: t.rank,
            }));
        } else {
            sorted = buildTeamLeaderboard(players);
        }

        gameLeaderboard.innerHTML = '';
        sorted.forEach((team, idx) => {
            const el = document.createElement('div');
            const rank = team.rank || idx + 1;
            const statusClass = team.eliminated ? 'team-eliminated' : (team.active === false ? 'team-inactive' : '');
            el.className = `player-item team-score-item ${statusClass}`;
            el.id = `lb-team-${team.team}`;
            el.innerHTML = `
                <div class="player-avatar">${team.eliminated ? '❌' : (rank <= 3 ? ['🥇','🥈','🥉'][rank-1] : '🛡️')}</div>
                <div class="player-name" style="font-size: 0.9rem;">${team.name || 'Đội ' + team.team}</div>
                <div class="player-team-badge">${team.members ? team.members.length : 0}/5</div>
                <div class="player-score">${team.score}</div>
            `;
            gameLeaderboard.appendChild(el);
        });
    }

    function buildTeamLeaderboard(players) {
        const teamMap = new Map();

        players.forEach(player => {
            const teamId = Number(player.team);
            if (!teamId) return;

            if (!teamMap.has(teamId)) {
                teamMap.set(teamId, {
                    team: teamId,
                    name: `Đội ${teamId}`,
                    avatar: '🛡️',
                    score: 0,
                    members: [],
                    best_streak: 0
                });
            }

            const team = teamMap.get(teamId);
            team.score += Number(player.score || 0);
            team.members.push(player);
            team.best_streak = Math.max(team.best_streak, Number(player.best_streak || player.streak || 0));
        });

        return [...teamMap.values()].sort((a, b) => b.score - a.score || a.team - b.team);
    }

    function updateModeUI(isTournament) {
        document.querySelectorAll('.mode-card').forEach(card => {
card.classList.toggle('selected', card.dataset.mode === (isTournament ? 'tournament' : 'classic'));
        });
    }

    function updateRoundUI(data) {
        if (!gameRoundInfo || !roundBadge) return;
        if (!tournamentMode && !data.tournament_mode) {
            gameRoundInfo.classList.add('hidden');
            return;
        }
        gameRoundInfo.classList.remove('hidden');
        const roundNum = data.round || currentRound;
        roundBadge.textContent = data.round_name || TOURNAMENT_ROUNDS[roundNum]?.name || `Vòng ${roundNum}`;
        if (roundDesc) {
            roundDesc.textContent = data.round_description || '';
        }
    }

    function formatCountdown(seconds) {
        const m = Math.floor(seconds / 60);
        const s = seconds % 60;
        return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    }

    function updateBreakCountdown(seconds) {
        if (breakCountdown) {
            breakCountdown.textContent = formatCountdown(seconds);
        }
    }

    function renderBreakRankings(rankings) {
        if (!breakRankings) return;
        breakRankings.innerHTML = '';
        rankings.forEach(team => {
            const el = document.createElement('div');
            el.className = `break-rank-item ${team.eliminated ? 'eliminated' : 'active'}`;
            el.innerHTML = `
                <span class="break-rank-no">#${team.rank || '-'}</span>
                <span class="break-rank-name">${team.name || 'Đội ' + team.team}</span>
                <span class="break-rank-score">${team.score} điểm</span>
                <span class="break-rank-status">${team.eliminated ? '❌ Loại' : '✅ Đi tiếp'}</span>
            `;
            breakRankings.appendChild(el);
        });
    }

    function renderBreakTeams(teamIds, container, type) {
        if (!container) return;
        container.innerHTML = '';
        if (!teamIds.length) {
            container.innerHTML = '<span class="break-empty">—</span>';
            return;
        }
        teamIds.forEach(id => {
            const chip = document.createElement('span');
            chip.className = `team-chip ${type}`;
            chip.textContent = `Đội ${id}`;
            container.appendChild(chip);
        });
    }

    function showRoundBreakSummary(data) {
        // Brief toast before break screen loads from round_break event
        const advancing = (data.advancing_teams || []).map(t => `Đội ${t}`).join(', ');
        showToast(`Kết thúc ${data.round_name}. Đi tiếp: ${advancing}`, 'success');
    }

    function displayTournamentResults(data) {
        showScreen('results');
        if (resultsTitle) resultsTitle.textContent = 'Kết Quả Giải Đấu';

        const rankings = data.final_rankings || [];
        const winner = data.winner;
        const mvp = data.mvp;

        if (tournamentWinnerBanner && winner) {
            tournamentWinnerBanner.classList.remove('hidden');
            winnerTeamName.textContent = winner.name || `Đội ${winner.team}`;
            if (mvp) {
                mvpPlayerName.textContent = mvp.name || '—';
                mvpPlayerScore.textContent = `(${mvp.score} điểm)`;
            }
        }

        podium.innerHTML = '';
        if (rankings.length > 0) {
            if (rankings.length > 1) {
                podium.appendChild(createPodiumItem(rankings[1], 2, '🥈'));
            }
            podium.appendChild(createPodiumItem(rankings[0], 1, '🏆'));
            if (rankings.length > 2) {
                podium.appendChild(createPodiumItem(rankings[2], 3, '🥉'));
            }
        }

        const me = (data.final_scores || []).find(p => p.name === window.CURRENT_USER.username);
        const myTeamResult = myTeam ? rankings.find(t => t.team === myTeam) : null;
        const myStats = {
            score: myTeamResult ? myTeamResult.score : (me ? me.score : 0),
            correct_answers: me ? (me.score > 0 ? '?' : 0) : 0,
            max_streak: me ? me.best_streak : 0,
        };
        resScore.textContent = myStats.score || 0;
        resCorrect.textContent = myStats.correct_answers !== undefined ? myStats.correct_answers : '--';
        resStreak.textContent = myStats.max_streak || 0;

        displayTeamRankings(rankings);
        startAutoRedirectCountdown(15);
    }

    function displayResults(leaderboard, myStats) {
        showScreen('results');
        if (tournamentWinnerBanner) tournamentWinnerBanner.classList.add('hidden');
        if (resultsTitle) resultsTitle.textContent = 'Kết Quả Cuộc Thi';
        
        // Populate Podium
        podium.innerHTML = '';
        if (leaderboard.length > 0) {
            // 2nd Place
            if (leaderboard.length > 1) {
                podium.appendChild(createPodiumItem(leaderboard[1], 2, '🥈'));
            }
            // 1st Place
            podium.appendChild(createPodiumItem(leaderboard[0], 1, '🏆'));
            // 3rd Place
            if (leaderboard.length > 2) {
                podium.appendChild(createPodiumItem(leaderboard[2], 3, '🥉'));
            }
        }
        
        // My Stats
        resScore.textContent = myStats.score || 0;
        resCorrect.textContent = myStats.correct_answers !== undefined ? myStats.correct_answers : '--';
        resStreak.textContent = myStats.max_streak || 0;

        displayTeamRankings(leaderboard);
        startAutoRedirectCountdown(15);
    }

    function createPodiumItem(player, rank, medal) {
        const div = document.createElement('div');
        div.className = `podium-item podium-${rank === 1 ? '1st' : rank === 2 ? '2nd' : '3rd'}`;
        const displayName = player.name || player.username || 'Ẩn danh';
        const avatar = player.avatar || '👤';
        const members = player.members ? `<div class="podium-members">${player.members.map(p => p.name || p.username).join(', ')}</div>` : '';
        div.innerHTML = `
            <div class="podium-avatar">${avatar}</div>
            <div class="podium-name">${medal} ${displayName}</div>
<div class="podium-score">${player.score ?? 0} điểm</div>
            ${members}
        `;
        return div;
    }

    function showToast(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
            background: ${type === 'error' ? 'var(--danger)' : type === 'success' ? 'var(--success)' : type === 'warning' ? 'var(--accent)' : 'var(--primary)'};
            color: #fff; padding: 12px 24px; border-radius: 12px;
            font-weight: 600; z-index: 9999; animation: slideUp 0.3s ease;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3); max-width: 80vw; text-align: center;
        `;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), duration);
    }

    function showBadgeUnlock(badge) {
        document.getElementById('badge-icon').textContent = badge.icon;
        document.getElementById('badge-name').textContent = badge.name;
        document.getElementById('badge-desc').textContent = badge.description;
        badgeModal.classList.add('show');
    }

    function showSceneIntro(data = {}) {
        const duration = Number(data.seconds || 12);
        let remaining = duration;

        stopSceneCountdown();
        if (sceneCountdown) {
            sceneCountdown.textContent = remaining;
        }
        showScreen('scene');

        sceneCountdownTimer = setInterval(() => {
            remaining = Math.max(0, remaining - 1);
            if (sceneCountdown) {
                sceneCountdown.textContent = remaining;
            }
            if (remaining <= 0) {
                stopSceneCountdown();
            }
        }, 1000);
    }

    function stopSceneCountdown() {
        if (sceneCountdownTimer) {
            clearInterval(sceneCountdownTimer);
            sceneCountdownTimer = null;
        }
    }

    function showRoundIntro(data = {}) {
        let remaining = Number(data.round_intro_seconds || 30);

        if (roundIntroKicker && data.round) {
            roundIntroKicker.textContent = `Vòng ${data.round}`;
        }
        if (roundIntroTitle && data.round_name) {
            roundIntroTitle.textContent = data.round_name;
        }
        if (roundIntroDescription && data.round_description) {
            roundIntroDescription.innerHTML = data.round_description;
        }

        stopRoundIntroCountdown();
        if (roundIntroCountdown) {
            roundIntroCountdown.textContent = remaining;
        }
        showScreen('round-intro');

        roundIntroTimer = setInterval(() => {
            remaining = Math.max(0, remaining - 1);
            if (roundIntroCountdown) {
                roundIntroCountdown.textContent = remaining;
            }
            if (remaining <= 0) {
                stopRoundIntroCountdown();
                showScreen('game');
            }
        }, 1000);
    }

    function stopRoundIntroCountdown() {
        if (roundIntroTimer) {
            clearInterval(roundIntroTimer);
            roundIntroTimer = null;
        }
    }

    function showScreen(name) {
        screenLobby.classList.remove('active');
        if (screenScene) screenScene.classList.remove('active');
        if (screenRoundIntro) screenRoundIntro.classList.remove('active');
        screenGame.classList.remove('active');
        if (screenBreak) screenBreak.classList.remove('active');
        screenResults.classList.remove('active');

        // Hide special round layouts
        if (round3GameLayout) round3GameLayout.classList.add('hidden');
        if (round4GameLayout) round4GameLayout.classList.add('hidden');

        document.getElementById(`screen-${name}`).classList.add('active');
    }

    // ── Round 4 UI Helpers ──
    function renderR4TeammateList(teammateProgress) {
        if (!r4TeammateList) return;
        r4TeammateList.innerHTML = '';
        teammateProgress.forEach(tp => {
            const item = document.createElement('div');
            const statusIcon = tp.status === 'completed' ? '✅' : (tp.status === 'current' ? '🎮' : '⏳');
            const activeClass = tp.status === 'current' ? 'r4-teammate-active' : '';
            const completedClass = tp.status === 'completed' ? 'r4-teammate-done' : '';
            item.className = `r4-teammate-item ${activeClass} ${completedClass}`;
            item.innerHTML = `
                <span class="r4-teammate-name">${statusIcon} ${tp.player_name}</span>
                <span class="r4-teammate-mission">NV${tp.mission_index}</span>
                <span class="r4-teammate-score">${tp.score > 0 ? `+${tp.score}` : (tp.status === 'completed' ? '0' : '—')}</span>
            `;
            r4TeammateList.appendChild(item);
        });
    }

    function renderR4OpponentProgress(oppData) {
        if (!oppData) return;
        if (r4OpponentTeamName) r4OpponentTeamName.textContent = `Đội ${oppData.team_id}`;
        if (r4OpponentScore) r4OpponentScore.textContent = `${oppData.score || 0}đ`;
        if (r4OpponentProgressDots) {
            r4OpponentProgressDots.innerHTML = '';
            (oppData.progress || []).forEach((status, i) => {
                const dot = document.createElement('span');
                dot.className = `r4-opp-dot ${status}`;
                dot.textContent = `NV${i + 1}`;
                r4OpponentProgressDots.appendChild(dot);
            });
        }
    }

    function updateHostProgressDashboard() {
        const progressContainer = document.getElementById('host-teams-progress');
        if (!progressContainer) return;

        progressContainer.innerHTML = '';

        const teamsMap = new Map();
        
        for (let i = 1; i <= 10; i++) {
            teamsMap.set(i, {
                id: i,
                score: 0,
                members: [],
                active: false
            });
        }

        currentPlayers.forEach(p => {
            if (p.is_host || !p.team) return;
            const teamId = Number(p.team);
            const team = teamsMap.get(teamId);
            if (team) {
                team.active = true;
                team.score += p.score || 0;
                
                const progressEntry = currentAnswersProgress.find(ap => ap.sid === p.sid);
                const hasAnswered = progressEntry ? progressEntry.answered : false;
                
                team.members.push({
                    sid: p.sid,
                    name: p.username,
                    avatar: p.avatar,
                    answered: hasAnswered
                });
            }
        });

        const activeTeams = [...teamsMap.values()].filter(t => t.active);
        
        if (activeTeams.length === 0) {
            progressContainer.innerHTML = '<p class="spectator-notice">Chưa có đội nào tham gia.</p>';
            return;
        }

        activeTeams.forEach(team => {
            const allAnswered = team.members.every(m => m.answered);
            const answeredCount = team.members.filter(m => m.answered).length;
            const totalCount = team.members.length;

            const card = document.createElement('div');
            card.className = `host-team-progress-card ${allAnswered ? 'all-answered' : ''}`;
            
            let membersHTML = team.members.map(m => `
                <span class="player-progress-dot ${m.answered ? 'answered' : ''}">
                    ${m.avatar} ${m.name} ${m.answered ? '✅' : '⏳'}
                </span>
            `).join('');

            card.innerHTML = `
                <div class="host-team-progress-header">
                    <span class="host-team-name">Đội ${team.id} (${answeredCount}/${totalCount})</span>
                    <span class="host-team-score">${team.score} điểm</span>
                </div>
                <div class="host-team-members-progress">
                    ${membersHTML}
                </div>
            `;
            progressContainer.appendChild(card);
        });
    }

    let redirectInterval = null;

    function startAutoRedirectCountdown(seconds = 15) {
        const timerBanner = document.getElementById('results-countdown-banner');
        const timerText = document.getElementById('results-countdown-timer');
        if (!timerBanner || !timerText) return;

        timerBanner.classList.remove('hidden');
        let remaining = seconds;
        timerText.textContent = remaining;

        if (redirectInterval) clearInterval(redirectInterval);
        
        redirectInterval = setInterval(() => {
            remaining--;
            if (timerText) timerText.textContent = remaining;
            if (remaining <= 0) {
                clearInterval(redirectInterval);
                window.location.href = '/';
            }
        }, 1000);
    }

    function displayTeamRankings(items) {
        const listContainer = document.getElementById('team-rankings-list');
        const cardContainer = document.getElementById('team-rankings-card');
        if (!listContainer || !cardContainer) return;

        if (!items || items.length === 0) {
            cardContainer.classList.add('hidden');
            return;
        }

        cardContainer.classList.remove('hidden');
        listContainer.innerHTML = '';

        // Sort items by score descending (highest score at the top, lowest score at the bottom)
        const sortedItems = [...items].sort((a, b) => {
            return (b.score || 0) - (a.score || 0) || (a.total_time || 0) - (b.total_time || 0);
        });

        sortedItems.forEach((item, idx) => {
            const rank = idx + 1;
            
            // Format name and members
            let displayName = '';
            let membersList = '';
            let isTeam = item.team !== undefined;

            if (isTeam) {
                displayName = item.name || `Đội ${item.team}`;
                membersList = (item.members || []).map(m => m.name || m.username || 'Ẩn danh').join(', ');
            } else {
                displayName = item.name || item.username || 'Ẩn danh';
                membersList = 'Cá nhân';
            }

            // Medals or rank formatting
            let rankBadge = '';
            if (rank === 1) rankBadge = '🥇';
            else if (rank === 2) rankBadge = '🥈';
            else if (rank === 3) rankBadge = '🥉';
            else rankBadge = `#${rank}`;

            const row = document.createElement('div');
            row.className = 'flex items-center justify-between p-4 bg-slate-800/40 hover:bg-slate-800/80 border border-slate-700/30 rounded-2xl transition-all duration-300 shadow-lg backdrop-blur-sm';
            row.innerHTML = `
                <div class="flex items-center gap-4">
                    <span class="w-10 h-10 rounded-xl bg-gradient-to-br from-slate-700 to-slate-800 text-white flex items-center justify-center font-extrabold text-base shadow-md border border-slate-600/50">${rankBadge}</span>
                    <div>
                        <span class="font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-300 text-lg">${displayName}</span>
                        <span class="text-xs text-slate-400 block mt-0.5">${membersList}</span>
                    </div>
                </div>
                <div class="text-right">
                    <span class="font-black text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-yellow-500 text-2xl">${item.score || 0}đ</span>
                    ${item.total_time ? `<span class="text-[10px] text-slate-500 block">Thời gian: ${item.total_time.toFixed(1)}s</span>` : ''}
                </div>
            `;
            listContainer.appendChild(row);
        });
    }

    // Start everything
    init();
});
