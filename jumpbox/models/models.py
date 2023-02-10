from wtforms import BooleanField, FileField, HiddenField, StringField
from wtforms.validators import DataRequired, InputRequired

from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField
from CTFd.models import db


class RequiredIf(InputRequired):
    """
    Require field if mentioned field is present
    """
    def __init__(self, other_field_name, *args, **kwargs):
        self.other_field_name = other_field_name
        super(RequiredIf, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        if bool(other_field.data):
            super(RequiredIf, self).__call__(form, field)

class JumpboxConfig(db.Model):
    """
	Docker Config Model. This model stores the config for docker API connections.
	"""
    id = db.Column(db.Integer, primary_key=True)
    enabled = db.Column("enabled",db.Boolean, index=True)
    hostname = db.Column("hostname", db.String(64), index=True)
    username = db.Column("username", db.String(64), index=True)
    private_key = db.Column("private_key", db.String(2200), index=True)

class JumpboxConfigForm(BaseForm):
    id = HiddenField()
    enabled = BooleanField('Enabled', validators=[DataRequired(),])
    hostname = StringField(
        "Jumpbox Hostname", 
        description="The Hostname/IP of your the jumpbox server",
        validators=[RequiredIf('enabled')]
    )
    username = StringField("username", validators=[RequiredIf('enabled')])
    private_key = FileField('SSH Private Key', validators=[RequiredIf('enabled')])
    submit = SubmitField('Submit')

class JumpboxUsers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column("team_id", db.String(64), index=True)
    user_id = db.Column("user_id", db.String(64), index=True)
    username = db.Column("username", db.String(64), index=True)
    password = db.Column("password", db.String(64), index=True)