from flask import render_template, session, redirect, url_for

from CTFd.models import db, Teams
from CTFd.utils import admins_only, is_admin

from CTFd import utils

from uuid import uuid4 #used for random hex string generation
from os import system #for executing commands to docker

container_name = "wettytest" #CHANGE ME. Use whatever name you provided to your container
useradd_cmd = "docker exec -it %s /usr/sbin/useradd -m -s /bin/bash -p $(openssl passwd -1 %s) %s"
return_info = "To access web shell visit http://10.0.0.68:8080/<br>Username: %s<br>Password: %s" #CHANGE ME. The URL needs to be yours.

login_info = {} #this stores login info. If CTFd webapp is restarted, the information is lost. New

def load(app):
    @app.route('/docker', methods=['GET'])
    def view_docker():
        if utils.authed(): #make sure the user is logged in
            user = Teams.query.filter_by(id=session['id']).first() #get user/team id. 
            if login_info.has_key(user.id): #if there is already login info for the user
                return_data =  return_info%(login_info[user.id][0],login_info[user.id][1])
                return render_template('page.html', content=return_data) #provide the login info to the user
            else: #if there is no login info for the user
                randomvalue = uuid4().hex[0:16] #generate random hex string
                username = randomvalue[:8]
                password = randomvalue[8:]
                login_info[user.id] = [username,password] #add login info into our dictionary
                system(useradd_cmd%(container_name,password,username)) #run a command to add a user to the container
                return_data = return_info%(login_info[user.id][0],login_info[user.id][1])
                return render_template('page.html', content=return_data) #provide the login info to the user
        else: #if user isn't logged in, send them to the login page
            return redirect(url_for('auth.login'))
