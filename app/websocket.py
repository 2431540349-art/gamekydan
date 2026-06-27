import json
import secrets
import time
import random
from threading import Timer, Lock
from flask import request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import current_user

from models.question import Question
from models.user import User
from models.badge_definition import BadgeDefinition
from models.player_answer import PlayerAnswer
from models.engine.sql import session as db_session

# SocketIO object initialized without app, will be initialized via init_app in app/__init__.py
socketio = SocketIO(cors_allowed_origins="*", async_mode='threading', logger=False, engineio_logger=False)

room_lock = Lock()
rooms = {}
TEAM_COUNT = 10
TEAM_SIZE = 5
MAX_PLAYERS_PER_ROOM = TEAM_COUNT * TEAM_SIZE

DIFFICULTY_CONFIG = {
    'easy': {
        'time_per_question': 20,
        'score_multiplier': 1.0,
        'lifelines': ['fifty_fifty', 'hint'],
        'question_count': 10
    },
    'medium': {
        'time_per_question': 20,
        'score_multiplier': 1.5,
        'lifelines': ['fifty_fifty'],
        'question_count': 12
    },
    'hard': {
        'time_per_question': 20,
        'score_multiplier': 2.0,
        'lifelines': [],
        'question_count': 15
    }
}

# Giải đấu 4 vòng: 10 → 5 → 3 → 2 đội (đối kháng chung kết)
# Thời gian nghỉ giữa vòng: 7–10 phút; thời gian/câu giảm dần ở vòng sâu hơn
TOURNAMENT_ROUND_CONFIG = {
    1: {
        'name': 'Vòng 1 — Loại sơ',
        'teams_in': 10,
        'teams_advance': 5,
        'question_count': 5,
        'time_per_question': 15,
        'break_seconds': 480,
        'description': '10 đội tranh tài, chọn 5 đội đi tiếp',
    },
    2: {
        'name': 'Vòng 2 — Bán kết',
        'teams_in': 5,
        'teams_advance': 3,
        'question_count': 4,
        'time_per_question': 12,
        'break_seconds': 420,
        'description': '5 đội, chọn 3 đội vào chung kết',
    },
    3: {
        'name': 'Vòng 3 — Chung kết',
        'teams_in': 3,
        'teams_advance': 2,
        'question_count': 3,
        'time_per_question': 10,
        'break_seconds': 420,
        'description': '3 đội, chọn 2 đội vào trận đối kháng',
    },
    4: {
        'name': 'Vòng 4 — Đối kháng',
        'teams_in': 2,
        'teams_advance': 1,
        'question_count': 5,
        'time_per_question': 7,
        'break_seconds': 0,
        'description': '2 đội đối đầu trực tiếp, chọn nhà vô địch & MVP',
        'is_final': True,
    },
}

def init_tournament_room_state(room):
    room['tournament_mode'] = True
    room['current_round'] = 0
    room['active_teams'] = set()
    room['eliminated_teams'] = set()
    room['round_history'] = []
    room['in_break'] = False
    room['break_remaining'] = 0

def get_teams_with_players(room):
    teams = set()
    for p in room['players'].values():
        if p.get('team'):
            teams.add(p['team'])
    return teams

def get_active_player_sids(room):
    if not room.get('tournament_mode'):
return list(room['players'].keys())
    active_teams = room.get('active_teams') or set()
    return [
        sid for sid, p in room['players'].items()
        if p.get('team') in active_teams
    ]

def get_round_time_limit(room):
    if room.get('tournament_mode') and room.get('current_round'):
        cfg = TOURNAMENT_ROUND_CONFIG.get(room['current_round'], {})
        return cfg.get('time_per_question', DIFFICULTY_CONFIG[room['difficulty']]['time_per_question'])
    return DIFFICULTY_CONFIG[room['difficulty']]['time_per_question']

def get_team_rankings(room, team_ids=None):
    if team_ids is None:
        team_ids = room.get('active_teams') or get_teams_with_players(room)
    teams = {}
    for sid, p in room['players'].items():
        team_id = p.get('team')
        if not team_id or team_id not in team_ids:
            continue
        if team_id not in teams:
            teams[team_id] = {
                'team': team_id,
                'name': f'Đội {team_id}',
                'score': 0,
                'total_time': 0.0,
                'members': [],
            }
        teams[team_id]['score'] += p['score']
        teams[team_id]['total_time'] += p.get('total_time', 0.0)
        teams[team_id]['members'].append({
            'sid': sid,
            'name': p['name'],
            'avatar': p['avatar'],
            'score': p['score'],
            'best_streak': p.get('best_streak', 0),
        })
    for team in teams.values():
        team['members'].sort(key=lambda m: m['score'], reverse=True)
    return sorted(
        teams.values(),
        key=lambda t: (-t['score'], t['total_time'], t['team'])
    )

