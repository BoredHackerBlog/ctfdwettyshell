import tempfile
import os
from os import system  # for executing commands to docker
from uuid import uuid4  # used for random hex string generation

from flask import (Blueprint, redirect, render_template, request, session,
                   url_for)

from CTFd.models import Teams, db
from CTFd.utils.config import is_teams_mode
from CTFd.utils.decorators import admins_only, authed_only
from CTFd.utils.user import get_current_team, get_current_user

from .models.models import JumpboxConfig, JumpboxConfigForm, JumpboxUsers

ssh_useradd_cmd = "ssh -i %s -o StrictHostKeyChecking=no %s@%s 'sudo /usr/sbin/useradd -m -s /bin/bash -p $(openssl passwd -1 %s) %s'"


def define_terminal_app(app):
    admin_jumpbox_config = Blueprint('admin_jumpbox_config', __name__, template_folder='templates')

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
            if request.form.get('enabled'):
                j.enabled = (request.form['enabled'] == "true")
                j.hostname = request.form['hostname']
                j.username = request.form['username']
                if request.files.get('private_key'):
                    private_key = request.files['private_key'].stream.read()
                    temppk = tempfile.NamedTemporaryFile(mode="wb", dir="/tmp", delete=False)
                    temppk.write(private_key)
                    temppk.seek(0)
                    j.private_key = temppk.name
                    os.chmod(j.private_key, 0o600)
                else:
                    j.private_key = ""
            else:
                j.enabled = False
                j.hostname = jumpbox.get('hostname')
                j.username = jumpbox.get('username')
                j.private_key = jumpbox.get('private_key')
            db.session.add(j)
            db.session.commit()
            jumpbox = JumpboxConfig.query.filter_by(id=1).first()
        return render_template("jumpbox_config.html", config=jumpbox, form=form)

    app.register_blueprint(admin_jumpbox_config)

def define_jumpbox_user_status(app):
    user_jumpbox_status = Blueprint('user_jumpbox_status', __name__)

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
                system(ssh_useradd_cmd%(J.private_key, J.username,J.hostname,password,username))
                db.session.add(jumpbox)
                db.session.commit()
            return_data = f"""Username: {username}
                Password: {password}

                Credentials can be utilized to connect via ssh:
                ssh {username}@{J.hostname}
                """
            return render_template('page.html', content=return_data) 
        else:
            return_data = f"Jumpbox not configured yet"
            return render_template('page.html', content=return_data) 

    app.register_blueprint(user_jumpbox_status)

def load(app):
    app.db.create_all()
    define_terminal_app(app)
    define_jumpbox_user_status(app)