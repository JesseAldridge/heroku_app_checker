![Screenshot](/screenshot2.png?raw=true "Screenshot")

Create a `secrets.py` file following the format in `secrets.py.fake_example`.

Then run `pip install -r requirements.txt`.

Then run the server in one process and `python loop.py &` in another.

Here is how I like to run the server:

Install gunicorn if necessary:
`sudo apt-get install gunicorn`

`sudo gunicorn server:app -b 0.0.0.0:80 --log-file=- &`


You'll need to install heroku toolbelt and setup ssh access to GitHub for this to work.


----

"server.py" -> "app_checker_report.txt" <- app_checker.py
