#!/usr/bin/python3
"""The route handler for html pages"""

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for, jsonify
from flask_login import login_required, current_user
from sqlalchemy import text
from datetime import datetime
import json

from app.main.auth import auth
from app.websocket import rooms
from models.category import Category
from models.user import User

FIXED_ROOM_CODE = "2026"
STUDENTS = [
    {"mssv": "2431540347", "name": "Huỳnh Trọng Hiệp", "gender": "Nam", "group": "1"},
    {"mssv": "2431540308", "name": "Hoàng Yến Nhi", "gender": "Nữ", "group": "1"},
    {"mssv": "2431540315", "name": "Lưu Ngọc Thiện", "gender": "Nữ", "group": "1"},
    {"mssv": "2431540340", "name": "Trần Thị Cẩm Tiên", "gender": "Nữ", "group": "1"},
    {"mssv": "2431540329", "name": "Lê Quang Vinh", "gender": "Nam", "group": "1"},
    {"mssv": "2431540067", "name": "Nguyễn Tiến Đạt", "gender": "Nam", "group": "10"},
    {"mssv": "2431540013", "name": "Lê Nguyễn Khôi Nguyên", "gender": "Nam", "group": "10"},
    {"mssv": "2431540012", "name": "Ngô Đồng Quang Nguyên", "gender": "Nam", "group": "10"},
    {"mssv": "2331540316", "name": "Nguyễn Thanh Tuấn", "gender": "Nam", "group": "10"},
    {"mssv": "2431540022", "name": "Trương Quốc Tuấn", "gender": "Nam", "group": "10"},
    {"mssv": "2431540069", "name": "Nguyễn Hoàng Long", "gender": "Nam", "group": "2"},
    {"mssv": "2431540096", "name": "Phạm Minh Nhật", "gender": "Nam", "group": "2"},
    {"mssv": "2431540078", "name": "Đỗ Thị Như Quỳnh", "gender": "Nữ", "group": "2"},
    {"mssv": "2431540084", "name": "Lê Nguyễn Ngọc Tâm", "gender": "Nữ", "group": "2"},
    {"mssv": "2431540111", "name": "Lê Ngọc Khánh Trình", "gender": "Nam", "group": "2"},
    {"mssv": "2431540115", "name": "Mai Ngọc Anh", "gender": "Nam", "group": "3"},
    {"mssv": "2431540120", "name": "Lê Dũng", "gender": "Nam", "group": "3"},
    {"mssv": "2431540117", "name": "Nguyễn Thảo Nhi", "gender": "Nữ", "group": "3"},
    {"mssv": "2431540109", "name": "Nguyễn Tứ Tâm", "gender": "Nam", "group": "3"},
    {"mssv": "2431540234", "name": "Châu Nhựt Tân", "gender": "Nam", "group": "3"},
    {"mssv": "2431540081", "name": "Nguyễn Ngọc Mai Thy", "gender": "Nữ", "group": "3"},
    {"mssv": "2331540055", "name": "LƯƠNG THÁI KHANG", "gender": "Nam", "group": "4"},
    {"mssv": "2431540061", "name": "Phan Tuấn Kiệt", "gender": "Nam", "group": "4"},
    {"mssv": "2331540004", "name": "NGUYỄN MINH SANG", "gender": "Nam", "group": "4"},
    {"mssv": "2431540062", "name": "Bùi Trần Thanh Thiên", "gender": "Nam", "group": "4"},
    {"mssv": "2431540065", "name": "Hồng Lê Minh Thông", "gender": "Nam", "group": "4"},
    {"mssv": "2254810099", "name": "BÙI ĐỨC TRUNG", "gender": "Nam", "group": "4"},
    {"mssv": "2431540274", "name": "Bùi Quốc Bảo", "gender": "Nam", "group": "6"},
    {"mssv": "2431540209", "name": "Lạc Du Định", "gender": "Nam", "group": "6"},
    {"mssv": "2431540284", "name": "Phạm Nguyễn Bảo Ngọc", "gender": "Nam", "group": "6"},
    {"mssv": "2431540133", "name": "Lý Thế Vinh", "gender": "Nam", "group": "6"},
    {"mssv": "2431540270", "name": "Phùng Văn Vũ", "gender": "Nam", "group": "6"},
    {"mssv": "2431540029", "name": "Trần Bảo An", "gender": "Nam", "group": "7"},
    {"mssv": "2431540020", "name": "Đinh Quỳnh Anh", "gender": "Nữ", "group": "7"},
    {"mssv": "2431540039", "name": "Đỗ Trần Quang Anh", "gender": "Nam", "group": "7"},
    {"mssv": "2431540016", "name": "Hà Nguyễn Gia Huy", "gender": "Nam", "group": "7"},
    {"mssv": "2431540082", "name": "Nguyễn Hoàng Nam", "gender": "Nam", "group": "7"},
    {"mssv": "2331540029", "name": "Hồ Thị Ánh Ngọc", "gender": "Nữ", "group": "7"},
    {"mssv": "2431540085", "name": "Trần Việt Cường", "gender": "Nam", "group": "8"},
    {"mssv": "2431540072", "name": "Trần Minh Đức", "gender": "Nam", "group": "8"},
    {"mssv": "2431540079", "name": "Vương Huy Thắng", "gender": "Nam", "group": "8"},
    {"mssv": "2431540064", "name": "Trần Ngọc Trung", "gender": "Nam", "group": "8"},
    {"mssv": "2431540103", "name": "Nguyễn Trương Tú Anh", "gender": "Nam", "group": "8"},
    {"mssv": "2431540068", "name": "Vũ Trung Kiên", "gender": "Nam", "group": "8"},
    {"mssv": "2431540032", "name": "Nguyễn Phan Khánh Vy", "gender": "Nữ", "group": "9"},
    {"mssv": "2431540018", "name": "Trần Phúc Hoàng", "gender": "Nam", "group": "9"},
    {"mssv": "2254810162", "name": "NGUYỄN ANH KHA", "gender": "Nam", "group": "9"},
    {"mssv": "2431540112", "name": "Ngô Tùng Anh Tú", "gender": "Nam", "group": "9"},
    {"mssv": "2431540027", "name": "Phan Hoàng Tý", "gender": "Nam", "group": "9"}
]
STUDENTS_BY_MSSV = {student["mssv"]: student for student in STUDENTS}

