![Screenshot](/screenshot2.png?raw=true "Screenshot")

Create a `secrets.py` file following the format in `secrets.py.fake_example`.

Here is how I set things up:

Create an Ubuntu ec2 box.

Modify your ~/.ssh/config to point to it.  Mine looks like this:

Host app-checker
    HostName 12.345.56.789
    User ubuntu
    IdentityFile ~/.ssh/my-ssh-key.pem

ssh into it.

Install pip: `sudo easy_install pip`
Install gunicorn:  `sudo apt-get install gunicorn`
Install requirements: `pip install -r requirements.txt --user`.


Run gunicorn:
`sudo gunicorn server:app -b 0.0.0.0:80 --log-file=- &`

Run `python loop.py &`.  This will do the queries and generate the report regularly.

You'll need to install heroku toolbelt and setup ssh access to GitHub for this to work.


Install [Fabric](http://www.fabfile.org/) on your local machine.

Run `fab deploy_server`.

