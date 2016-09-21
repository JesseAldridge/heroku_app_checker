import subprocess, re, os, time, collections

import records

import secrets

# Get all the tags in the git repo.  Match them against Heroku releases and alembic version.

for repo_path, apps in secrets.repo_to_heroku_apps:
    os.chdir(os.path.expanduser(repo_path))
    subprocess.call('git pull'.split())
    subprocess.call('git fetch --tags'.split())
    proc = subprocess.Popen(
        'git show-ref --tags --dereference'.split(), stdout=subprocess.PIPE)
    stdout = proc.communicate()[0]
    commit_to_tag = {}
    for match in re.finditer('([a-z0-9]+) refs/tags/([a-z0-9\.\-]+)', stdout):
        commit_to_tag[match.group(1)[:7]] = match.group(2)

    row_str = u'{:<4} {:<35} {:<10} {:<15}'
    print '```'
    row_str_params = [u' ', 'App Name', 'Commit', 'Tag']
    if apps[0][2]:
        row_str += ' {}'
        row_str_params.append('Alembic Version')

    print row_str.format(*row_str_params).encode('utf8')
    print '-' * 80

    for icon_str, app_name, should_check_alembic in apps:
        proc = subprocess.Popen(
            'heroku releases --app {}'.format(app_name).split(), stdout=subprocess.PIPE)
        stdout = proc.communicate()[0]
        match = re.search('Deploy ([a-z0-9]+)', stdout)
        commit = match.group(1)
        tag = commit_to_tag.get(commit)

        row_str_params = [icon_str, app_name, commit, tag]

        if should_check_alembic:
            proc = subprocess.Popen(
                'heroku config:get ALEMBIC_DATABASE_URL --app {}'.format(app_name).split(),
                stdout=subprocess.PIPE)
            _db_url_with_creds = proc.communicate()[0]
            try:
                db = records.Database(_db_url_with_creds)
            except ValueError:
                alembic_version = 'error'
            else:
                rows = db.query('select * from alembic_version')
                alembic_version = rows[0]['version_num']
            row_str_params.append(alembic_version)
        print row_str.format(*row_str_params).encode('utf8')
    print '```'
