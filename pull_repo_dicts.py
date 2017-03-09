# -*- coding: utf8 -*-
import subprocess, re, os, time, collections, json, sys

import records

import conf


def pull_repo_dicts(testing):
    old_wd = os.getcwd()
    try:
        return pull_repo_dicts_inner(testing)
    finally:
        os.chdir(old_wd)

def pull_repo_dicts_inner(testing):
    # For each repo defined in conf.py...

    repo_dicts = []
    for repo_path, app_tuples in conf.repo_to_heroku_apps:
        repo_dicts.append({'path': repo_path, 'app_dicts': []})
        repo_dict = repo_dicts[-1]

        # Pull git tags.

        os.chdir(os.path.expanduser(repo_path))
        subprocess.call('git pull'.split())
        subprocess.call('git fetch --tags'.split())
        proc = subprocess.Popen(
            'git show-ref --tags --dereference'.split(), stdout=subprocess.PIPE)

        stdout = proc.communicate()[0]
        commit_to_tag = {}
        for match in re.finditer('([a-z0-9]+) refs/tags/([a-z0-9\.\-]+)', stdout):
            commit = match.group(1)[:7]
            tag = match.group(2)
            commit_to_tag[commit] = tag

        commit_tag_list = sorted(commit_to_tag.items(), key=lambda t: t[1])
        print 'commit_to_tag:', '\n'.join([str(t) for t in commit_tag_list][-100:])

        # For each app defined in conf.py...

        if testing:
            app_tuples = app_tuples[:3]

        repo_dict['app_dicts'] = [build_app_dict(commit_to_tag, *t) for t in app_tuples]

    return repo_dicts

def build_app_dict(commit_to_tag, icon_str, app_name, should_check_alembic):
    # Pull deployed commit and tag from heroku.

    app_dict = {
        'icon_str': icon_str,
        'app_name': app_name,
        'commit': None,
        'tag': None,
        'domain_name': None,
        'error': False
    }

    print 'pulling:', app_name
    proc = subprocess.Popen(
        'heroku releases -n100 --app {}'.format(app_name).split(), stdout=subprocess.PIPE)
    stdout = proc.communicate()[0]
    match = re.search('Deploy ([a-z0-9]+)', stdout)
    commit = None
    if match:
        commit = app_dict['commit'] = match.group(1)

    print 'commit:', commit
    app_dict['tag'] = commit_to_tag.get(commit)

    # Pull alembic version.

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
        finally:
            db.close()
        app_dict['alembic_version'] = alembic_version

    # Pull domain.

    proc = subprocess.Popen('heroku domains --app {}'.format(app_name).split(),
                            stdout=subprocess.PIPE)
    stdout_str = proc.communicate()[0]
    line_iter = iter(stdout_str.splitlines())
    for line in line_iter:
        if line.startswith('──────'):
            break
    for line in line_iter:
        app_dict['domain_name'] = line.split()[0]
    return app_dict


if __name__ == '__main__':
    testing = (len(sys.argv) == 2 and sys.argv[1] == 'test')

    while True:
        repo_dicts = pull_repo_dicts(testing)
        out_json = json.dumps(repo_dicts, indent=2)
        if testing:
            print 'out_json:', out_json
        with open('repos.json', 'w') as f:
            f.write(out_json)