def build_tournament_leaderboard_payload(room):
    rankings = get_team_rankings(room)
    eliminated = sorted(room.get('eliminated_teams') or set())
    for rank, team in enumerate(rankings, 1):
        team['rank'] = rank
        team['eliminated'] = team['team'] in (room.get('eliminated_teams') or set())
        team['active'] = team['team'] in (room.get('active_teams') or set())
    return rankings

def get_room_by_sid(sid):
    with room_lock:
        for code, room in rooms.items():
            if sid in room['players']:
                return code
    return None

def get_room_players_list(room_code):
    room = rooms.get(room_code)
    if not room:
        return []
    res = []
    for sid, p in room['players'].items():
        badges_list = []
        if p['user_id']:
            badges_list = get_user_badges(p['user_id'])
        res.append({
            'sid': sid,
            'user_id': p['user_id'],
            'username': p['name'],
            'avatar': p['avatar'],
            'team': p.get('team'),
            'score': p['score'],
            'streak': p['streak'],
            'ready': p['is_ready'],
            'is_host': (room['host_sid'] == sid),
            'badges': badges_list,
            'is_active': (
                not room.get('tournament_mode')
or p.get('team') in (room.get('active_teams') or set())
            ),
            'is_eliminated': (
                room.get('tournament_mode')
                and p.get('team') in (room.get('eliminated_teams') or set())
            ),
        })
    return res

def get_room_teams_list(room_code):
    players = get_room_players_list(room_code)
    teams = []
    for team_no in range(1, TEAM_COUNT + 1):
        members = [p for p in players if p.get('team') == team_no]
        teams.append({
            'id': team_no,
            'name': f"Đội {team_no}",
            'count': len(members),
            'capacity': TEAM_SIZE,
            'members': members
        })
    return teams

def emit_room_state(room_code):
    players = get_room_players_list(room_code)
    socketio.emit('player_list_update', players, to=room_code)
    socketio.emit('team_list_update', get_room_teams_list(room_code), to=room_code)

def get_user_badges(user_id):
    user = db_session.query(User).filter_by(id=user_id).first()
    if user and user.badges:
        try:
            return json.loads(user.badges)
        except:
            return []
    return []

def award_badge(user_id, badge_key):
    user = db_session.query(User).filter_by(id=user_id).first()
    if user:
        try:
            badges = json.loads(user.badges) if user.badges else []
        except:
            badges = []
        if badge_key not in badges:
            badges.append(badge_key)
            user.badges = json.dumps(badges)
            db_session.merge(user)
            db_session.commit()

def get_total_games(user_id):
    user = db_session.query(User).filter_by(id=user_id).first()
    return user.total_games if user else 0

def check_and_award_badges(user_id, game_result):
    awarded = []
    current_badges = get_user_badges(user_id)
    
    checks = [
        ('thanh_than', game_result.get('max_streak', 0) >= 10),
        ('biet_luat', len(game_result.get('articles_correct', [])) >= 10),
        ('chien_binh', game_result.get('final_rank') == 1),
        ('nhanh_tay', game_result.get('total_time', 999) <= 180),
        ('kien_nhan', get_total_games(user_id) >= 5),
        ('toan_ven', game_result.get('wrong_answers', 1) == 0),
    ]
    
    for badge_key, condition in checks:
        if condition and badge_key not in current_badges:
            award_badge(user_id, badge_key)
            awarded.append(badge_key)
    
    return awarded

# --- SOCKET.IO EVENT HANDLERS ---

@socketio.on('create_room')
def on_create_room(data):
    try:
        difficulty = data.get('difficulty', 'medium')
        avatar = data.get('avatar', 'avatar_1')
        name = data.get('name', 'Trưởng phòng')
        
        room_code = secrets.token_hex(3).upper()
        
        user_db_id = None
        if current_user.is_authenticated:
            user_db_id = current_user.id
            name = current_user.username
            current_user.avatar = avatar
current_user.difficulty = difficulty
            db_session.merge(current_user)
            db_session.commit()
            
        with room_lock:
            rooms[room_code] = {
                'host_sid': request.sid,
                'difficulty': difficulty,
                'tournament_mode': True,
                'started': False,
                'questions': [],
                'current_index': 0,
                'active_question': None,
                'question_start_time': 0,
                'player_answers_submitted': {},
                'players': {
                    request.sid: {
                        'user_id': user_db_id,
                        'name': name,
                        'avatar': avatar,
                        'team': None,
                        'score': 0,
                        'streak': 0,
                        'best_streak': 0,
                        'articles_correct': set(),
                        'wrong_answers': 0,
                        'total_time': 0.0,
                        'used_lifelines': {'fifty_fifty': False, 'hint': False},
                        'used_lifeline_on_this': False,
                        'is_ready': False
                    }
                },
                'game_id': secrets.token_hex(8),
                'timer_thread': None
            }
        
        join_room(room_code)
        
        emit('room_created', {
            'room_code': room_code,
            'difficulty': difficulty,
            'players': get_room_players_list(room_code),
            'teams': get_room_teams_list(room_code)
        })
    except Exception as e:
        emit('error', {'message': f"Lỗi tạo phòng: {str(e)}"})

