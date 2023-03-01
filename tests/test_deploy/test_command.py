# Tests for commcare_cloud.commands.deploy.command.Deploy
# Way too many things are mocked here.
import sys
from pathlib import Path
from unittest.mock import patch

from testil import assert_raises, eq

from commcare_cloud.commands.deploy import command, commcare
from commcare_cloud.commcare_cloud import call_commcare_cloud #make_command_parser
from commcare_cloud.environment.main import Environment, get_environment
from commcare_cloud.fab.deploy_diff import DeployDiff


def test_deploy_commcare_happy_path():
    def run_playbook(playbook, context, *args, unknown_args={}, **kw):
        eq(unknown_args, ["-e", "code_version=def456"])
        eq(context.environment.release_name, "GHOST")
        log.append(playbook)
        return 0

    def run_fab(env_name, fab, task, *args, **kw):
        log.append(" ".join((f"{fab} {task}",) + args))
        return 0

    log = []
    with (
        patch.object(commcare, "run_ansible_playbook", run_playbook),
        patch.object(commcare, "commcare_cloud", run_fab),
    ):
        _deploy_commcare()

    eq(log, ["deploy_hq.yml", "fab deploy_commcare --set release_name=GHOST"])


def test_resume_deploy_with_release_name():
    def run_playbook(playbook, context, *args, unknown_args=None, **kw):
        eq(unknown_args, ["-e", "code_version="])
        eq(context.environment.release_name, "FRANK")
        log.append(playbook)
        return 0

    def run_fab(env_name, fab, task, *args, **kw):
        log.append(" ".join((f"{fab} {task}",) + args))
        return 0

    log = []
    with (
        patch.object(commcare, "run_ansible_playbook", run_playbook),
        patch.object(commcare, "commcare_cloud", run_fab),
    ):
        _deploy_commcare("--resume=FRANK")

    eq(log, [
        "deploy_hq.yml",
        "fab deploy_commcare:resume=yes --set release_name=FRANK"
    ])


def test_resume_deploy_without_release_name_raises():
    def run_playbook(playbook, context, *args, unknown_args=None, **kw):
        raise Exception("unexpected")

    def run_fab(env_name, fab, task, *args, **kw):
        raise Exception("unexpected")

    with (
        patch.object(commcare, "run_ansible_playbook", run_playbook),
        patch.object(commcare, "commcare_cloud", run_fab),
        assert_raises(SystemExit),
        patch("sys.stderr", sys.stdout)
    ):
        _deploy_commcare("--resume")


def _deploy_commcare(*argv):
    envs = Path(__file__).parent.parent / "test_envs"
    diff = DeployDiff(None, "abc123", "def456", None)
    get_environment.reset_cache()
    with (
        patch("commcare_cloud.environment.paths.ENVIRONMENTS_DIR", envs),
        patch.object(command, "check_branch"),
        patch.object(commcare, "record_deploy_start"),
        patch.object(commcare, "record_deploy_failed"),
        patch.object(commcare, "record_successful_deploy"),
        patch.object(commcare, "confirm_deploy", lambda *a: True),
        patch.object(commcare, "DEPLOY_DIFF", diff),
        patch.object(Environment, "create_generated_yml", lambda self:None),
        patch.object(Environment, "release_name", "GHOST"),
    ):
        argv = ("cchq", "small_cluster", "deploy", "commcare") + argv
        return call_commcare_cloud(argv)
