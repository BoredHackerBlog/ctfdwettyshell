CTFd plugin to provide web shells to CTF players. It utilizes CTFd(https://github.com/CTFd/CTFd/), Docker, and Wetty (https://github.com/krishnasrinivas/wetty).

More information here: http://www.boredhackerblog.info/2018/05/providing-shell-for-ctfs.html

Download:
```
git clone https://github.com/BoredHackerBlog/ctfdwettyshell
```

Setup:

0. Modify the Dockerfile file to fit whatever needs you have.
1. Build a docker image with the Dockerfile file.
```
cd ctfdwettyshell
docker build -t wettytest .
```
2. Copy wettyshell folder to your CTFd plugins folder
3. Start the docker container
```
docker run -td --rm --name wettytest -p 8080:3000 wettytest
```
4. Customize the init file inside the wettyshell folder. Change container_name and return_info strings.
5. Start CTFd
6. From the admin page, add a new page and redirect it to /docker. (Check blog for more info)

Feel free to clone and improve the code.

Similar plugin or features:
https://github.com/tamuctf/ctfd-shell-plugin
https://github.com/picoCTF/picoCTF/tree/master/picoCTF-shell