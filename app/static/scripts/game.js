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
    const screenGame = document.getElementById('screen-game');
    const screenBreak = document.getElementById('screen-break');
    const screenResults = document.getElementById('screen-results');
    
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
    const btnSkipBreak = document.getElementById('btn-skip-break');
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
    const resultsTitle = document.getElementById('results-title');

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

    const TOURNAMENT_ROUNDS = {
        1: { name: 'Vòng 1 — Loại sơ' },
        2: { name: 'Vòng 2 — Bán kết' },
        3: { name: 'Vòng 3 — Chung kết' },
        4: { name: 'Vòng 4 — Đối kháng' },
    };

    const teamLocked = Boolean(window.GAME_CONFIG.playerTeam);

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
            
            // Check if all players ready (excluding host)
            if (window.GAME_CONFIG.isHost) {
                const playersToCheck = players.filter(p => !p.is_host);
                const allReady = playersToCheck.length > 0 && playersToCheck.every(p => p.ready && p.team);
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
            if (window.GAME_CONFIG.isHost && btnSkipBreak) {
                btnSkipBreak.classList.remove('hidden');
            }
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

        socket.on('game_started', (data) => {
            showScreen('game');
            if (window.GAME_CONFIG.isHost) {
                document.querySelector('.game-layout').classList.add('hidden');
                document.getElementById('host-dashboard').classList.remove('hidden');
            } else {
                document.querySelector('.game-layout').classList.remove('hidden');
                document.getElementById('host-dashboard').classList.add('hidden');
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
// Update lifeline button states
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
            currentAnswersProgress = currentPlayers.filter(p => !p.is_host).map(p => ({
                sid: p.sid,
                name: p.username,
                team: p.team,
                answered: false
            }));
            
            displayQuestion(data);
            
            if (window.GAME_CONFIG.isHost) {
                const hostQArticle = document.getElementById('host-q-article');
                const hostQText = document.getElementById('host-q-text');
                const hostQCorrect = document.getElementById('host-q-correct-answer');
                
                if (hostQArticle) hostQArticle.textContent = data.article || "NĐ 13/2023";
                if (hostQText) hostQText.textContent = data.question;
                
                if (hostQCorrect && data.correct_answer && data.options) {
                    const correctLetter = data.correct_answer.toUpperCase();
                    const correctIdx = ['A', 'B', 'C', 'D'].indexOf(correctLetter);
                    const correctText = data.options[correctIdx] || '';
                    hostQCorrect.innerHTML = `🟢 Đáp án đúng: <strong>${correctLetter}. ${correctText}</strong>`;
                }
                
                updateHostProgressDashboard();
            }
        });

        socket.on('timer_tick', (timeLeft) => {
            gameTimer.textContent = timeLeft;
            SoundEffects.playTick();
            if (timeLeft <= 5) {
                gameTimer.classList.add('danger');
            } else {
                gameTimer.classList.remove('danger');
                gameTimer.classList.remove('warning');
            }
        });

        socket.on('answer_result', (data) => {
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

        socket.on('error', (data) => {
            const msg = typeof data === 'string' ? data : (data.message || 'Lỗi không xác định');
            showToast(msg, 'error');
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

        if (window.GAME_CONFIG.isHost) {
            if (btnReady) btnReady.classList.add('hidden');
            if (selectedTeamStatus) selectedTeamStatus.textContent = 'Bạn là Quản trị viên (Host)';
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
                if (window.GAME_CONFIG.isHost) return;
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
                socket.emit('start_game');
            });
        }
    }

    // Game Actions
    function setupGameListeners() {
        // Answer clicks
        answersContainer.addEventListener('click', (e) => {
            const btn = e.target.closest('.answer-btn');
            if (!btn || hasAnswered || btn.classList.contains('disabled') || btn.classList.contains('eliminated')) return;

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

        if (btnSkipBreak) {
            btnSkipBreak.addEventListener('click', () => {
                SoundEffects.playClick();
                socket.emit('skip_break');
            });
        }

        const btnHostReset = document.getElementById('btn-host-reset');
        if (btnHostReset) {
            btnHostReset.addEventListener('click', () => {
                if (confirm('Bạn có chắc chắn muốn dừng và reset lại trò chơi không? Tất cả điểm số sẽ được đặt lại về 0.')) {
                    SoundEffects.playClick();
                    socket.emit('reset_game');
                }
            });
        }
    }

    function displayQuestion(data) {
        hasAnswered = false;
        expPopup.classList.remove('show');
        hintPopup.classList.add('hidden');

        if (data.time_per_question) {
            currentTimeLimit = data.time_per_question;
        }
        if (data.round) {
            currentRound = data.round;
            updateRoundUI(data);
        }

        qArticle.textContent = data.article || "NĐ 13/2023";
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
            btn.className = 'answer-btn';
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
        playerCount.textContent = `${players.length}/50`;
        
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
            selectedTeamStatus.textContent = myTeam ? `Bạn đang ở Đội ${myTeam}` : 'Chưa chọn đội';
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

    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
            background: ${type === 'error' ? 'var(--danger)' : type === 'success' ? 'var(--success)' : 'var(--primary)'};
            color: #fff; padding: 12px 24px; border-radius: 12px;
            font-weight: 600; z-index: 9999; animation: slideUp 0.3s ease;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        `;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3500);
    }

    function showBadgeUnlock(badge) {
        document.getElementById('badge-icon').textContent = badge.icon;
        document.getElementById('badge-name').textContent = badge.name;
        document.getElementById('badge-desc').textContent = badge.description;
        badgeModal.classList.add('show');
    }

    function showScreen(name) {
        screenLobby.classList.remove('active');
        screenGame.classList.remove('active');
        if (screenBreak) screenBreak.classList.remove('active');
        screenResults.classList.remove('active');

        document.getElementById(`screen-${name}`).classList.add('active');
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

    // Start everything
    init();
});