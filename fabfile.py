# -*- coding: utf-8 -*-
import random

from fabric.api import cd, env, local, parallel, roles, run, task
from fabric.contrib.files import exists

# Changable settings
env.roledefs = {
    'web': [
        'lives52@scorch.devsoc.org',
        'lives52@smaug.devsoc.org',
    ],
    'cron': [
        'lives52@scorch.devsoc.org',
    ],
}

env.home = env.get('home', '/var/www/lives52')
env.repo = env.get('repo', '52lives')
env.media = env.get('media', '52lives')
env.database = env.get('database', 'lives52_django')

CRONTAB = """
MAILTO=admin@blanc.ltd.uk

{daily}         /usr/local/bin/django-cron python manage.py clearsessions
"""

# Avoid tweaking these
env.use_ssh_config = True
GIT_REMOTE = 'git@github.com:developersociety/{env.repo}.git'
DATABASE_SERVER = 'golestandt.devsoc.org'


@task
@roles('cron')
def cron(remove=None):
    """
    Crontab setup.

    Can also be removed if needed.

    fab cron
    fab cron:remove=True
    """
    # Allow quick removal if needed
    if remove:
        run('crontab -r')
        return

    # Deterministic based on hostname
    random.seed(env.host_string)

    # Several templates - can add more if needed
    def every_x(minutes=60, hour='*', day='*', month='*', day_of_week='*'):
        # Add some randomness to minutes
        start = random.randint(0, minutes - 1)
        minute = ','.join(str(x) for x in range(start, 60, minutes))

        return '{minute} {hour} {day} {month} {day_of_week}'.format(
            minute=minute, hour=hour, day=day, month=month, day_of_week=day_of_week)

    daily = every_x(hour=random.randint(0, 23))
    hourly = every_x()

    cron = CRONTAB.format(daily=daily, hourly=hourly)

    run("echo '{}' | crontab -".format(cron))


@task
@roles('web')
@parallel
def clone_repo(branch='master'):
    """
    Initial site setup.

    Only intended to be run once, but can be used to switch branch.

    fab clone_repo
    fab clone_repo:branchname
    """
    with cd(env.home):
        if not exists('.git'):
            git_repo = GIT_REMOTE.format(env=env)
            run('git clone --quiet --recursive {} .'.format(git_repo))
        else:
            run('git fetch')

        run('git checkout {}'.format(branch))


@task
@roles('web')
def deploy(force_reload=None):
    """
    Deploy to remote server.

    Steps includes pull repo, migrate, install requirements, collect static.

    fab deploy
    fab deploy:True
    fab deploy:force_reload=True
    """
    with cd(env.home):
        run('git pull')

        run('pip install --quiet --requirement requirements/production.txt')

        # Clean up any potential cruft
        run('find . -name "*.pyc" -delete')

        # Install nvm using .nvmrc version
        run('nvm install --no-progress')

        # Check for changes in nvm or package-lock.json
        run(
            'cmp --silent .nvmrc node_modules/.nvmrc || '
            'rm -f node_modules/.package-lock.json'
        )
        run(
            'cmp --silent package-lock.json node_modules/.package-lock.json || '
            'rm -f node_modules/.package-lock.json'
        )

        # Install node packages
        if not exists('node_modules/.package-lock.json'):
            run('npm ci --no-progress')
            run('cp -a package-lock.json node_modules/.package-lock.json')
            run('cp -a .nvmrc node_modules/.nvmrc')

        # Generate css from less.
        run(
            '{}/node_modules/.bin/grunt less:development autoprefixer cssmin'.format(
                env.home
            )
        )

        # Migrate database changes
        run('python manage.py migrate')

        # Static files
        run('python manage.py collectstatic --verbosity=0 --noinput')

        if force_reload:
            run('killall -TERM uwsgi')
        else:
            run('killall -HUP uwsgi')


@task
def get_backup(hostname=None, replace_hostname='127.0.0.1', replace_port=8000):
    """
    Get remote backup and restore database locally.

    fab get_backup
    fab get_backup:www.example.com
    fab get_backup:www.example.com,192.1.1.1
    fab get_backup:hostname=www.example.com,replace_hostname=192.1.1.1,replace_port=8000
    """
    # Recreate database
    local('dropdb --if-exists {}'.format(env.database))
    local('createdb {}'.format(env.database))

    # Connect to the server and dump database.
    commands = ['ssh -C {} sudo -u postgres pg_dump --no-owner {}'.format(
        DATABASE_SERVER, env.database
    )]

    if hostname:
        # If hostname is passed replace with replace_hostname.
        commands.append('sed -e "s|{}|{}:{}|g"'.format(
            hostname, replace_hostname, replace_port
        ))

    # Restore database.
    commands.append('psql --single-transaction {}'.format(env.database))

    local(' | '.join(commands))


@task
def get_media(directory=''):
    """
    Download remote media files.

    fab get_media
    fab get_media:assets
    """
    # Recreate database
    # Sync files from our S3 bucket/directory
    local(
        'aws-vault exec devsoc-contentfiles-download -- '
        'aws s3 sync '
        's3://contentfiles-media-eu-west-2/{media}/{directory} '
        'htdocs/media/{directory}'.format(
            media=env.media, directory=directory
        )
    )
