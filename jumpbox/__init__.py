import os
import tempfile
from pathlib import Path
from uuid import uuid4

from flask import Blueprint, render_template, request

from CTFd.api import CTFd_API_v1
from CTFd.models import Teams, Users, db
from CTFd.utils.config import is_teams_mode
from CTFd.utils.decorators import admins_only, authed_only
from CTFd.utils.user import get_current_team, get_current_user

from .api.api import delete_jump_users
from .functions.functions import ssh_user_add
from .models.models import JumpboxConfig, JumpboxConfigForm, JumpboxUsers


def define_terminal_app(app):
    admin_jumpbox_config = Blueprint(
        "admin_jumpbox_config", __name__, template_folder="templates"
    )

    @admin_jumpbox_config.route("/admin/jumpbox_config", methods=["GET", "POST"])
    @admins_only
    def jumpbox_config():
        jumpbox = JumpboxConfig.query.filter_by(id=1).first()
        form = JumpboxConfigForm()
        if request.method == "POST":
            if jumpbox:
                j = jumpbox
            else:
                j = JumpboxConfig()
            if request.form.get("enabled"):
                j.enabled = request.form["enabled"] == "true"
                j.hostname = request.form["hostname"]
                j.username = request.form["username"]
                if request.files.get("private_key"):
                    private_key = request.files["private_key"].stream.read()
                    temppk = tempfile.NamedTemporaryFile(
                        mode="wb", dir="/tmp", delete=False
                    )
                    temppk.write(private_key)
                    temppk.seek(0)
                    j.private_key = temppk.name
                    os.chmod(j.private_key, 0o600)
                else:
                    j.private_key = jumpbox.private_key if jumpbox.private_key else ""
            else:
                j.enabled = False
                j.hostname = jumpbox.hostname if jumpbox.hostname else None
                j.username = jumpbox.username if jumpbox.username else None
                j.private_key = jumpbox.private_key if jumpbox.private_key else None
            db.session.add(j)
            db.session.commit()
            jumpbox = JumpboxConfig.query.filter_by(id=1).first()
        jumpbox.private_key = (
            jumpbox.private_key if Path(jumpbox.private_key).exists() else None
        )
        return render_template("jumpbox_config.html", config=jumpbox, form=form)

    app.register_blueprint(admin_jumpbox_config)


def define_user_management(app):
    admin_jumpbox_user_mgmt = Blueprint(
        "admin_jumpbox_user_mgmt",
        __name__,
        template_folder="templates",
        static_folder="assets",
    )

    @admin_jumpbox_user_mgmt.route("/admin/jumpbox_user_mgmt", methods=["GET", "POST"])
    @admins_only
    def user_mgmt():
        users = JumpboxUsers.query.all()
        for i in users:
            if is_teams_mode():
                name = Teams.query.filter_by(id=i.team_id).first()
                i.team_id = name.name
            else:
                name = Users.query.filter_by(id=i.user_id).first()
                i.user_id = name.name
        return render_template("jumpbox_user_mgmt.html", users=users)

    app.register_blueprint(admin_jumpbox_user_mgmt)


def define_jumpbox_user_status(app):
    user_jumpbox_status = Blueprint(
        "user_jumpbox_status", __name__, template_folder="templates"
    )

    @user_jumpbox_status.route("/terminal", methods=["GET", "POST"])
    @authed_only
    def user_status():
        J = JumpboxConfig.query.filter_by(id=1).first()
        jumpbox = JumpboxUsers()
        if J:
            if is_teams_mode():
                session = get_current_team()
                existing = JumpboxUsers.query.filter_by(team_id=session.id).first()
            else:
                session = get_current_user()
                existing = JumpboxUsers.query.filter_by(user_id=session.id).first()
            if existing:
                username = existing.username
                password = existing.password
            else:
                randomvalue = uuid4().hex[0:16]
                username = randomvalue[:8]
                password = randomvalue[8:]
                jumpbox.username = username
                jumpbox.password = password
                if is_teams_mode:
                    jumpbox.team_id = session.id
                else:
                    jumpbox.user_id = session.id
                success = ssh_user_add(
                    hostname=J.hostname,
                    host_user=J.username,
                    private_key=J.private_key,
                    username=username,
                    password=password,
                )
                if success:
                    db.session.add(jumpbox)
                    db.session.commit()
                else:
                    return render_template(
                        "jumpbox_user.html",
                        config={"enabled": False},
                        errors=["Failed to create user account!"],
                    )
            return_data = {
                "enabled": J.enabled,
                "username": username,
                "password": password,
                "hostname": J.hostname,
            }
            return render_template("jumpbox_user.html", config=return_data)
        else:
            return_data = {"enabled": False}
            return render_template("jumpbox_user.html", config=return_data)

    app.register_blueprint(user_jumpbox_status)


def load(app):
    app.db.create_all()
    define_terminal_app(app)
    define_user_management(app)
    define_jumpbox_user_status(app)
    CTFd_API_v1.add_namespace(delete_jump_users, "/delete_jump_user")