@socketio.on('join_room')
def on_join_room(data):
    try:
        room_code = data.get('room_code', '').upper()
        avatar = data.get('avatar', 'avatar_1')
        name = data.get('name', 'Người chơi')
        
        with room_lock:
            if room_code not in rooms:
                emit('error', {'message': 'Phòng chơi không tồn tại!'})
                return
            room = rooms[room_code]
            if room['started']:
                emit('error', {'message': 'Ván đấu đã bắt đầu!'})
                return
            if len(room['players']) >= MAX_PLAYERS_PER_ROOM:
                emit('error', {'message': 'Phòng đã đủ 50 người!'})
                return
                
            user_db_id = None
            if current_user.is_authenticated:
                user_db_id = current_user.id
                name = current_user.username
                current_user.avatar = avatar
                db_session.merge(current_user)
                db_session.commit()
            
            if room['host_sid'] is None:
                room['host_sid'] = request.sid
            
            is_player_host = (room['host_sid'] == request.sid)
            
            team_id = data.get('team')
            if isinstance(team_id, str) and team_id.isdigit():
                team_id = int(team_id)
            if isinstance(team_id, int) and 1 <= team_id <= TEAM_COUNT:
                members_in_team = [player for player in room['players'].values() if player.get('team') == team_id]
                if len(members_in_team) < TEAM_SIZE:
                    assigned_team = team_id
                else:
                    assigned_team = None
            else:
                assigned_team = None

            room['players'][request.sid] = {
                'user_id': user_db_id,
'name': name,
                'avatar': avatar,
                'team': assigned_team,
                'score': 0,
                'streak': 0,
                'best_streak': 0,
                'articles_correct': set(),
                'wrong_answers': 0,
                'total_time': 0.0,
                'used_lifelines': {'fifty_fifty': False, 'hint': False},
                'used_lifeline_on_this': False,
                'is_ready': False
            }
            
        join_room(room_code)
        
        emit_room_state(room_code)
        
        emit('room_created', {
            'room_code': room_code,
            'difficulty': room['difficulty'],
            'players': get_room_players_list(room_code),
            'teams': get_room_teams_list(room_code)
        })
    except Exception as e:
        emit('error', {'message': f"Lỗi tham gia phòng: {str(e)}"})


@socketio.on('toggle_ready')
def on_toggle_ready(data):
    try:
        sid = request.sid
        room_code = get_room_by_sid(sid)
        if not room_code:
            return
        ready = bool(data.get('ready', False))
        with room_lock:
            room = rooms[room_code]
            if sid in room['players']:
                is_host = (room['host_sid'] == sid)
                if not room['players'][sid].get('team'):
                    emit('error', {'message': 'Bạn cần chọn đội trước khi sẵn sàng!'})
                    return
                room['players'][sid]['is_ready'] = True if is_host else ready
        emit_room_state(room_code)
    except Exception as e:
        emit('error', {'message': f"Lỗi sẵn sàng: {str(e)}"})


@socketio.on('select_team')
def on_select_team(data):
    try:
        sid = request.sid
        room_code = get_room_by_sid(sid)
        if not room_code:
            return

        team_id = int(data.get('team'))
        if team_id < 1 or team_id > TEAM_COUNT:
            emit('error', {'message': 'Đội không hợp lệ!'})
            return

        with room_lock:
            room = rooms[room_code]
            if room.get('started'):
                emit('error', {'message': 'Không thể đổi đội khi ván đấu đã bắt đầu!'})
                return
            if sid not in room['players']:
                return
            if room['players'][sid].get('team'):
                emit('error', {'message': 'Bạn đã được gán đội và không thể đổi.'})
                return

            members_in_team = [
                player_sid
                for player_sid, player in room['players'].items()
                if player_sid != sid and player.get('team') == team_id
            ]
            if len(members_in_team) >= TEAM_SIZE:
                emit('error', {'message': f'Đội {team_id} đã đủ 5 người!'})
                return

            room['players'][sid]['team'] = team_id
            room['players'][sid]['is_ready'] = False

        emit_room_state(room_code)
    except (TypeError, ValueError):
        emit('error', {'message': 'Đội không hợp lệ!'})
    except Exception as e:
        emit('error', {'message': f"Lỗi chọn đội: {str(e)}"})


