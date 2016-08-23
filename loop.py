import subprocess, os

while True:
    print 'running app_checker.py...'
    proc = subprocess.Popen('python app_checker.py'.split(), stdout=subprocess.PIPE)
    stdout = proc.communicate()[0]
    print 'done'
    with open(os.path.expanduser('~/app_checker_report.txt'), 'w') as f:
        f.write(stdout)
