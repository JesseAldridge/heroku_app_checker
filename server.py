import os, json, re, time
from datetime import datetime

import flask

import secrets


app = flask.Flask(__name__)

os.environ['TZ'] = "US/Pacific"
time.tzset()

@app.route('/')
def index():
    report_path = os.path.expanduser('~/app_checker_report.txt')
    tables = build_tables(report_path, ('Front End', 'Back End'))
    mod_time = os.path.getmtime(report_path)
    last_mod_dt = datetime.fromtimestamp(mod_time)

    # todo: proper template
    return '''
    <link id="bs-css" href="https://netdna.bootstrapcdn.com/bootstrap/3.0.3/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .outer { margin: 1px; width: 2000px }

        .table-container { display: inline-block; }

        table.front-end {width: 500px}
        table.back-end {width: 650px}
        table {border-collapse:collapse}

        table tr:nth-child(odd) {
          background: #eeeeee
        }

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
    path_to_repo = json.loads(text)

    tables = []
    for table_title, repo_dict in path_to_repo.iteritems():
        column_names = repo_dict['apps'][0].keys() if repo_dict['apps'] else []
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
        tables.append('''
        <div class="table-container">
            <h3>{}</h3>
            <table class="{}">
                {}
            </table>
        </div>
        <div>{}</div>
        '''.format(table_title, table_title.lower().replace(' ', '-'),
                   '\n'.join(table_rows), merges_needed))
    return tables

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 3000.
    app.run(host='0.0.0.0', port=secrets.PORT, debug=(secrets.PORT==3000))