@socketio.on('update_avatar')
def on_update_avatar(data):
    try:
        sid = request.sid
        room_code = get_room_by_sid(sid)
        if not room_code:
            return
        avatar = data.get('avatar')
        if avatar:
            with room_lock:
                room = rooms[room_code]
                if sid in room['players']:
                    room['players'][sid]['avatar'] = avatar
            emit_room_state(room_code)
    except Exception as e:
        emit('error', {'message': f"Lỗi cập nhật avatar: {str(e)}"})


@socketio.on('update_settings')
def on_update_settings(data):
    try:
        sid = request.sid
        room_code = get_room_by_sid(sid)
        if not room_code:
            return
        with room_lock:
            room = rooms[room_code]
            if room['host_sid'] != sid:
                return
            difficulty = data.get('difficulty')
            if difficulty in ['easy', 'medium', 'hard']:
                room['difficulty'] = difficulty
            if 'tournament_mode' in data:
                room['tournament_mode'] = bool(data.get('tournament_mode'))
        payload = {'difficulty': room['difficulty']}
        if 'tournament_mode' in data:
            payload['tournament_mode'] = room.get('tournament_mode', False)
        socketio.emit('settings_updated', payload, to=room_code)
        emit_room_state(room_code)
    except Exception as e:
        emit('error', {'message': f"Lỗi cập nhật thiết lập: {str(e)}"})

@socketio.on('start_game')
def on_start_game():
    try:
        sid = request.sid
        room_code = get_room_by_sid(sid)
        if not room_code:
            return
        room = rooms[room_code]
        if room['host_sid'] != sid:
            emit('error', {'message': 'Chỉ có trưởng phòng mới có thể bắt đầu game!'})
            return
        if not room['players']:
            emit('error', {'message': 'Phòng chưa có người chơi!'})
            return
        if any(not p.get('team') for p in room['players'].values()):
            emit('error', {'message': 'Tất cả người chơi cần chọn đội trước khi bắt đầu!'})
            return
        if any(not p.get('is_ready') for p in room['players'].values()):
            emit('error', {'message': 'Tất cả người chơi cần sẵn sàng trước khi bắt đầu!'})
            return

        room['started'] = True
        room['game_id'] = secrets.token_hex(8)

        if room.get('tournament_mode', True):
            teams_present = get_teams_with_players(room)
            if len(teams_present) < 2:
                emit('error', {'message': 'Giải đấu cần ít nhất 2 đội có người chơi!'})
                room['started'] = False
                return
            init_tournament_room_state(room)
            room['active_teams'] = teams_present
            start_tournament_round(room_code, 1)
        else:
            diff = room['difficulty']
            q_count = DIFFICULTY_CONFIG[diff]['question_count']
all_qs = db_session.query(Question).filter_by(difficulty=diff).all()
            if len(all_qs) < q_count:
                all_qs += db_session.query(Question).filter(Question.difficulty != diff).all()

            random.shuffle(all_qs)
            room['questions'] = all_qs[:q_count]
            room['current_index'] = 0

            socketio.emit('game_started', {
                'question_count': q_count,
                'difficulty': diff,
                'lifelines': DIFFICULTY_CONFIG[diff]['lifelines'],
                'tournament_mode': False,
            }, to=room_code)

            socketio.sleep(1.5)
            send_next_question(room_code)
    except Exception as e:
        emit('error', {'message': f"Lỗi khởi động game: {str(e)}"})

def load_round_questions(room, round_num):
    cfg = TOURNAMENT_ROUND_CONFIG[round_num]
    diff = room['difficulty']
    q_count = cfg['question_count']
    used_ids = set(room.get('used_question_ids') or [])

    all_qs = db_session.query(Question).filter_by(difficulty=diff).all()
    if len(all_qs) < q_count:
        all_qs += db_session.query(Question).filter(Question.difficulty != diff).all()

    available = [q for q in all_qs if q.id not in used_ids]
    if len(available) < q_count:
        available = list(all_qs)

    random.shuffle(available)
    selected = available[:q_count]
    if 'used_question_ids' not in room:
        room['used_question_ids'] = []
    room['used_question_ids'].extend(q.id for q in selected)
    room['questions'] = selected
    room['current_index'] = 0