pages = Blueprint("main", __name__)
pages.register_blueprint(auth)


@pages.route("/")
def home():
    """The landing page of the project"""
    cats = Category.all()
    users = User.top()
    return render_template("home-page.html", categories=cats, users=users)


@pages.route("/lobby")
def lobby():
    """Create or Join room form selection"""
    room_code = request.args.get("room_code", "").strip()
    if room_code != FIXED_ROOM_CODE:
        flash(f"Chỉ được phép vào phòng {FIXED_ROOM_CODE}.", "error")
        return redirect(url_for("main.home"))
    return render_template("lobby.html", students=STUDENTS, room_code=room_code)


def _create_game_room(player_name, room_code=FIXED_ROOM_CODE):
    import secrets
    from app.websocket import rooms, room_lock

    if not player_name:
        player_name = current_user.username if current_user.is_authenticated else "Người chơi"

    with room_lock:

        if room_code not in rooms:
            rooms[room_code] = {
                'host_sid': None,
                'difficulty': 'medium',
                'started': False,
                'questions': [],
                'current_index': 0,
                'active_question': None,
                'question_start_time': 0,
                'player_answers_submitted': {},
                'players': {},
                'game_id': secrets.token_hex(8),
                'timer_thread': None
            }


    session["guest_player_name"] = player_name
    return redirect(url_for("main.game_room", room_id=room_code, host="true", name=player_name))


@pages.route("/game/student-login", methods=["POST"])
def student_login():
    room_code = request.form.get("room_code", "").strip()
    student_mssv = request.form.get("student_mssv", "").strip()
    student_password = request.form.get("student_password", "").strip()
    student = STUDENTS_BY_MSSV.get(student_mssv)

    if room_code != FIXED_ROOM_CODE:
        flash(f"Chỉ được phép vào phòng {FIXED_ROOM_CODE}.", "error")
        return redirect(url_for("main.home"))

    if not student or student_password != student_mssv:
        flash("MSSV hoặc mật khẩu không đúng. Vui lòng thử lại.", "error")
        return redirect(url_for("main.lobby", room_code=room_code))

    session["guest_player_name"] = student["name"]
    session["guest_player_group"] = student["group"]
    session["guest_player_team"] = int(student["group"]) if student["group"].isdigit() else None
    flash(f"Chào {student['name']}, bạn thuộc nhóm {student['group']}.", "success")

    from app.websocket import rooms
    if room_code in rooms and rooms[room_code].get("started"):
        flash("Phòng chơi này đã bắt đầu, vui lòng thử phòng khác.", "error")
        return redirect(url_for("main.home"))

    if room_code in rooms:
        return redirect(url_for("main.game_room", room_id=room_code, host="false", name=student["name"]))

    return _create_game_room(student["name"], room_code)


@pages.route("/game/create", methods=["POST"])
def create_room():
    player_name = request.form.get("player_name", "").strip()
    return _create_game_room(player_name)


@pages.route("/game/guest", methods=["POST"])
def guest_room_route():
    import secrets
    room_code = request.form.get("room_code", "").strip()
    player_name = request.form.get("player_name", "").strip()

    if not (room_code.isdigit() and len(room_code) == 4):
        flash("Mã phòng phải gồm đúng 4 số.", "error")
        return redirect(url_for("main.lobby"))

    if not player_name:
        flash("Vui lòng nhập tên người chơi.", "error")
        return redirect(url_for("main.lobby"))

    from app.websocket import rooms, room_lock
    with room_lock:
        is_new_room = room_code not in rooms
        if is_new_room:
            rooms[room_code] = {
                'host_sid': None,
                'difficulty': 'medium',
                'tournament_mode': True,
                'started': False,
                'questions': [],
                'current_index': 0,
                'active_question': None,
                'question_start_time': 0,
                'player_answers_submitted': {},
                'players': {},
                'game_id': secrets.token_hex(8),
                'timer_thread': None
            }

    session["guest_player_name"] = player_name
    return redirect(url_for("main.game_room", room_id=room_code, host="true" if is_new_room else "false", name=player_name))


