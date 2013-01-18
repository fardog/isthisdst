from fabric.api import *
from fabric.contrib.console import confirm
from fabric.contrib.project import rsync_project


# these are the defaults, override them in your fabfile_local
env.hosts = ['user@example.com']
AWS_ACCESSKEY = 'your_access_key'
AWS_SECRET = 'your_aws_secret'
AWS_S3_BUCKET = 'your-bucketname'
LOCAL_DIR = '/full/path/to/local/dir'
REMOTE_DIR = '/full/path/to/remote/dir'
REMOTE_SETTINGS_FILE = 'relative/path/to/deployment/settings/file'
GIT_REPO = 'git@example.com:username/repo.git'
FAVICONS = {
    'ico': {
        'size': 32,
        'name': 'favicon.ico',
    },
    'apple-57': {
        'size': 57,
        'name': 'apple-touch-icon-precomposed.png',
    },
    'apple-72': {
        'size': 72,
        'name': 'apple-touch-icon-72x72-precomposed.png',
    },
    'apple-114': {
        'size': 114,
        'name': 'apple-touch-icon-114x114-precomposed.png',
    },
    'apple-144': {
        'size': 144,
        'name': 'apple-touch-icon-144x144-precomposed.png',
    },
    'fb': {
        'size': 300,
        'name': 'opengraph-icon.png',
    },
}


def prepare_staticfiles():
    """
    Collects the static files, including processing/minifying via pipeline and
    auto-creating favicons from svg.
    """
    make_favicons()
    local('rm -rf static')
    with lcd('app'):
        local('./manage.py collectstatic')
    local('s3put -a "%s" -s "%s" -b "%s" -p "%s" -g public-read static' % (AWS_ACCESSKEY, AWS_SECRET, AWS_S3_BUCKET, LOCAL_DIR))


def commit(message=None):
    """
    Interactively adds and commits to your local repo.
    """
    with settings(warn_only=True):
        result = local("git add -p")
    if result.failed and not confirm("`git add` returned some errors. Commit anyway?"):
        abort("Aborting at user request.")
    if message:
        local('git commit -m "%s"' % message)
    else:
        local('git commit')


def push():
    """
    Push changes to remote repository.
    """
    local("git push")


def prepare_deploy():
    """
    Perform all local preparations at once, and prepare for deploy.
    """
    commit()
    push()
    prepare_staticfiles()


def deploy():
    """
    Deploy changes to your remote host. Makes assumptions that a deployment
    directory is already set up, and that your user has permissions to write
    to it.
    """
    # verify that the directory exists on remote host, fail if not
    with settings(warn_only=True):
        result = run("test -d %s" % REMOTE_DIR)
    if result.failed and not confirm("The remote deployment doesn't exist, try to clone it?"):
        abort("Aborting at user request.")

    # if we made it here with a failed test, we need to clone
    if result.failed:
        clone()

    # make a place for our new static files and transfer, then kill the old dir
    with cd(REMOTE_DIR):
        run("git pull")
        run("git submodule update")
        run("mkdir static_tmp")
        rsync_project(local_dir='static/', remote_dir='%s/static_tmp/' % REMOTE_DIR)

        with settings(warn_only=True):
            mv_static = run("test -d %s/static" % REMOTE_DIR)
        if not mv_static.failed:
            run("mv static static_old")
        run("mv static_tmp static")
        if not mv_static.failed:
            run("rm -rf static_old")
        run("chmod -R 777 db")

    # push the settings file
    push_localsettings()

    # now reload httpd
    run("sudo service httpd reload")


def clone():
    """
    Clones the repository on the remote host, and sets up the local sqlite db.
    """
    run("mkdir %s" % REMOTE_DIR)

    with cd(REMOTE_DIR):
        run("git clone --recursive %s ." % GIT_REPO)
        run("mkdir db && chmod 777 db")
        push_localsettings()

    with cd('%s/app/' % REMOTE_DIR):
        run("./manage.py syncdb")

    with cd(REMOTE_DIR):
        run("chmod -R 777 db")


def push_localsettings():
    """
    Pushes the local_settings file up to the server after a deploy.
    """
    with cd(REMOTE_DIR):
        put(local_path=REMOTE_SETTINGS_FILE,
            remote_path='app/isthisdst/local_settings.py')


def make_favicons():
    with lcd("assets/favicons/"):
        for k, v in FAVICONS.items():
            local("convert favicon.svg -resize %s %s" % (v['size'], v['name']))


# import your local settings, which should define the ALLCAPS variables above.
from fabfile_local import *