def start_tournament_round(room_code, round_num):
    try:
        with room_lock:
            if room_code not in rooms:
                return
            room = rooms[room_code]

        cfg = TOURNAMENT_ROUND_CONFIG[round_num]
        room['current_round'] = round_num
        room['in_break'] = False
        load_round_questions(room, round_num)

        for p in room['players'].values():
            p['used_lifelines'] = {'fifty_fifty': False, 'hint': False}
            p['used_lifeline_on_this'] = False

        diff = room['difficulty']
        socketio.emit('round_started', {
            'round': round_num,
            'round_name': cfg['name'],
            'round_description': cfg['description'],
            'question_count': cfg['question_count'],
            'time_per_question': cfg['time_per_question'],
            'teams_active': sorted(room['active_teams']),
            'teams_eliminated': sorted(room.get('eliminated_teams') or set()),
            'difficulty': diff,
            'lifelines': DIFFICULTY_CONFIG[diff]['lifelines'],
            'tournament_mode': True,
            'total_rounds': 4,
            'team_rankings': build_tournament_leaderboard_payload(room),
        }, to=room_code)

        socketio.emit('game_started', {
            'question_count': cfg['question_count'],
            'difficulty': diff,
            'lifelines': DIFFICULTY_CONFIG[diff]['lifelines'],
'tournament_mode': True,
            'round': round_num,
            'round_name': cfg['name'],
        }, to=room_code)

        socketio.sleep(2.0)
        send_next_question(room_code)
    except Exception as e:
        socketio.emit('error', {'message': f"Lỗi bắt đầu vòng đấu: {str(e)}"}, to=room_code)

def send_next_question(room_code):
    try:
        with room_lock:
            if room_code not in rooms:
                return
            room = rooms[room_code]
            
        idx = room['current_index']
        if idx >= len(room['questions']):
            if room.get('tournament_mode'):
                end_tournament_round(room_code)
            else:
                end_game(room_code)
            return
            
        q = room['questions'][idx]
        room['active_question'] = q
        room['current_index'] += 1
        room['player_answers_submitted'] = {}
        room['question_start_time'] = time.time()
        
        for p in room['players'].values():
            p['used_lifeline_on_this'] = False
            
        # Build payload matching frontend expectations
        q_dict = {
            'id': q.id,
            'question': q.content,
            'options': [q.option_a, q.option_b, q.option_c, q.option_d],
            'article': q.article_name,
            'article_name': q.article_name,
            'difficulty': q.difficulty,
            'current_q': room['current_index'],
            'total_q': len(room['questions']),
        }
        if room.get('tournament_mode'):
            cfg = TOURNAMENT_ROUND_CONFIG.get(room['current_round'], {})
            q_dict['round'] = room['current_round']
            q_dict['round_name'] = cfg.get('name', '')
            q_dict['time_per_question'] = cfg.get('time_per_question', 20)
        
        socketio.emit('new_question', q_dict, to=room_code)
        
        room['timer_active'] = True
        
        def run_timer(rc, q_idx):
            try:
                with room_lock:
                    if rc not in rooms:
                        return
                    rm = rooms[rc]
                    limit = get_round_time_limit(rm)

                for t in range(limit, -1, -1):
                    with room_lock:
                        if rc not in rooms:
                            break
                        rm = rooms[rc]
                        if not rm['started'] or rm['current_index'] != q_idx or not rm.get('timer_active'):
                            break
                    
                    socketio.emit('timer_tick', t, to=rc)
                    
                    if t == 0:
                        handle_question_timeout(rc)
                        break
                    socketio.sleep(1.0)
            except Exception as ex:
                print("Error in timer background task:", ex)
                
        socketio.start_background_task(run_timer, room_code, room['current_index'])
    except Exception as e:
socketio.emit('error', {'message': f"Lỗi chuyển câu hỏi: {str(e)}"}, to=room_code)

def handle_question_timeout(room_code):
    try:
        with room_lock:
            if room_code not in rooms:
                return
            room = rooms[room_code]
            if not room['active_question']:
                return
                
        limit = get_round_time_limit(room)
        active_sids = get_active_player_sids(room)
        for sid in active_sids:
            p = room['players'].get(sid)
            if not p:
                continue
            if sid not in room['player_answers_submitted']:
                if p['user_id']:
                    try:
                        ans_log = PlayerAnswer(
                            user_id=p['user_id'],
                            game_id=room['game_id'],
                            question_id=room['active_question'].id,
                            article_id=room['active_question'].article_id,
                            is_correct=False,
                            time_taken=float(limit),
                            difficulty=room['difficulty']
                        )
                        db_session.add(ans_log)
                        db_session.commit()
                    except Exception as e:
                        print("Error logging timeout answer:", e)
                        db_session.rollback()
                        
                p['streak'] = 0
                p['wrong_answers'] += 1
                p['total_time'] += float(limit)
                
                socketio.emit('streak_update', {
                    'streak': 0,
                    'is_correct': False,
                    'explanation': room['active_question'].explanation,
                    'article_name': room['active_question'].article_name
                }, to=sid)
                
        reveal_answers(room_code)
    except Exception as e:
        print("Error handling timeout:", e)

