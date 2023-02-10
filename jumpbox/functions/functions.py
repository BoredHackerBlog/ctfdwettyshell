import paramiko


def execute_ssh_cmd(hostname, host_user, private_key, ssh_cmd):
    try:
        private_key = paramiko.RSAKey.from_private_key_file(private_key)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=host_user, pkey=private_key)
        _, stdout, _ = ssh.exec_command(ssh_cmd)
        exit_status = stdout.channel.recv_exit_status()
        ssh.close()
        return exit_status == 0
    except FileNotFoundError:
        return False


def ssh_user_add(hostname, host_user, private_key, username, password):
    ssh_cmd = f"sudo /usr/sbin/useradd -m -s /bin/bash -p $(openssl passwd -1 {password}) {username}"
    return execute_ssh_cmd(hostname, host_user, private_key, ssh_cmd)


def ssh_user_del(hostname, host_user, private_key, username):
    ssh_cmd = f"sudo userdel -r {username}"
    return execute_ssh_cmd(hostname, host_user, private_key, ssh_cmd)
