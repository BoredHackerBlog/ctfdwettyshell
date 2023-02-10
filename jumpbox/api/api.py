from flask import request
from flask_restx import Namespace, Resource

from CTFd.models import db
from CTFd.utils.decorators import admins_only

from ..functions.functions import ssh_user_del
from ..models.models import JumpboxConfig, JumpboxUsers

delete_jump_users = Namespace(
    "delete_jump_user", description="Endpoint to delete jumpbox users"
)


@delete_jump_users.route("", methods=["POST", "GET"])
class DeleteJumpUserAPI(Resource):
    @admins_only
    def get(self):
        selected_id = request.args.get("id")
        full = request.args.get("all")
        jumpbox = JumpboxConfig.query.filter_by(id=1).first_or_404()
        users = JumpboxUsers.query.all()

        if full == "true":
            for user in users:
                success = ssh_user_del(
                    hostname=jumpbox.hostname,
                    host_user=jumpbox.username,
                    private_key=jumpbox.private_key,
                    username=user.username,
                )
                if success:
                    print(f"User ID: {user.id} deleted")
                    JumpboxUsers.query.filter_by(id=user.id).delete()
                else:
                    return f"Failed to delete {user.username}", 500
        else:
            user = JumpboxUsers.query.filter_by(id=selected_id).first()
            success = ssh_user_del(
                hostname=jumpbox.hostname,
                host_user=jumpbox.username,
                private_key=jumpbox.private_key,
                username=user.username,
            )
            if success:
                print(f"User ID: {user.id} deleted")
                JumpboxUsers.query.filter_by(id=user.id).delete()
            else:
                return f"Failed to delete {user.username}", 500
        db.session.commit()
        return "Success", 200
