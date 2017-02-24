![Screenshot](/screenshot.png?raw=true "Screenshot")

Keep track of many parallel heroku deployments in one place.

# Installation

Create a `conf.py` file following the format in `conf.py.fake_example`.

Install requirements:
```
sudo easy_install pip
sudo apt-get install gunicorn`
pip install -r requirements.txt --user
wget -O- https://toolbelt.heroku.com/install-ubuntu.sh | sh
```

For a non-public repo, add a GitHub ssh key to `~/.ssh/`  
(You may want to create a separate user for this if you are collaborating with others.)

Clone the repos you want to track:  
  `git clone git@github.com:my_company/my_frontend.git`  
  `git clone git@github.com:my_company/my_backend.git`  

Switch to the application directory:  `cd heroku_app_checker`

Run gunicorn:  `sudo gunicorn server:app -w 4 -b 0.0.0.0:80 --log-file=- &`  
Run the report generator loop:  `python pull_repo_dicts.py &`  