@pages.route("/game/join", methods=["POST"])
def join_room_route():
    room_code = request.form.get("room_code", "").upper().strip()
    player_name = request.form.get("player_name", "").strip()
    from app.websocket import rooms
    if room_code not in rooms:
        flash("Phòng chơi không tồn tại!", "error")
        return redirect(url_for("main.lobby"))
    if player_name:
        session["guest_player_name"] = player_name
    return redirect(url_for("main.game_room", room_id=room_code, name=player_name))


@pages.route("/game/<room_id>")
def game_room(room_id):
    """Play the game in a multiplayer room"""
    from app.websocket import rooms
    if room_id not in rooms:
        return abort(404)
    host_param = request.args.get('host', '').lower()
    player_name = request.args.get("name") or session.get("guest_player_name") or (
        current_user.username if current_user.is_authenticated else "Người chơi"
    )
    player_team = session.get("guest_player_team")
    is_host = (host_param in ('true', '1')) or rooms[room_id]['host_sid'] is None or len(rooms[room_id]['players']) == 0
    return render_template(
        "multiplayer-room-page.html",
        room_code=room_id,
        is_host=is_host,
        player_name=player_name,
        player_team=player_team
    )


@pages.route("/profile")
@login_required
def profile():
    """Show the user profile containing statistics and badges"""
    from models.engine.sql import session as db_session
    from models.badge_definition import BadgeDefinition

    # Fetch 5 recent games
    recent_games_raw = db_session.execute(text("""
        SELECT game_id, created_at, difficulty,
               COUNT(*) as total_questions,
               SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct_questions
        FROM player_answers
        WHERE user_id = :user_id
        GROUP BY game_id
        ORDER BY created_at DESC
        LIMIT 5
    """), {"user_id": current_user.id}).fetchall()
    
    recent_games = []
    for row in recent_games_raw:
        # Convert date to human-readable string
        dt_val = datetime_val = row[1]
        if isinstance(dt_val, str):
            try:
                dt_val = datetime.fromisoformat(dt_val.split('.')[0])
            except:
                pass
        dt_str = dt_val.strftime("%d/%m/%Y %H:%M") if hasattr(dt_val, "strftime") else str(dt_val)
        
        recent_games.append({
            'game_id': row[0],
            'created_at': dt_str,
            'difficulty': row[2],
            'total': row[3],
            'correct': row[4],
            'accuracy': round((row[4] / row[3] * 100), 1) if row[3] > 0 else 0
        })
        
    all_badges = db_session.query(BadgeDefinition).all()
    user_badges = json.loads(current_user.badges) if current_user.badges else []
    
    # Construct stats
    accuracy = round((current_user.right_tries / current_user.total_tries * 100), 1) if current_user.total_tries > 0 else 0
    stats = {
        'games_played': current_user.total_games,
        'total_score': current_user.total_score,
        'average_accuracy': accuracy,
        'max_streak': current_user.best_streak
    }
    
    # Construct badges
    badges = []
    for b in all_badges:
        badges.append({
            'name': b.name,
            'description': b.description,
            'icon': b.icon,
            'earned': b.badge_key in user_badges
        })
        
    # Construct heatmap
    stats_raw = db_session.execute(text("""
        SELECT 
            article_id,
            article_name,
            COUNT(*) as total,
            SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct
        FROM player_answers
        WHERE user_id = :user_id
        GROUP BY article_id, article_name
        ORDER BY article_id
    """), {"user_id": current_user.id}).fetchall()
    
    heatmap = []
    for row in stats_raw:
        total = row[2]
        correct = row[3]
        acc = (correct / total * 100) if total > 0 else 0
        heatmap.append({
            'article': row[0],
            'article_name': row[1],
            'total': total,
            'correct': correct,
            'accuracy': round(acc, 1)
        })
    
    return render_template("profile.html", recent_games=recent_games, stats=stats, badges=badges, heatmap=heatmap)


@pages.route("/api/player/stats")
def player_stats():
    """Get weak areas heatmap statistics for the logged in user"""
    if not current_user.is_authenticated:
        return jsonify({'stats': []})
        
    from models.engine.sql import session as db_session
    stats = db_session.execute(text("""
        SELECT 
            article_id,
            article_name,
            COUNT(*) as total,
            SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct,
            ROUND(AVG(time_taken), 1) as avg_time
        FROM player_answers
        WHERE user_id = :user_id
        GROUP BY article_id, article_name
        ORDER BY article_id
    """), {"user_id": current_user.id}).fetchall()
    
    result = []
    for row in stats:
        total = row[2]
        correct = row[3]
        accuracy = (correct / total * 100) if total > 0 else 0
        result.append({
            'article_id': row[0],
            'article_name': row[1],
            'total': total,
            'correct': correct,
            'accuracy': round(accuracy, 1),
            'avg_time': row[4],
            'level': 'strong' if accuracy >= 80 else ('ok' if accuracy >= 50 else 'weak')
        })
    return jsonify({'stats': result})

