![Screenshot](/screenshot2.png?raw=true "Screenshot")

Keep track of many parallel heroku instances in one place.

** Installation **

Clone the repo:  `git clone https://github.com/JesseAldridge/heroku_app_checker`

Create a `secrets.py` file following the format in `secrets.py.fake_example`.

Setup a remote server.  Here is how I do it:

Note, I haven't yet tested these instructions, so there's probably a few rough edges here and there.

Create a Ubuntu [ec2 box](https://aws.amazon.com/ec2/) (the smallest kind is fine).

Make sure port 80 is accessible (configured via security group).

Modify your ~/.ssh/config to point to it.  Mine looks something like this:

Host app-checker
    HostName 12.345.56.789
    User ubuntu
    IdentityFile ~/.ssh/my-ssh-key.pem

Install [Fabric](http://www.fabfile.org/) on your local machine.

rsync the files to the remote server.  You can just run `fab deploy_server` to do this.

ssh into the server.  `ssh app-checker`

Install pip:  `sudo easy_install pip`
Install gunicorn:  `sudo apt-get install gunicorn`
Install requirements:  `pip install -r requirements.txt --user`.
Install heroku toolbelt:  `wget -O- https://toolbelt.heroku.com/install-ubuntu.sh | sh`

For a non-public repo, add a GitHub ssh key to `~/.ssh/`
(You may want to create a separate user for this if more than one person will work on this.)

Clone the repos you want to track:
  `git clone git@github.com:my_company/my_frontend.git`
  `git clone git@github.com:my_company/my_backend.git`

Switch to the application directory:  `cd heroku_app_checker`

Run gunicorn:  `sudo gunicorn server:app -w 4 -b 0.0.0.0:80 --log-file=- &`
Run the report generator loop in the background:  `python loop.py &`

Ctrl+D to logoff

You should now be able to view the app at the ip of the ec2 box.
