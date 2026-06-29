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
from app.round1_questions import (
    ROUND1_ANSWER_SECONDS,
    ROUND1_QUESTIONS_PER_PLAYER,
    ROUND1_READ_SECONDS,
    allocate_round1_questions,
)
from app.round2_questions import (
    ROUND2_ANSWER_SECONDS,
    ROUND2_QUESTIONS_PER_TEAM,
    ROUND2_READ_SECONDS,
    allocate_round2_questions,
)

# SocketIO object initialized without app, will be initialized via init_app in app/__init__.py
socketio = SocketIO(cors_allowed_origins="*", async_mode='threading', logger=False, engineio_logger=False)

room_lock = Lock()
rooms = {}
TEAM_COUNT = 10
TEAM_SIZE = 6
MAX_PLAYERS_PER_ROOM = TEAM_COUNT * TEAM_SIZE
INTRO_SCENE_SECONDS = 12
ROUND_INTRO_SECONDS = 30

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
        'teams_advance': 7,
        'question_count': ROUND1_QUESTIONS_PER_PLAYER,
        'time_per_question': ROUND1_ANSWER_SECONDS,
        'read_seconds': ROUND1_READ_SECONDS,
        'break_seconds': 10,
        'description': '10 đội tham gia, chọn 7 đội may mắn đi tiếp và 3 đội bị loại',
    },
    2: {
        'name': 'Vòng 2 — Bán kết',
        'teams_in': 7,
        'teams_advance': 5,
        'question_count': ROUND2_QUESTIONS_PER_TEAM,
        'time_per_question': ROUND2_ANSWER_SECONDS,
        'read_seconds': ROUND2_READ_SECONDS,
        'break_seconds': 10,
        'description': '7 đội theo 7 chủ đề, chọn 5 đội đi tiếp',
    },
    3: {
        'name': 'Vòng 3 — Phát hiện tấn công',
        'teams_in': 3,
        'teams_advance': 2,
        'question_count': 6,
        'time_per_question': 20,
        'break_seconds': 10,
        'description': '3 đội phân tích hình ảnh, chỉ ra dấu hiệu tấn công mạng',
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
                emit('error', {'message': 'Phòng đã đủ 60 người!'})
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
                if not room['players'][sid].get('team'):
                    emit('error', {'message': 'Bạn cần chọn đội trước khi sẵn sàng!'})
                    return
                room['players'][sid]['is_ready'] = ready
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
                emit('error', {'message': f'Đội {team_id} đã đủ {TEAM_SIZE} người!'})
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
        players_to_check = room['players']
        if not players_to_check:
            emit('error', {'message': 'Phòng chưa có người chơi tham gia!'})
            return
        if any(not p.get('team') for p in players_to_check.values()):
            emit('error', {'message': 'Tất cả người chơi cần chọn đội trước khi bắt đầu!'})
            return
        if any(not p.get('is_ready') for p in players_to_check.values()):
            emit('error', {'message': 'Tất cả người chơi cần sẵn sàng trước khi bắt đầu!'})
            return

        if room.get('tournament_mode', True):
            teams_present = get_teams_with_players(room)
            if len(teams_present) < 1:
                emit('error', {'message': 'Giải đấu cần ít nhất 1 đội có người chơi!'})
                return

        room['started'] = True
        room['game_id'] = secrets.token_hex(8)
        socketio.emit('show_scene', {
            'url': f'/game/{room_code}/scene',
            'seconds': INTRO_SCENE_SECONDS
        }, to=room_code)
        socketio.sleep(INTRO_SCENE_SECONDS)

        if room.get('tournament_mode', True):
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
    if round_num == 1:
        room['round1_assignments'] = allocate_round1_questions(room['players'])
        room['round1_question_index'] = 0
        room['questions'] = []
        room['current_index'] = 0
        return
    if round_num == 2:
        room['round2_assignments'] = allocate_round2_questions(room.get('active_teams') or set())
        room['round2_question_index'] = 0
        room['questions'] = []
        room['current_index'] = 0
        return
    if round_num == 3:
        try:
            import os
            q_count = cfg['question_count']
            json_path = os.path.join(os.path.dirname(__file__), 'static', 'round3_cases.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                cases = json.load(f)
            random.shuffle(cases)
            room['questions'] = cases[:q_count]
            room['current_index'] = 0
        except Exception as e:
            print("Error loading round 3 cases:", e)
            room['questions'] = []
            room['current_index'] = 0
        return

    if round_num == 4:
        try:
            import os
            json_path = os.path.join(os.path.dirname(__file__), 'static', 'round4_incidents.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                incidents = json.load(f)
            random.shuffle(incidents)
            room['questions'] = incidents[0]['missions']
            room['active_incident'] = incidents[0]
            room['current_index'] = 0
            
            active_teams = list(room.get('active_teams') or get_teams_with_players(room))
            if len(active_teams) < 2:
                all_teams = get_teams_with_players(room)
                active_teams = list(all_teams)[:2]
            
            room['round4_team_states'] = {}
            for team_id in active_teams:
                members = [sid for sid, p in room['players'].items() if p.get('team') == team_id]
                members.sort()
                
                room['round4_team_states'][team_id] = {
                    'current_mission_index': 0,
                    'scores': [0] * 5,
                    'times': [0.0] * 5,
                    'hints_used': [False] * 5,
                    'perfect_missions': [False] * 5,
                    'completed': False,
                    'current_player_sid': None,
                    'active_players_list': members,
                    'timer_remaining': 20,
                    'timer_active': False
                }
        except Exception as e:
            print("Error loading round 4 incidents:", e)
            room['questions'] = []
            room['current_index'] = 0
        return

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
        round_lifelines = [] if round_num == 1 else DIFFICULTY_CONFIG[diff]['lifelines']
        socketio.emit('round_started', {
            'round': round_num,
            'round_name': cfg['name'],
            'round_description': cfg['description'],
            'question_count': cfg['question_count'],
            'time_per_question': cfg['time_per_question'],
            'teams_active': sorted(room['active_teams']),
            'teams_eliminated': sorted(room.get('eliminated_teams') or set()),
            'difficulty': diff,
            'lifelines': round_lifelines,
            'tournament_mode': True,
            'total_rounds': 4,
            'team_rankings': build_tournament_leaderboard_payload(room),
        }, to=room_code)

        socketio.emit('game_started', {
            'question_count': cfg['question_count'],
            'difficulty': diff,
            'lifelines': round_lifelines,
            'tournament_mode': True,
            'round': round_num,
            'round_name': cfg['name'],
            'round_description': cfg.get('description', ''),
            'round_intro_seconds': ROUND_INTRO_SECONDS,
        }, to=room_code)

        socketio.sleep(ROUND_INTRO_SECONDS)
        send_next_question(room_code)
    except Exception as e:
        socketio.emit('error', {'message': f"Lỗi bắt đầu vòng đấu: {str(e)}"}, to=room_code)

def send_next_round1_question(room_code):
    try:
        with room_lock:
            if room_code not in rooms:
                return
            room = rooms[room_code]

        idx = room.get('round1_question_index', 0)
        if idx >= ROUND1_QUESTIONS_PER_PLAYER:
            end_tournament_round(room_code)
            return

        active_sids = get_active_player_sids(room)
        room['round1_question_index'] = idx + 1
        room['current_index'] = idx + 1
        room['player_answers_submitted'] = {}
        room['active_questions'] = {}
        room['active_question'] = True
        room['question_start_time'] = time.time()
        room['round1_phase'] = 'reading'

        cfg = TOURNAMENT_ROUND_CONFIG[1]
        for sid in active_sids:
            q = (room.get('round1_assignments') or {}).get(sid, [])[idx]
            room['active_questions'][sid] = q
            if sid in room['players']:
                room['players'][sid]['used_lifeline_on_this'] = False
            socketio.emit('new_question', {
                'id': q.id,
                'question': q.content,
                'options': [q.option_a, q.option_b, q.option_c, q.option_d],
                'article': q.article_name,
                'article_name': q.article_name,
                'difficulty': q.difficulty,
                'current_q': idx + 1,
                'total_q': ROUND1_QUESTIONS_PER_PLAYER,
                'round': 1,
                'round_name': cfg['name'],
                'time_per_question': ROUND1_ANSWER_SECONDS,
                'read_seconds': ROUND1_READ_SECONDS,
                'answer_seconds': ROUND1_ANSWER_SECONDS,
                'answer_locked': True,
            }, to=sid)

        room['timer_active'] = True

        def run_round1_timer(rc, q_idx):
            try:
                for t in range(ROUND1_READ_SECONDS, -1, -1):
                    with room_lock:
                        if rc not in rooms:
                            return
                        rm = rooms[rc]
                        if not rm['started'] or rm['current_index'] != q_idx or not rm.get('timer_active'):
                            return
                    socketio.emit('reading_tick', {'remaining': t}, to=rc)
                    if t > 0:
                        socketio.sleep(1.0)

                with room_lock:
                    if rc not in rooms:
                        return
                    rooms[rc]['round1_phase'] = 'answer'
                socketio.emit('answer_phase_started', {
                    'seconds': ROUND1_ANSWER_SECONDS,
                }, to=rc)

                for t in range(ROUND1_ANSWER_SECONDS, -1, -1):
                    with room_lock:
                        if rc not in rooms:
                            return
                        rm = rooms[rc]
                        if not rm['started'] or rm['current_index'] != q_idx or not rm.get('timer_active'):
                            return
                    socketio.emit('timer_tick', t, to=rc)
                    if t == 0:
                        handle_round1_question_timeout(rc)
                        return
                    socketio.sleep(1.0)
            except Exception as ex:
                print("Error in round 1 timer:", ex)

        socketio.start_background_task(run_round1_timer, room_code, room['current_index'])
    except Exception as e:
        socketio.emit('error', {'message': f"Lỗi chuyển câu vòng 1: {str(e)}"}, to=room_code)

def handle_round1_question_timeout(room_code):
    try:
        with room_lock:
            if room_code not in rooms:
                return
            room = rooms[room_code]
            if not room.get('active_questions'):
                return

        limit = ROUND1_ANSWER_SECONDS
        for sid in get_active_player_sids(room):
            p = room['players'].get(sid)
            q = room.get('active_questions', {}).get(sid)
            if not p or not q or sid in room['player_answers_submitted']:
                continue
            p['streak'] = 0
            p['wrong_answers'] += 1
            p['total_time'] += float(limit)
            socketio.emit('streak_update', {
                'streak': 0,
                'is_correct': False,
                'explanation': q.explanation,
                'article_name': q.article_name
            }, to=sid)

        reveal_round1_answers(room_code)
    except Exception as e:
        print("Error handling round 1 timeout:", e)

def reveal_round1_answers(room_code):
    try:
        with room_lock:
            if room_code not in rooms:
                return
            room = rooms[room_code]
            active_questions = dict(room.get('active_questions') or {})
            room['active_questions'] = {}
            room['active_question'] = None
            room['timer_active'] = False
            room['round1_phase'] = None

        scores_update = {sid: p['score'] for sid, p in room['players'].items()}
        for sid, q in active_questions.items():
            socketio.emit('answer_result', {
                'correct_answer': q.correct_answer.strip().lower(),
                'explanation': q.explanation,
                'article_name': q.article_name,
                'scores': scores_update
            }, to=sid)

        socketio.emit('leaderboard_update', {
            'players': get_room_players_list(room_code),
            'team_rankings': build_tournament_leaderboard_payload(room),
            'tournament_mode': True,
            'current_round': 1,
        }, to=room_code)

        def auto_advance(rc):
            socketio.sleep(2.0)
            send_next_question(rc)

        socketio.start_background_task(auto_advance, room_code)
    except Exception as e:
        print("Error revealing round 1 answers:", e)

def send_next_round2_question(room_code):
    try:
        with room_lock:
            if room_code not in rooms:
                return
            room = rooms[room_code]

        idx = room.get('round2_question_index', 0)
        if idx >= ROUND2_QUESTIONS_PER_TEAM:
            end_tournament_round(room_code)
            return

        room['round2_question_index'] = idx + 1
        room['current_index'] = idx + 1
        room['player_answers_submitted'] = {}
        room['active_questions'] = {}
        room['active_question'] = True
        room['question_start_time'] = time.time()
        room['round_custom_phase'] = 'reading'

        cfg = TOURNAMENT_ROUND_CONFIG[2]
        active_sids = get_active_player_sids(room)
        for sid in active_sids:
            player = room['players'].get(sid)
            team_id = player.get('team') if player else None
            pack = (room.get('round2_assignments') or {}).get(team_id)
            if not pack:
                continue
            q = pack['questions'][idx]
            room['active_questions'][sid] = q
            player['used_lifeline_on_this'] = False
            socketio.emit('new_question', {
                'id': q.id,
                'question': q.content,
                'options': [q.option_a, q.option_b, q.option_c],
                'article': pack['title'],
                'article_name': q.article_name,
                'difficulty': q.difficulty,
                'current_q': idx + 1,
                'total_q': ROUND2_QUESTIONS_PER_TEAM,
                'round': 2,
                'round_name': cfg['name'],
                'time_per_question': ROUND2_ANSWER_SECONDS,
                'read_seconds': ROUND2_READ_SECONDS,
                'answer_seconds': ROUND2_ANSWER_SECONDS,
                'answer_locked': True,
            }, to=sid)

        room['timer_active'] = True
        socketio.start_background_task(
            run_custom_round_timer,
            room_code,
            room['current_index'],
            ROUND2_READ_SECONDS,
            ROUND2_ANSWER_SECONDS,
            handle_custom_question_timeout,
        )
    except Exception as e:
        socketio.emit('error', {'message': f"Lỗi chuyển câu vòng 2: {str(e)}"}, to=room_code)

def run_custom_round_timer(room_code, question_index, read_seconds, answer_seconds, timeout_handler):
    try:
        for t in range(read_seconds, -1, -1):
            with room_lock:
                if room_code not in rooms:
                    return
                room = rooms[room_code]
                if not room['started'] or room['current_index'] != question_index or not room.get('timer_active'):
                    return
            socketio.emit('reading_tick', {'remaining': t}, to=room_code)
            if t > 0:
                socketio.sleep(1.0)

        with room_lock:
            if room_code not in rooms:
                return
            rooms[room_code]['round_custom_phase'] = 'answer'
        socketio.emit('answer_phase_started', {'seconds': answer_seconds}, to=room_code)

        for t in range(answer_seconds, -1, -1):
            with room_lock:
                if room_code not in rooms:
                    return
                room = rooms[room_code]
                if not room['started'] or room['current_index'] != question_index or not room.get('timer_active'):
                    return
            socketio.emit('timer_tick', t, to=room_code)
            if t == 0:
                timeout_handler(room_code)
                return
            socketio.sleep(1.0)
    except Exception as ex:
        print("Error in custom round timer:", ex)

def handle_custom_question_timeout(room_code):
    try:
        with room_lock:
            if room_code not in rooms:
                return
            room = rooms[room_code]
            if not room.get('active_questions'):
                return
            limit = get_round_time_limit(room)

        for sid in get_active_player_sids(room):
            p = room['players'].get(sid)
            q = room.get('active_questions', {}).get(sid)
            if not p or not q or sid in room['player_answers_submitted']:
                continue
            p['streak'] = 0
            p['wrong_answers'] += 1
            p['total_time'] += float(limit)
            socketio.emit('streak_update', {
                'streak': 0,
                'is_correct': False,
                'explanation': q.explanation,
                'article_name': q.article_name
            }, to=sid)

        reveal_custom_answers(room_code)
    except Exception as e:
        print("Error handling custom round timeout:", e)

def reveal_custom_answers(room_code):
    try:
        with room_lock:
            if room_code not in rooms:
                return
            room = rooms[room_code]
            active_questions = dict(room.get('active_questions') or {})
            current_round = room.get('current_round', 0)
            room['active_questions'] = {}
            room['active_question'] = None
            room['timer_active'] = False
            room['round_custom_phase'] = None

        scores_update = {sid: p['score'] for sid, p in room['players'].items()}
        for sid, q in active_questions.items():
            socketio.emit('answer_result', {
                'correct_answer': q.correct_answer.strip().lower(),
                'explanation': q.explanation,
                'article_name': q.article_name,
                'scores': scores_update
            }, to=sid)

        socketio.emit('leaderboard_update', {
            'players': get_room_players_list(room_code),
            'team_rankings': build_tournament_leaderboard_payload(room),
            'tournament_mode': True,
            'current_round': current_round,
        }, to=room_code)

        def auto_advance(rc):
            socketio.sleep(2.0)
            send_next_question(rc)

        socketio.start_background_task(auto_advance, room_code)
    except Exception as e:
        print("Error revealing custom round answers:", e)

def send_next_round3_case(room_code):
    try:
        with room_lock:
            if room_code not in rooms:
                return
            room = rooms[room_code]

        idx = room['current_index']
        if idx >= len(room['questions']):
            end_tournament_round(room_code)
            return

        case = room['questions'][idx]
        room['active_question'] = case
        room['current_index'] += 1
        room['player_answers_submitted'] = {}
        room['question_start_time'] = time.time()

        for p in room['players'].values():
            p['used_lifeline_on_this'] = False

        payload = {
            'id': case['id'],
            'type': case['type'],
            'title': case['title'],
            'image': case['image'],
            'question': case['question'],
            'time_per_question': case.get('time', 30),
            'score': case.get('score', 100),
            'current_q': room['current_index'],
            'total_q': len(room['questions']),
            'round': 3,
            'round_name': TOURNAMENT_ROUND_CONFIG[3]['name'],
            'tournament_mode': True
        }

        if case['type'] == 'drag_drop':
            payload['items'] = case['items']
            payload['targets'] = case['targets']
        elif case['type'] == 'connect':
            payload['left_items'] = case['left_items']
            payload['right_items'] = case['right_items']
        elif case['type'] == 'timeline':
            payload['events'] = case['events']
        elif case['type'] == 'multiple_hotspots':
            payload['hotspots'] = [{'id': h['id']} for h in case['hotspots']]

        socketio.emit('new_question', payload, to=room_code)

        room['timer_active'] = True

        def run_timer(rc, q_idx):
            try:
                with room_lock:
                    if rc not in rooms:
                        return
                    rm = rooms[rc]
                    limit = case.get('time', 30)

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
                print("Error in round 3 timer background task:", ex)

        socketio.start_background_task(run_timer, room_code, room['current_index'])
    except Exception as e:
        socketio.emit('error', {'message': f"Lỗi chuyển vụ án vòng 3: {str(e)}"}, to=room_code)

def send_next_question(room_code):
    try:
        with room_lock:
            if room_code not in rooms:
                return
            room = rooms[room_code]

        if room.get('tournament_mode') and room.get('current_round') == 1:
            send_next_round1_question(room_code)
            return
        if room.get('tournament_mode') and room.get('current_round') == 2:
            send_next_round2_question(room_code)
            return
        if room.get('tournament_mode') and room.get('current_round') == 3:
            send_next_round3_case(room_code)
            return
        if room.get('tournament_mode') and room.get('current_round') == 4:
            send_next_round4_mission(room_code)
            return
            
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
        is_round3 = (room.get('tournament_mode') and room.get('current_round') == 3)
        for sid in active_sids:
            p = room['players'].get(sid)
            if not p:
                continue
            if sid not in room['player_answers_submitted']:
                if p['user_id'] and not is_round3:
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
                
                explanation = room['active_question'].get('explanation', 'Không có giải thích.') if is_round3 else room['active_question'].explanation
                title = room['active_question'].get('title', 'Vụ án') if is_round3 else room['active_question'].article_name
                
                socketio.emit('streak_update', {
                    'streak': 0,
                    'is_correct': False,
                    'explanation': explanation,
                    'article_name': title
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
            
        is_round3 = (room.get('tournament_mode') and room.get('current_round') == 3)
        if is_round3:
            correct_key = str(q.get('answer', ''))
            explanation = q.get('explanation', 'Không có giải thích.')
            article_name = q.get('title', 'Vụ án')
        else:
            correct_key = q.correct_answer.strip().lower()
            explanation = q.explanation
            article_name = q.article_name
        
        scores_update = {}
        for sid, p in room['players'].items():
            scores_update[sid] = p['score']
            
        socketio.emit('answer_result', {
            'round': room.get('current_round', 0),
            'correct_answer': correct_key,
            'explanation': explanation,
            'article_name': article_name,
            'scores': scores_update,
            'correct_details': q.get('answer') if is_round3 else None
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

@socketio.on('next_round3_case')
def on_next_round3_case():
    try:
        sid = request.sid
        room_code = get_room_by_sid(sid)
        if not room_code:
            return
        room = rooms[room_code]
        if room['host_sid'] != sid:
            emit('error', {'message': 'Chỉ có quản trị viên mới chuyển vụ án tiếp theo!'})
            return
        if room.get('current_round') != 3:
            return
        send_next_round3_case(room_code)
    except Exception as e:
        emit('error', {'message': f"Lỗi chuyển vụ án: {str(e)}"})

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

def schedule_room_cleanup(room_code):
    def cleanup():
        socketio.sleep(15.5)
        try:
            with room_lock:
                if room_code in rooms:
                    room = rooms[room_code]
                    print(f"[CLEANUP] Automatically cleaning up room {room_code} and force-redirecting players.")
                    if room.get('timer_thread'):
                        try:
                            room['timer_thread'].cancel()
                        except Exception:
                            pass
                    socketio.emit('force_redirect', {'url': '/'}, to=room_code)
                    rooms.pop(room_code, None)
        except Exception as e:
            print(f"Error in room cleanup for {room_code}: {e}")
            
    socketio.start_background_task(cleanup)

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
        schedule_room_cleanup(room_code)
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
        schedule_room_cleanup(room_code)
    except Exception as e:
        print("Error ending game:", e)

def validate_round3_case(case, submitted_answer):
    case_type = case['type']
    ans_correct = case['answer']
    
    evaluation = "Wrong"
    score_ratio = 0.0
    correct_details = None
    
    try:
        if case_type in ('click', 'image_hotspot', 'image_comparison'):
            if isinstance(submitted_answer, dict) and 'x' in submitted_answer and 'y' in submitted_answer:
                dist = ((submitted_answer['x'] - ans_correct['x'])**2 + (submitted_answer['y'] - ans_correct['y'])**2)**0.5
                if dist <= ans_correct['radius']:
                    evaluation = "Correct"
                    score_ratio = 1.0
            correct_details = ans_correct

        elif case_type == 'highlight':
            if (isinstance(submitted_answer, dict) and all(k in submitted_answer for k in ('x1', 'y1', 'x2', 'y2'))):
                ox1 = max(submitted_answer['x1'], ans_correct['x1'])
                oy1 = max(submitted_answer['y1'], ans_correct['y1'])
                ox2 = min(submitted_answer['x2'], ans_correct['x2'])
                oy2 = min(submitted_answer['y2'], ans_correct['y2'])
                
                if ox2 > ox1 and oy2 > oy1:
                    overlap_area = (ox2 - ox1) * (oy2 - oy1)
                    correct_area = (ans_correct['x2'] - ans_correct['x1']) * (ans_correct['y2'] - ans_correct['y1'])
                    if correct_area > 0 and (overlap_area / correct_area) >= 0.5:
                        evaluation = "Correct"
                        score_ratio = 1.0
            correct_details = ans_correct

        elif case_type in ('drag_drop', 'connect'):
            if isinstance(submitted_answer, dict):
                correct_count = 0
                total_items = len(ans_correct)
                for item_id, correct_target in ans_correct.items():
                    if submitted_answer.get(item_id) == correct_target:
                        correct_count += 1
                
                if correct_count == total_items:
                    evaluation = "Correct"
                    score_ratio = 1.0
                elif correct_count > 0:
                    evaluation = "Partial Score"
                    score_ratio = correct_count / total_items
            correct_details = ans_correct

        elif case_type in ('timeline', 'sequence_builder'):
            if isinstance(submitted_answer, list):
                correct_count = 0
                total_events = len(ans_correct)
                for idx, ev_id in enumerate(ans_correct):
                    if idx < len(submitted_answer) and submitted_answer[idx] == ev_id:
                        correct_count += 1
                
                if correct_count == total_events:
                    evaluation = "Correct"
                    score_ratio = 1.0
                elif correct_count > 0:
                    evaluation = "Partial Score"
                    score_ratio = correct_count / total_events
            correct_details = ans_correct

        elif case_type == 'text_input':
            if isinstance(submitted_answer, str):
                if submitted_answer.strip().upper() == ans_correct.strip().upper():
                    evaluation = "Correct"
                    score_ratio = 1.0
            correct_details = ans_correct

        elif case_type == 'multiple_hotspots':
            if isinstance(submitted_answer, list):
                correct_clicked = 0
                total_correct = len(ans_correct)
                for h_id in ans_correct:
                    if h_id in submitted_answer:
                        correct_clicked += 1
                extra_clicks = len(submitted_answer) - correct_clicked
                net_correct = max(0, correct_clicked - extra_clicks)
                
                if net_correct == total_correct:
                    evaluation = "Correct"
                    score_ratio = 1.0
                elif net_correct > 0:
                    evaluation = "Partial Score"
                    score_ratio = net_correct / total_correct
            correct_details = {
                'hotspots': case['hotspots'],
                'answer': ans_correct
            }
            
    except Exception as e:
        print("Error validating round 3 case:", e)
        
    return evaluation, score_ratio, correct_details

@socketio.on('submit_answer')
def on_submit_answer(data):
    try:
        sid = request.sid
        room_code = get_room_by_sid(sid)
        if not room_code:
            return
        room = rooms[room_code]
        p = room['players'].get(sid)
        current_round = room.get('current_round') if room.get('tournament_mode') else 0
        is_round1 = current_round == 1
        is_custom_round = room.get('tournament_mode') and current_round in (1, 2)
        q = (room.get('active_questions') or {}).get(sid) if is_custom_round else room.get('active_question')
        if not p or not q:
            return
        if sid in room['player_answers_submitted']:
            return
        if room.get('tournament_mode') and sid not in get_active_player_sids(room):
            return
        if is_round1 and room.get('round1_phase') != 'answer':
            return
        if is_custom_round and not is_round1 and room.get('round_custom_phase') != 'answer':
            return
            
        answer_text = data.get('answer', '') or data.get('round3_answer', '')
        time_taken = float(data.get('time_taken', 0.0))

        if current_round == 4:
            handle_round4_answer_submission(room, sid, data)
            return

        if current_round == 3:
            evaluation, score_ratio, correct_details = validate_round3_case(q, answer_text)
            is_correct = (evaluation == "Correct")
            score = 1 if is_correct else 0
            p['score'] += score

            if is_correct:
                p['streak'] += 1
                if p['streak'] > p['best_streak']:
                    p['best_streak'] = p['streak']
            else:
                p['streak'] = 0
                p['wrong_answers'] += 1

            p['total_time'] += time_taken
            room['player_answers_submitted'][sid] = {
                'answer': answer_text,
                'is_correct': is_correct,
                'score': score,
                'time_taken': time_taken,
                'evaluation': evaluation
            }

            emit('answer_result', {
                'round': 3,
                'is_correct': is_correct,
                'score': score,
                'partial_score': 0,
                'evaluation': evaluation,
                'explanation': q.get('explanation', 'Không có giải thích vụ án.'),
                'correct_details': correct_details
            })
            emit('streak_update', {
                'streak': p['streak'],
                'is_correct': is_correct,
                'new_badges': []
            })

            active_sids = get_active_player_sids(room)
            progress = []
            for s in active_sids:
                player_info = room['players'].get(s)
                if player_info:
                    progress.append({
                        'sid': s,
                        'name': player_info['name'],
                        'team': player_info.get('team'),
                        'answered': (s in room['player_answers_submitted'])
                    })
            socketio.emit('answers_progress_update', {
                'progress': progress
            }, to=room_code)

            active_answered = [s for s in active_sids if s in room['player_answers_submitted']]
            if len(active_answered) == len(active_sids) and len(active_sids) > 0:
                if room.get('timer_thread'):
                    room['timer_thread'].cancel()
                reveal_answers(room_code)
            return

        is_correct = False
        val_clean = answer_text.strip().lower()
        if val_clean in ['a', 'b', 'c', 'd']:
            is_correct = (q.correct_answer.strip().lower() == val_clean)
        else:
            correct_text = getattr(q, f"option_{q.correct_answer.strip().lower()}", "")
            if correct_text and correct_text.strip().lower() == val_clean:
                is_correct = True
                
        score = 1 if is_correct else 0
        if is_correct:
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
        
        if p['user_id'] and not getattr(q, 'is_static_round', False):
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
        
        # Broadcast answers progress
        active_sids = get_active_player_sids(room)
        progress = []
        for s in active_sids:
            player_info = room['players'].get(s)
            if player_info:
                progress.append({
                    'sid': s,
                    'name': player_info['name'],
                    'team': player_info.get('team'),
                    'answered': (s in room['player_answers_submitted'])
                })
        socketio.emit('answers_progress_update', {
            'progress': progress
        }, to=room_code)
        active_answered = [s for s in active_sids if s in room['player_answers_submitted']]
        if len(active_answered) == len(active_sids) and len(active_sids) > 0:
            if room.get('timer_thread'):
                room['timer_thread'].cancel()
            if is_round1:
                reveal_round1_answers(room_code)
            elif is_custom_round:
                reveal_custom_answers(room_code)
            else:
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
        if not p:
            return
        current_round = room.get('current_round') if room.get('tournament_mode') else 0
        if current_round == 4:
            handle_round4_hint_request(room, sid, data)
            return

        if not room['active_question']:
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

@socketio.on('reset_game')
def on_reset_game():
    try:
        sid = request.sid
        room_code = get_room_by_sid(sid)
        if not room_code:
            return
        with room_lock:
            room = rooms[room_code]
            if room['host_sid'] != sid:
                emit('error', {'message': 'Chỉ có quản trị viên mới có thể dừng hoặc reset game!'})
                return
            
            if room.get('timer_thread'):
                room['timer_thread'].cancel()
                room['timer_thread'] = None
            
            room['started'] = False
            room['in_break'] = False
            room['questions'] = []
            room['current_index'] = 0
            room['active_question'] = None
            room['question_start_time'] = 0
            room['player_answers_submitted'] = {}
            room['timer_active'] = False
            
            for p in room['players'].values():
                p['score'] = 0
                p['streak'] = 0
                p['best_streak'] = 0
                p['articles_correct'] = set()
                p['wrong_answers'] = 0
                p['total_time'] = 0.0
                p['used_lifelines'] = {'fifty_fifty': False, 'hint': False}
                p['used_lifeline_on_this'] = False
                p['is_ready'] = False
            
            if room.get('tournament_mode'):
                init_tournament_room_state(room)
        
        socketio.emit('game_reset', to=room_code)
        emit_room_state(room_code)
    except Exception as e:
        emit('error', {'message': f"Lỗi reset game: {str(e)}"})

# ==========================================================================
# CYBER INCIDENT RESPONSE ENGINE (VÒNG 4) - BACKEND SERVICES
# ==========================================================================

def send_next_round4_mission(room_code):
    try:
        with room_lock:
            if room_code not in rooms:
                return
            room = rooms[room_code]
        
        active_teams = list(room.get('round4_team_states', {}).keys())
        for team_id in active_teams:
            start_team_round4_mission(room_code, team_id)
    except Exception as e:
        print("Error in send_next_round4_mission:", e)

def start_team_round4_mission(room_code, team_id):
    try:
        with room_lock:
            if room_code not in rooms:
                return
            room = rooms[room_code]
            team_state = room.get('round4_team_states', {}).get(team_id)
            if not team_state or team_state['completed']:
                return

            mission_idx = team_state['current_mission_index']
            if mission_idx >= 5:
                team_state['completed'] = True
                # End the round immediately when any team completes their missions
                end_round4_grand_final(room_code)
                return

            mission = room['questions'][mission_idx]
            members = team_state['active_players_list']
            if not members:
                team_state['completed'] = True
                return

            player_order = mission.get('player_order', mission_idx + 1)
            member_idx = (player_order - 1) % len(members)
            active_sid = members[member_idx]
            time_limit = mission.get('time', TOURNAMENT_ROUND_CONFIG[4]['time_per_question'])
            team_state['current_player_sid'] = active_sid
            team_state['timer_remaining'] = time_limit
            
            payload = {
                'incident_title': room['active_incident']['title'],
                'incident_story': room['active_incident']['story'],
                'incident_background': room['active_incident']['background'],
                'difficulty': room['active_incident']['difficulty'],
                'mission_id': mission['id'],
                'mission_index': mission_idx + 1,
                'total_missions': 5,
                'type': mission['type'],
                'instruction': mission['question'],
                'image': mission['image'],
                'time_limit': time_limit,
                'active_player_sid': active_sid,
                'active_player_name': room['players'][active_sid]['name'],
                'opponent_progress': get_opponent_progress_payload(room, team_id),
                'teammate_progress': get_teammate_progress_payload(room, team_id),
                'team_score': get_team_total_score(room, team_id),
                'round': 4,
                'round_name': TOURNAMENT_ROUND_CONFIG[4]['name'],
                'tournament_mode': True
            }

            if mission['type'] == 'drag_drop':
                payload['items'] = mission['items']
                payload['targets'] = mission['targets']
            elif mission['type'] in ('timeline', 'sequence_builder'):
                payload['events'] = mission['events']
            elif mission['type'] == 'image_comparison':
                payload['image_left'] = mission['image_left']
                payload['image_right'] = mission['image_right']

            for sid in members:
                socketio.emit('new_round4_mission', payload, to=sid)

        if room.get('host_sid'):
            socketio.emit('host_round4_update', get_host_round4_payload(room), to=room['host_sid'])

        socketio.start_background_task(run_team_round4_timer, room_code, team_id, mission_idx, time_limit)

    except Exception as e:
        print(f"Error in start_team_round4_mission for team {team_id}:", e)

def run_team_round4_timer(room_code, team_id, mission_idx, time_limit=20):
    try:
        for remaining in range(time_limit, -1, -1):
            socketio.sleep(1.0)
            with room_lock:
                if room_code not in rooms:
                    return
                room = rooms[room_code]
                team_state = room.get('round4_team_states', {}).get(team_id)
                if not team_state or team_state['completed'] or team_state['current_mission_index'] != mission_idx:
                    return

                team_state['timer_remaining'] = remaining

            for sid in team_state['active_players_list']:
                socketio.emit('round4_timer_tick', {
                    'remaining': remaining,
                    'mission_index': mission_idx + 1
                }, to=sid)

            if remaining == 0:
                auto_submit_round4_timeout(room_code, team_id, mission_idx)
                break
    except Exception as ex:
        print("Error in run_team_round4_timer:", ex)

def auto_submit_round4_timeout(room_code, team_id, mission_idx):
    try:
        with room_lock:
            if room_code not in rooms:
                return
            room = rooms[room_code]
            team_state = room.get('round4_team_states', {}).get(team_id)
            if not team_state or team_state['completed'] or team_state['current_mission_index'] != mission_idx:
                return

            mission = room['questions'][mission_idx]
            
            team_state['scores'][mission_idx] = 0
            team_state['times'][mission_idx] = 20.0
            team_state['perfect_missions'][mission_idx] = False

            for sid in team_state['active_players_list']:
                socketio.emit('round4_mission_result', {
                    'mission_index': mission_idx + 1,
                    'is_correct': False,
                    'score': 0,
                    'explanation': mission.get('explanation', 'Hết thời gian trả lời nhiệm vụ.'),
                    'correct_details': mission.get('answer')
                }, to=sid)

            team_state['current_mission_index'] += 1

        start_team_round4_mission(room_code, team_id)

    except Exception as e:
        print("Error in auto_submit_round4_timeout:", e)

def handle_round4_answer_submission(room, sid, data):
    try:
        p = room['players'].get(sid)
        team_id = p.get('team')
        team_state = room.get('round4_team_states', {}).get(team_id)
        if not team_state or team_state['completed']:
            return

        mission_idx = team_state['current_mission_index']
        if team_state['current_player_sid'] != sid:
            emit('error', {'message': 'Chưa tới lượt của bạn!'})
            return

        mission = room['questions'][mission_idx]
        answer_text = data.get('round3_answer') or data.get('answer', '')
        time_taken = float(data.get('time_taken', 0.0))

        evaluation, score_ratio, correct_details = validate_round3_case(mission, answer_text)
        is_correct = (evaluation == "Correct")

        score = 1 if is_correct else 0

        p['score'] += score
        p['total_time'] += time_taken
        
        team_state['scores'][mission_idx] = score
        team_state['times'][mission_idx] = time_taken
        team_state['perfect_missions'][mission_idx] = is_correct

        for member_sid in team_state['active_players_list']:
            socketio.emit('round4_mission_result', {
                'mission_index': mission_idx + 1,
                'is_correct': is_correct,
                'score': score,
                'explanation': mission.get('explanation', 'Hoàn thành nhiệm vụ.'),
                'correct_details': correct_details
            }, to=member_sid)

        with room_lock:
            team_state['current_mission_index'] += 1

        room_code = get_room_by_sid(sid)
        start_team_round4_mission(room_code, team_id)

    except Exception as e:
        print("Error in handle_round4_answer_submission:", e)

def handle_round4_hint_request(room, sid, data):
    try:
        p = room['players'].get(sid)
        team_id = p.get('team')
        team_state = room.get('round4_team_states', {}).get(team_id)
        if not team_state or team_state['completed']:
            return

        mission_idx = team_state['current_mission_index']
        if team_state['current_player_sid'] != sid:
            emit('error', {'message': 'Chỉ người đang thực hiện lượt mới có thể yêu cầu gợi ý!'})
            return

        team_state['hints_used'][mission_idx] = True
        mission = room['questions'][mission_idx]
        hint_text = mission.get('hint', 'Không có gợi ý cho bước này.')

        for member_sid in team_state['active_players_list']:
            socketio.emit('round4_hint_result', {
                'mission_index': mission_idx + 1,
                'hint': hint_text
            }, to=member_sid)

    except Exception as e:
        print("Error in handle_round4_hint_request:", e)

def get_opponent_progress_payload(room, my_team_id):
    try:
        opponent_team_id = None
        for t_id in room.get('round4_team_states', {}).keys():
            if t_id != my_team_id:
                opponent_team_id = t_id
                break
        
        if not opponent_team_id:
            return None

        opp_state = room['round4_team_states'][opponent_team_id]
        return {
            'team_id': opponent_team_id,
            'current_mission': opp_state['current_mission_index'] + 1,
            'completed': opp_state['completed'],
            'score': get_team_total_score(room, opponent_team_id),
            'progress': [
                'completed' if i < opp_state['current_mission_index'] else ('current' if i == opp_state['current_mission_index'] else 'waiting')
                for i in range(5)
            ]
        }
    except Exception as e:
        print("Error in get_opponent_progress_payload:", e)
        return None

def get_teammate_progress_payload(room, team_id):
    try:
        team_state = room['round4_team_states'][team_id]
        members = team_state['active_players_list']
        progress_list = []
        for idx in range(5):
            player_sid = members[idx % len(members)]
            player_name = room['players'][player_sid]['name']
            
            status = 'waiting'
            if idx < team_state['current_mission_index']:
                status = 'completed'
            elif idx == team_state['current_mission_index']:
                status = 'current'
                
            progress_list.append({
                'mission_index': idx + 1,
                'player_name': player_name,
                'player_sid': player_sid,
                'status': status,
                'score': team_state['scores'][idx]
            })
        return progress_list
    except Exception as e:
        print("Error in get_teammate_progress_payload:", e)
        return []

def get_team_total_score(room, team_id):
    try:
        team_state = room['round4_team_states'][team_id]
        return sum(team_state['scores'])
    except Exception:
        return 0

def get_host_round4_payload(room):
    try:
        states = {}
        for team_id, ts in room.get('round4_team_states', {}).items():
            states[team_id] = {
                'current_mission': ts['current_mission_index'] + 1,
                'completed': ts['completed'],
                'score': get_team_total_score(room, team_id),
                'active_player': room['players'][ts['current_player_sid']]['name'] if ts['current_player_sid'] else 'None',
                'scores': ts['scores'],
                'times': ts['times']
            }
        return {
            'incident_title': room['active_incident']['title'],
            'team_states': states
        }
    except Exception:
        return {}

def end_round4_grand_final(room_code):
    try:
        with room_lock:
            if room_code not in rooms:
                return
            room = rooms[room_code]

        active_teams = list(room['round4_team_states'].keys())
        
        rankings = []
        for team_id in active_teams:
            ts = room['round4_team_states'][team_id]
            total_score = get_team_total_score(room, team_id)
            total_time = sum(ts['times'])
            
            members = [
                {
                    'sid': sid,
                    'name': p['name'],
                    'avatar': p['avatar'],
                    'score': p['score']
                }
                for sid, p in room['players'].items() if p.get('team') == team_id
            ]
            
            rankings.append({
                'team': team_id,
                'name': f'Đội {team_id}',
                'score': total_score,
                'total_time': total_time,
                'accuracy': sum(1 for pm in ts['perfect_missions'] if pm) / 5.0 * 100,
                'avg_time': total_time / 5.0,
                'perfect_missions': sum(1 for pm in ts['perfect_missions'] if pm),
                'members': members
            })

        rankings.sort(key=lambda x: (-x['score'], x['total_time']))
        
        champion_team = rankings[0]['team']
        runner_up_team = rankings[1]['team'] if len(rankings) > 1 else None

        champion_members = rankings[0]['members']
        champion_members.sort(key=lambda x: x['score'], reverse=True)
        mvp_player = champion_members[0] if champion_members else {'name': 'Ẩn danh', 'avatar': '👤', 'score': 0}

        cfg = TOURNAMENT_ROUND_CONFIG[4]
        round_result = {
            'round': 4,
            'round_name': cfg['name'],
            'rankings': rankings,
            'advancing_teams': [champion_team],
            'eliminated_teams': [runner_up_team] if runner_up_team else [],
        }
        room['round_history'].append(round_result)

        # Print results and statistics to server console immediately
        print(f"\n🏆 [ROUND 4 GRAND FINAL RESULTS] ROOM: {room_code}")
        print(f"🥇 CHAMPION TEAM: {champion_team}")
        if runner_up_team:
            print(f"🥈 RUNNER UP TEAM: {runner_up_team}")
        print(f"⭐ MVP: {mvp_player['avatar']} {mvp_player['name']} - {mvp_player['score']} pts")
        print("📊 TEAM STATISTICS:")
        for team_stat in rankings:
            print(f"  - Team {team_stat['team']}: Score={team_stat['score']}, Accuracy={team_stat['accuracy']:.1f}%, Avg Time={team_stat['avg_time']:.1f}s, Perfect Missions={team_stat['perfect_missions']}/5")
        print("="*40 + "\n")

        socketio.emit('round4_game_over', {
            'champion_team': champion_team,
            'runner_up_team': runner_up_team,
            'rankings': rankings,
            'mvp': {
                'name': mvp_player['name'],
                'avatar': mvp_player['avatar'],
                'score': mvp_player['score']
            }
        }, to=room_code)
        schedule_room_cleanup(room_code)

    except Exception as e:
        print("Error in end_round4_grand_final:", e)

