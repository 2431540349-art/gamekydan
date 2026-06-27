from flask import Blueprint, redirect, render_template, request, url_for, flash
from flask_login import LoginManager, current_user, login_user, logout_user

from models.user import User

login_manager = LoginManager()
auth = Blueprint("auth", __name__)


@login_manager.user_loader
def load_user(user_id):
    """provide the user to the authentication system"""
    return User.getone(user_id)


@auth.get("/logout")
def logout():
    """log out the user"""
    logout_user()
    return redirect("/login")


@auth.get("/login")
def login_page():
    """GET the login page"""
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    return render_template("login-page.html")


@auth.post("/login")
def login():
    """Submit the login form"""
    username = request.form.get("username")
    password = request.form.get("password")
    remember = request.form.get("remember") == "on"

    if not (username and password):
        flash("Vui lòng điền đầy đủ thông tin", "error")
        return redirect(url_for("main.auth.login_page"))

    user = User.by_username(username)
    if not (user and user.check_password(password)):
        flash("Tên đăng nhập hoặc mật khẩu không đúng", "error")
        return redirect(url_for("main.auth.login_page"))

    login_user(user, remember=remember)
    next_page = request.args.get("next", "/")
    return redirect(next_page)


@auth.get("/register")
def register_page():
    """GET the register page"""
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    return render_template("register-page.html")


@auth.post("/register")
def register():
    """Submit the registration form"""
    errors = {}
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not username:
        errors["username"] = "Vui lòng chọn tên đăng nhập"
    if len(password) < 4:
        errors["password"] = "Mật khẩu phải chứa ít nhất 4 ký tự"
    if password != confirm_password:
        errors["confirm"] = "Mật khẩu xác nhận không khớp"

    if len(errors):
        for key, err in errors.items():
            flash(err, "error")
        return redirect(url_for("main.auth.register_page"))

    try:
        user = User(username=username, password=password)
        user.save()
        flash("Đăng ký thành công! Hãy đăng nhập tài khoản của bạn.", "success")
        return redirect(url_for("main.auth.login_page"))
    except AssertionError:
        flash("Tên đăng nhập không hợp lệ", "error")
        return redirect(url_for("main.auth.register_page"))
    except Exception:
        flash("Tên đăng nhập đã tồn tại", "error")
        return redirect(url_for("main.auth.register_page"))
