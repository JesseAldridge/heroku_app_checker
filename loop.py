import json

import app_checker


while True:
  print 'running app_checker.py...'

  report_dict = app_checker.report_all_repos()
  json_str = json.dumps(report_dict, indent=2)
  with open(os.path.expanduser('~/app_checker_report.json'), 'w') as f:
    f.write()
