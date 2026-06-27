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

    // State
    let socket;
    let myAvatar = '👤';
    let myDifficulty = 'medium';
    let myTeam = null;
    let isReady = false;
    let hasAnswered = false;
    let currentLifelines = { fifty_fifty: true, hint: true };

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
            updatePlayerList(players);
            updateLeaderboard(players);
            updateMyTeamState(players);
            
            // Check if all players ready
            if (window.GAME_CONFIG.isHost) {
                const allReady = players.every(p => p.ready && p.team);
                if (allReady && players.length > 0) {
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
                // Update UI to reflect host's difficulty choice
                document.querySelectorAll('.diff-card').forEach(el => el.classList.remove('selected'));
                const sel = document.querySelector(`.diff-card[data-diff="${data.difficulty}"]`);
                if(sel) sel.classList.add('selected');
                myDifficulty = data.difficulty;
            }
        });

        socket.on('game_started', (data) => {
            showScreen('game');
            // Reset lifelines based on difficulty config
            const lifelines = (data && data.lifelines) ? data.lifelines : [];
            currentLifelines = {
                fifty_fifty: lifelines.includes('fifty_fifty'),
                hint: lifelines.includes('hint')
            };
            // Update lifeline button states
            if (!currentLifelines.fifty_fifty) {
                btn5050.disabled = true;
                btn5050.style.opacity = '0.3';
                btn5050.title = 'Không khả dụng ở độ khó này';
            }
            if (!currentLifelines.hint) {
                btnHint.disabled = true;
                btnHint.style.opacity = '0.3';
                btnHint.title = 'Không khả dụng ở độ khó này';
            }
        });

        socket.on('new_question', (data) => {
            displayQuestion(data);
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
                updateLeaderboard(data.players);
            }
        });

        socket.on('game_over', (data) => {
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

        // Difficulty (Host only)
        if (window.GAME_CONFIG.isHost) {
            document.querySelectorAll('.diff-card').forEach(el => {
                el.addEventListener('click', () => {
                    SoundEffects.playClick();
                    document.querySelectorAll('.diff-card').forEach(e => e.classList.remove('selected'));
                    el.classList.add('selected');
                    myDifficulty = el.dataset.diff;
                    socket.emit('update_settings', { difficulty: myDifficulty });
                });
            });
        } else {
            // Disable clicks for non-host
            document.querySelectorAll('.diff-card').forEach(el => {
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

            const limit = 20;
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
    }

    function displayQuestion(data) {
        hasAnswered = false;
        expPopup.classList.remove('show'); // Hide explanation
        hintPopup.classList.add('hidden'); // Hide hint

        qArticle.textContent = data.article || "NĐ 13/2023";
        qText.textContent = data.question;
        gameProgress.textContent = `Câu ${data.current_q} / ${data.total_q}`;
        
        // Reset lifelines UI for new question if not used
        if (currentLifelines.fifty_fifty) btn5050.disabled = false;
        if (currentLifelines.hint) btnHint.disabled = false;

        answersContainer.innerHTML = '';
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

    function updateLeaderboard(players) {
        const sorted = buildTeamLeaderboard(players);
        gameLeaderboard.innerHTML = '';
        
        sorted.forEach(team => {
            const el = document.createElement('div');
            el.className = 'player-item team-score-item';
            el.id = `lb-team-${team.team}`;
            el.innerHTML = `
                <div class="player-avatar">🛡️</div>
                <div class="player-name" style="font-size: 0.9rem;">Đội ${team.team}</div>
                <div class="player-team-badge">${team.members.length}/5</div>
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

    function displayResults(leaderboard, myStats) {
        showScreen('results');
        
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
        screenResults.classList.remove('active');
        
        document.getElementById(`screen-${name}`).classList.add('active');
    }

    // Start everything
    init();
});