def reveal_answers(room_code):
    try:
        with room_lock:
            if room_code not in rooms:
                return
            room = rooms[room_code]
            q = room['active_question']
            room['active_question'] = None
            room['timer_active'] = False
            
        correct_key = q.correct_answer.strip().lower()
        
        scores_update = {}
        for sid, p in room['players'].items():
            scores_update[sid] = p['score']
            
        socketio.emit('answer_result', {
            'correct_answer': correct_key,
            'explanation': q.explanation,
            'article_name': q.article_name,
            'scores': scores_update
        }, to=room_code)
        
        socketio.emit('leaderboard_update', {
            'players': get_room_players_list(room_code),
            'team_rankings': build_tournament_leaderboard_payload(room) if room.get('tournament_mode') else None,
'tournament_mode': room.get('tournament_mode', False),
            'current_round': room.get('current_round', 0),
        }, to=room_code)
        
        def auto_advance(rc):
            socketio.sleep(5.0)
            send_next_question(rc)
            
        socketio.start_background_task(auto_advance, room_code)
    except Exception as e:
        print("Error revealing answers:", e)

@socketio.on('request_next')
def on_request_next():
    try:
        sid = request.sid
        room_code = get_room_by_sid(sid)
        if not room_code:
            return
        room = rooms[room_code]
        if room['host_sid'] != sid:
            emit('error', {'message': 'Chỉ có trưởng phòng mới chuyển câu tiếp được!'})
            return
        
        send_next_question(room_code)
    except Exception as e:
        emit('error', {'message': f"Lỗi chuyển câu tiếp: {str(e)}"})

def end_tournament_round(room_code):
    try:
        with room_lock:
            if room_code not in rooms:
                return
            room = rooms[room_code]

        round_num = room['current_round']
        cfg = TOURNAMENT_ROUND_CONFIG[round_num]
        rankings = get_team_rankings(room, room['active_teams'])
        advance_count = min(cfg['teams_advance'], len(rankings))
        advancing = [t['team'] for t in rankings[:advance_count]]
        eliminated_this_round = [t['team'] for t in rankings[advance_count:]]

        round_result = {
            'round': round_num,
            'round_name': cfg['name'],
            'rankings': rankings,
            'advancing_teams': advancing,
            'eliminated_teams': eliminated_this_round,
        }
        room['round_history'].append(round_result)

        is_final = cfg.get('is_final', False)

        socketio.emit('round_end', {
            'round': round_num,
            'round_name': cfg['name'],
            'rankings': rankings,
            'advancing_teams': advancing,
            'eliminated_teams': eliminated_this_round,
            'is_final': is_final,
            'next_round': round_num + 1 if not is_final else None,
            'break_seconds': cfg['break_seconds'] if not is_final else 0,
        }, to=room_code)

        if is_final:
            end_tournament(room_code, rankings)
        else:
            room['eliminated_teams'].update(eliminated_this_round)
            room['active_teams'] = set(advancing)
            start_round_break(room_code, round_num, cfg['break_seconds'])
    except Exception as e:
        print("Error ending tournament round:", e)

def start_round_break(room_code, completed_round, break_seconds):
    try:
        with room_lock:
            if room_code not in rooms:
                return
            room = rooms[room_code]

        room['in_break'] = True
        room['break_remaining'] = break_seconds
        next_round = completed_round + 1
        next_cfg = TOURNAMENT_ROUND_CONFIG.get(next_round, {})

        socketio.emit('round_break', {
'completed_round': completed_round,
            'next_round': next_round,
            'next_round_name': next_cfg.get('name', ''),
            'next_round_description': next_cfg.get('description', ''),
            'break_seconds': break_seconds,
            'team_rankings': build_tournament_leaderboard_payload(room),
            'active_teams': sorted(room['active_teams']),
            'eliminated_teams': sorted(room['eliminated_teams']),
        }, to=room_code)

        def break_countdown(rc, total_seconds):
            try:
                for remaining in range(total_seconds, -1, -1):
                    with room_lock:
                        if rc not in rooms:
                            return
                        rm = rooms[rc]
                        if not rm.get('in_break'):
                            return
                        rm['break_remaining'] = remaining

                    socketio.emit('break_tick', {
                        'remaining': remaining,
                        'next_round': next_round,
                    }, to=rc)

                    if remaining == 0:
                        with room_lock:
                            if rc not in rooms:
                                return
                            rooms[rc]['in_break'] = False
                        start_tournament_round(rc, next_round)
                        break
                    socketio.sleep(1.0)
            except Exception as ex:
                print("Error in break countdown:", ex)

        socketio.start_background_task(break_countdown, room_code, break_seconds)
    except Exception as e:
        print("Error starting round break:", e)

