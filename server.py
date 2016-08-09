
import os, json, re, time
from datetime import datetime

import flask

import secrets


app = flask.Flask(__name__)

os.environ['TZ'] = "US/Pacific"
time.tzset()

@app.route('/')
def index():
    REPORT_PATH = os.path.expanduser('~/app_checker_report.txt')

    with open(REPORT_PATH) as f:
        text = f.read()
    line_iter = iter(text.splitlines())
    for _ in range(10 ** 3):
        try:
            line = line_iter.next()
        except StopIteration:
            return 'Report not found'
        if line.startswith('App Name'):
            break


    column_names = [s.strip() for s in re.split(' {2,}', line)]
    table_rows = ['<tr>{}</tr>'.format(''.join(['<th>{}</th>'.format(s) for s in column_names]))]
    try:
        for _ in range(10 ** 3):
            line = line_iter.next()
            if not line.startswith('gigwalk-'):
                continue
            column_cells = ['<td>{}</td>'.format(s) for s in line.split()]
            table_rows.append('<tr>{}</tr>'.format(''.join(column_cells)))
    except StopIteration:
        pass

    mod_time = os.path.getmtime(REPORT_PATH)
    last_mod_dt = datetime.fromtimestamp(mod_time)

    # todo: proper template
    return '''
    <link id="bs-css" href="https://netdna.bootstrapcdn.com/bootstrap/3.0.3/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .outer { margin: 1px }

        table{border-collapse:collapse; width:700px}

        table tr:nth-child(odd) {
          background: #eeeeee
        }

        td {
          background: inherit;
        }

        .last_mod { margin-top: 20px; }
    </style>

    <div class='outer'>
        <table>
            {{1}}
        </table>
        <div class='last_mod'>Last updated: {{2}}</div>
    </div>
    '''.replace('{{1}}', '\n'.join(table_rows)).replace(
        '{{2}}', '{} PST'.format(str(last_mod_dt)))

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 3000.
    app.run(host='0.0.0.0', port=secrets.PORT, debug=(secrets.PORT==3000))
