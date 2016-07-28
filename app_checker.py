import subprocess, re, os

import records

import secrets


# Get all the tags in the git repo.  Match them against Heroku releases and alembic version.

os.chdir(os.path.expanduser(secrets.PROJECT_PATH))
proc = subprocess.Popen(
    'git show-ref --tags'.split(), stdout=subprocess.PIPE)
stdout = proc.communicate()[0]
commit_to_tag = {}
for match in re.finditer('([a-z0-9]+) refs/tags/([a-z0-9\.\-]+)', stdout):
    commit_to_tag[match.group(1)[:7]] = match.group(2)

for app_key in secrets.app_name_to_db_url:
    if app_key is None:
        app_name = 'local'
        commit = None
        tag = None
    else:
        app_name = app_key
        proc = subprocess.Popen(
            'heroku releases --app {}'.format(app_name).split(), stdout=subprocess.PIPE)
        stdout = proc.communicate()[0]
        match = re.search('Deploy ([a-z0-9]+)', stdout)
        commit = match.group(1)
        tag = commit_to_tag.get(commit)

    print 'app_name: {}, commit: {} ({})'.format(app_name, commit, tag)

    _db_url_with_creds = secrets.app_name_to_db_url[app_key]
    safe_db_url = re.sub(
        '://([a-zA-Z0-9]+:[a-zA-Z0-9]+)@', '://<user>:<pass>@', _db_url_with_creds)
    db = records.Database(_db_url_with_creds)
    rows = db.query('select * from alembic_version')
    alembic_version = rows[0]['version_num']
    print '  alembic_version:', alembic_version
