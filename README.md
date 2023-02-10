# Jumpbox CTFd plugin
CTFd plugin to provide credentials to jumpbox. Adapted from [ctfdwettyshell](https://github.com/BoredHackerBlog/ctfdwettyshell). 

## Download:
```
git clone https://github.com/shiftysheep/ctfdjumpbox
```

## Setup:

0. Setup a server that will host the user accounts. 
    - This server can utilize ssh and/or wetty to allow user access to tools. 
1. Copy jumpbox folder to your CTFd plugins folder
2. Start CTFd
3. From the admin page, under plugins configure the `Jumpbox Config` settings.
4. From the admin page, add a new page and redirect it to /terminal.


## Management:
From admin page, under plugins select `Jumpbox User Management` to delete all or some users.

## Future improvements
- Allow docker configuration 
- Utilize wetty shell locally from CTFd server
- 