import os, json, re, time, sys
from datetime import datetime

import flask

import secrets

#
# On each request, parse the latest ~/app_checker_report.txt and return it as an html table.
#


app = flask.Flask(__name__)
port = int(sys.argv[1]) if len(sys.argv) == 2 else 80

os.environ['TZ'] = "US/Pacific"
time.tzset()

@app.route('/')
def index():
    report_path = os.path.expanduser('~/app_checker_report.txt')
    tables = build_tables(report_path, ('Front-End', 'Back-End'))
    mod_time = os.path.getmtime(report_path)
    last_mod_dt = datetime.fromtimestamp(mod_time)

    # todo: proper template
    return '''
    <link id="bs-css" href="https://netdna.bootstrapcdn.com/bootstrap/3.0.3/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .outer { margin: 1px; width: 2000px }

        .table-container {
            display: inline-block;
            margin: 5px;
            padding: 7px;
            border: solid;
        }

        .table-title {
            font-size: 30px;
            margin-bottom: 6px
        }

        #front-end tr:nth-child(even) { background-color: #eee }

        #back-end tr:nth-child(even) { background-color: #eee }

        table.front-end {width: 500px}
        table.back-end {width: 650px}
        table {border-collapse:collapse}

        td {
          background: inherit;
        }

        .last_mod { margin-top: 20px; }
    </style>

    <div class='outer'>
        {{1}}
        <div class='last_mod'>Last updated: {{2}}</div>
    </div>
    '''.replace('{{1}}', '\n'.join(tables)).replace(
        '{{2}}', '{} PST'.format(str(last_mod_dt)))


def build_tables(report_path, table_titles):
    with open(report_path) as f:
        text = f.read()
    line_iter = iter(text.splitlines())

    tables = []
    for table_title in table_titles:
        for _ in range(10 ** 3):
            try:
                line = line_iter.next()
            except StopIteration:
                return 'Report not found.'
            if re.search('App Name', line):
                break

        column_names = [s.strip() for s in re.split(' {2,}', line)]
        table_rows = [
            '<tr>{}</tr>'.format(''.join(['<th>{}</th>'.format(s) for s in column_names]))]
        for _ in range(10 ** 3):
            line = line_iter.next()
            if line.startswith('```'):
                break
            if not re.search('[a-zA-Z]{4,}', line):
                continue
            column_cells = ['<td>{}</td>'.format(s) for s in line.split()]
            table_rows.append('<tr>{}</tr>'.format(''.join(column_cells)))
        table_id = table_title.lower().replace(' ', '-')
        tables.append('''
        <div class="table-container" id="{}">
            <div class="table-title">{}</div>
            <table class="{}">
                {}
            </table>
        </div>
        '''.format(table_id, table_title, table_title.lower().replace(' ', '-'),
                   '\n'.join(table_rows)))
    return tables

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=(port != 80))