def end_tournament(room_code, final_rankings):
    try:
        with room_lock:
            if room_code not in rooms:
                return
            room = rooms[room_code]
            room['started'] = False
            room['in_break'] = False

        if not final_rankings:
            final_rankings = get_team_rankings(room)

        winner = final_rankings[0] if final_rankings else None
        runner_up = final_rankings[1] if len(final_rankings) > 1 else None

        mvp = None
        if winner:
            mvp = max(winner['members'], key=lambda m: m['score']) if winner['members'] else None

        sorted_players = sorted(room['players'].items(), key=lambda x: x[1]['score'], reverse=True)
        badges_unlocked_all = {}

        for rank, (sid, p) in enumerate(sorted_players, 1):
            if p['user_id']:
                user = db_session.query(User).filter_by(id=p['user_id']).first()
                if user:
                    user.total_games += 1
                    user.total_score += p['score']
                    user.total_tries += (p['wrong_answers'] + len(p['articles_correct']))
                    user.right_tries += len(p['articles_correct'])
                    if p['best_streak'] > user.best_streak:
user.best_streak = p['best_streak']

                    db_session.merge(user)
                    db_session.commit()

                    is_winner = winner and p.get('team') == winner['team']
                    game_result = {
                        'max_streak': p['best_streak'],
                        'articles_correct': list(p['articles_correct']),
                        'final_rank': 1 if is_winner else rank,
                        'total_time': p['total_time'],
                        'wrong_answers': p['wrong_answers']
                    }
                    new_badges = check_and_award_badges(p['user_id'], game_result)
                    if new_badges:
                        badges_unlocked_all[sid] = new_badges

        socketio.emit('tournament_over', {
            'final_rankings': final_rankings,
            'winner': winner,
            'runner_up': runner_up,
            'mvp': mvp,
            'round_history': room.get('round_history', []),
            'final_scores': [{
                'sid': sid,
                'name': p['name'],
                'avatar': p['avatar'],
                'team': p.get('team'),
                'score': p['score'],
                'best_streak': p['best_streak'],
                'wrong_answers': p['wrong_answers'],
                'total_time': p['total_time']
            } for sid, p in sorted_players],
            'badges_earned': badges_unlocked_all,
        }, to=room_code)
    except Exception as e:
        print("Error ending tournament:", e)

def end_game(room_code):
    try:
        with room_lock:
            if room_code not in rooms:
                return
            room = rooms[room_code]
            room['started'] = False
            
        sorted_players = sorted(room['players'].items(), key=lambda x: x[1]['score'], reverse=True)
        badges_unlocked_all = {}
        
        for rank, (sid, p) in enumerate(sorted_players, 1):
            if p['user_id']:
                user = db_session.query(User).filter_by(id=p['user_id']).first()
                if user:
                    user.total_games += 1
                    user.total_score += p['score']
                    user.total_tries += (p['wrong_answers'] + len(p['articles_correct']))
                    user.right_tries += len(p['articles_correct'])
                    if p['best_streak'] > user.best_streak:
                        user.best_streak = p['best_streak']
                    
                    db_session.merge(user)
                    db_session.commit()
                    
                    game_result = {
                        'max_streak': p['best_streak'],
                        'articles_correct': list(p['articles_correct']),
                        'final_rank': rank,
                        'total_time': p['total_time'],
                        'wrong_answers': p['wrong_answers']
                    }
new_badges = check_and_award_badges(p['user_id'], game_result)
                    if new_badges:
                        badges_unlocked_all[sid] = new_badges
                        
        socketio.emit('game_over', {
            'final_scores': [{
                'sid': sid,
                'name': p['name'],
                'avatar': p['avatar'],
                'team': p.get('team'),
                'score': p['score'],
                'best_streak': p['best_streak'],
                'wrong_answers': p['wrong_answers'],
                'total_time': p['total_time']
            } for sid, p in sorted_players],
            'badges_earned': badges_unlocked_all
        }, to=room_code)
    except Exception as e:
        print("Error ending game:", e)

