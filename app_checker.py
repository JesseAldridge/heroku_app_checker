# -*- coding: utf-8 -*-

import subprocess, re, os, time, collections

import records

import secrets

# Get all the tags in the git repo.  Match them against Heroku releases and alembic version.

def report_all_repos():
    path_to_repo = {}

    for repo_path, apps in secrets.repo_to_heroku_apps:
        os.chdir(os.path.expanduser(repo_path))
        subprocess.call('git pull'.split())

        merges_needed = []
        for upstream, downstream in secrets.upstream_to_downstream:
            subprocess.call('git checkout origin/dev'.split())
            proc = subprocess.Popen(
                'git merge origin/master --no-edit'.split(), stdout=subprocess.PIPE)
            stdout = proc.communicate()[0]
            if len(stdout).splitlines() > 1:
                merges_needed.append({'upstream': upstream, 'downstream': downstream})
            subprocess.call('git merge --abort'.split())

        proc = subprocess.Popen(
            'git show-ref --tags --dereference'.split(), stdout=subprocess.PIPE)
        stdout = proc.communicate()[0]
        commit_to_tag = {}
        for match in re.finditer('([a-z0-9]+) refs/tags/([a-z0-9\.\-]+)', stdout):
            commit_to_tag[match.group(1)[:7]] = match.group(2)

        path_to_repo[repo_path] = {
            'apps': [],
            'merges_needed': merges_needed
        }

        for icon_str, app_name, _db_url_with_creds in apps:
            proc = subprocess.Popen(
                'heroku releases --app {}'.format(app_name).split(), stdout=subprocess.PIPE)
            stdout = proc.communicate()[0]
            match = re.search('Deploy ([a-z0-9]+)', stdout)
            commit = match.group(1)
            tag = commit_to_tag.get(commit)

            alembic_version = None
            row_str_params = [icon_str, app_name, commit, tag]
            if _db_url_with_creds:
                safe_db_url = re.sub(
                    '://([a-zA-Z0-9]+:[a-zA-Z0-9]+)@', '://<user>:<pass>@', _db_url_with_creds)
                db = records.Database(_db_url_with_creds)
                rows = db.query('select * from alembic_version')
                alembic_version = rows[0]['version_num']
                row_str_params.append(alembic_version)
            path_to_repo[repo_path]['apps'].append([
                icon_str, app_name, commit, tag, alembic_version])

    return path_to_repo
