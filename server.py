from __future__ import unicode_literals

import os, json, re, time, sys
from datetime import datetime

import flask

import secrets

#
# On each request, parse the latest ~/repos.json and return it as an html table.
#


app = flask.Flask(__name__)
port = int(sys.argv[1]) if len(sys.argv) == 2 else 80

os.environ['TZ'] = "US/Pacific"
time.tzset()

@app.route('/')
def index():
    report_path = os.path.expanduser('repos.json')
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

        table {border-collapse:collapse}

        td {
          background: inherit;
          padding: 1px;
          padding-right: 10px;
        }

        .last_mod { margin-top: 20px; }
        .heroku { width: 15px; height: 15px }
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
    repo_dicts = json.loads(text)

    tables = []
    column_names = ['icon_str', 'domain_name', 'app_name', 'tag', 'alembic_version']
    for table_title, repo_dict in zip(table_titles, repo_dicts):

        filtered_cols = [name for name in column_names if name in repo_dict['app_dicts'][0]]

        table_rows = []
        ths = ['<th>{}</th>'.format(key_to_column_str(s)) for s in filtered_cols]
        table_rows.append('<tr>{}</tr>'.format(''.join(ths)))
        for app_dict in repo_dict['app_dicts']:
            column_cells = []
            for key in filtered_cols:
                table_val = get_table_val(app_dict, key, table_title.lower().startswith('front'))
                column_cells.append('<td>{}</td>'.format(table_val))
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

def key_to_column_str(s):
    if s in ('icon_str', 'app_name'):
        return ''
    words = s.split('_')
    return ' '.join(word[0].upper() + word[1:] for word in words)

def get_table_val(app_dict, key, should_link_domain):
    if key == 'domain_name' and should_link_domain:
        domain_name = app_dict[key]
        return '<a href="https://{}">{}</a>'.format(domain_name, domain_name)
    elif key == 'app_name':
        app_name = app_dict[key]
        return '''
            <a href="https://dashboard.heroku.com/apps/{}">
                <img class='heroku' src="https://dashboard.heroku.com/images/favicon.ico">
            </a>'''.format(app_name)
    return app_dict[key]

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=(port != 80))
