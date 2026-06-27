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
    return render_template("lobby.html")


@pages.route("/game/create", methods=["POST"])
def create_room():
    import random
    import secrets
    from app.websocket import rooms, room_lock

    player_name = request.form.get("player_name", "").strip()
    if not player_name:
        player_name = current_user.username if current_user.is_authenticated else "Người chơi"

    with room_lock:
        room_code = f"{random.randint(0, 9999):04d}"
        while room_code in rooms:
            room_code = f"{random.randint(0, 9999):04d}"
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
    is_host = (host_param in ('true', '1')) or rooms[room_id]['host_sid'] is None or len(rooms[room_id]['players']) == 0
    return render_template("multiplayer-room-page.html", room_code=room_id, is_host=is_host, player_name=player_name)


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