@socketio.on('submit_answer')
def on_submit_answer(data):
    try:
        sid = request.sid
        room_code = get_room_by_sid(sid)
        if not room_code:
            return
        room = rooms[room_code]
        p = room['players'].get(sid)
        if not p or not room['active_question']:
            return
        if sid in room['player_answers_submitted']:
            return
        if room.get('tournament_mode') and sid not in get_active_player_sids(room):
            return
            
        answer_text = data.get('answer', '')
        time_taken = float(data.get('time_taken', 0.0))
        q = room['active_question']
        
        is_correct = False
        val_clean = answer_text.strip().lower()
        if val_clean in ['a', 'b', 'c', 'd']:
            is_correct = (q.correct_answer.strip().lower() == val_clean)
        else:
            correct_text = getattr(q, f"option_{q.correct_answer.strip().lower()}", "")
            if correct_text and correct_text.strip().lower() == val_clean:
                is_correct = True
                
        multiplier = DIFFICULTY_CONFIG[room['difficulty']]['score_multiplier']
        time_limit = get_round_time_limit(room)
        
        score = 0
        if is_correct:
            time_bonus = max(0.0, (time_limit - time_taken) / time_limit)
            base_score = 100
            score = int(base_score * multiplier * (0.5 + 0.5 * time_bonus))
            
            p['score'] += score
            if not p.get('used_lifeline_on_this'):
                p['streak'] += 1
                if p['streak'] > p['best_streak']:
                    p['best_streak'] = p['streak']
            p['articles_correct'].add(q.article_id)
        else:
            p['streak'] = 0
            p['wrong_answers'] += 1
            
        p['total_time'] += time_taken
        
        room['player_answers_submitted'][sid] = {
            'answer': answer_text,
            'is_correct': is_correct,
            'score': score,
            'time_taken': time_taken
        }
        
        if p['user_id']:
            try:
                ans_log = PlayerAnswer(
                    user_id=p['user_id'],
game_id=room['game_id'],
                    question_id=q.id,
                    article_id=q.article_id,
                    is_correct=is_correct,
                    time_taken=time_taken,
                    difficulty=room['difficulty']
                )
                db_session.add(ans_log)
                db_session.commit()
            except Exception as e:
                print("Error logging answer:", e)
                db_session.rollback()
                
        emit('streak_update', {
            'streak': p['streak'],
            'is_correct': is_correct,
            'explanation': q.explanation,
            'article_name': q.article_name
        })
        
        active_sids = get_active_player_sids(room)
        active_answered = [s for s in active_sids if s in room['player_answers_submitted']]
        if len(active_answered) == len(active_sids) and len(active_sids) > 0:
            if room.get('timer_thread'):
                room['timer_thread'].cancel()
            reveal_answers(room_code)
    except Exception as e:
        emit('error', {'message': f"Lỗi nộp câu trả lời: {str(e)}"})

@socketio.on('use_lifeline')
def on_use_lifeline(data):
    try:
        sid = request.sid
        room_code = get_room_by_sid(sid)
        if not room_code:
            return
        room = rooms[room_code]
        p = room['players'].get(sid)
        if not p or not room['active_question']:
            return
        if room.get('tournament_mode') and sid not in get_active_player_sids(room):
            return

        lifeline_type = data.get('type')
        if not lifeline_type or p['used_lifelines'].get(lifeline_type):
            return
            
        p['used_lifelines'][lifeline_type] = True
        p['used_lifeline_on_this'] = True
        
        q = room['active_question']
        
        if lifeline_type == 'fifty_fifty':
            wrong_options = []
            for opt in ['a', 'b', 'c', 'd']:
                if opt != q.correct_answer.strip().lower():
                    wrong_options.append(opt)
            remove_options = random.sample(wrong_options, 2)
            emit('fifty_fifty_result', {
                'remove_options': remove_options
            })
        elif lifeline_type == 'hint':
            hint = q.explanation.split('.')[0] + '.'
            emit('hint_result', {
                'hint': hint
            })
    except Exception as e:
        emit('error', {'message': f"Lỗi dùng lifeline: {str(e)}"})

@socketio.on('skip_break')
def on_skip_break():
    try:
        sid = request.sid
        room_code = get_room_by_sid(sid)
        if not room_code:
            return
        with room_lock:
            room = rooms[room_code]
            if room['host_sid'] != sid:
                emit('error', {'message': 'Chỉ trưởng phòng mới có thể bỏ qua thời gian nghỉ!'})
                return
            if not room.get('in_break'):
                return
next_round = room['current_round'] + 1
            room['in_break'] = False
            room['break_remaining'] = 0
        if next_round <= 4:
            start_tournament_round(room_code, next_round)
    except Exception as e:
        emit('error', {'message': f"Lỗi bỏ qua thời gian nghỉ: {str(e)}"})

@socketio.on('leave_room')
def on_leave_room():
    sid = request.sid
    room_code = get_room_by_sid(sid)
    if not room_code:
        return
    handle_player_departure(sid, room_code)

@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid
    room_code = get_room_by_sid(sid)
    if not room_code:
        return
    handle_player_departure(sid, room_code)

def handle_player_departure(sid, room_code):
    try:
        with room_lock:
            if room_code not in rooms:
                return
            room = rooms[room_code]
            if sid in room['players']:
                player = room['players'].pop(sid)
                leave_room(room_code, sid=sid)
                
        socketio.emit('player_left', {
            'sid': sid,
            'name': player['name'],
            'players': get_room_players_list(room_code)
        }, to=room_code)
        
        emit_room_state(room_code)
        
        if not room['players']:
            if room.get('timer_thread'):
                room['timer_thread'].cancel()
            with room_lock:
                rooms.pop(room_code, None)
        elif room['host_sid'] == sid:
            next_host = list(room['players'].keys())[0]
            room['host_sid'] = next_host
            socketio.emit('new_host', {
                'host_sid': next_host
            }, to=room_code)
    except Exception as e:
        print("Error handling player departure:", e)