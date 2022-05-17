import os
import subprocess
import tempfile
from contextlib import contextmanager
from shlex import quote

from nose.tools import nottest
from unittest import TestCase


class TestGitSingleBranch(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        # init repos
        cls.sub_repo, cls.super_repo = setup_test_repos(cls.temp_dir.name)
        clone_url = cls.super_repo.git_do("remote", "get-url", "--push", "origin")
        # setup a clone for testing
        cls.repo = GitRepo(os.path.join(cls.temp_dir.name, "clone"))
        cls.repo.git_do("clone", clone_url.strip(), ".")
        cls.repo.git_do("submodule", "update", "--recursive", "--init", "--single-branch")

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def test_checkout_tag_has_correct_submodule_refs(self):
        self.repo.git_do("fetch", "origin", "--tags", "A")
        self.repo.git_do("checkout", "A", "--recurse-submodules")
        # Ensure the HEAD has the same commit hash as tag 'A'.
        self.assertEqual(
            self.repo.git_do("rev-parse", "HEAD"),
            self.repo.git_do("rev-parse", "A"),
        )
        # Ensure HEAD of 'sub' submodule has the same commit hash as 'branch-a'
        # on the OG repo.
        self.assertEqual(
            self.repo.git_do("-C", ".git/modules/sub", "rev-parse", "HEAD"),
            self.sub_repo.git_do("rev-parse", "branch-a"),
        )
        # Ensure the 'sub' working copy has a file 'a.txt' (created on last
        # commit of branch 'branch-a' on OG repo).
        self.assertTrue(os.path.exists(os.path.join(self.repo.repo_path, "sub", "a.txt")))

    def test_checkout_hash_has_correct_submodule_refs(self):
        unrefd_hash = self.super_repo.git_do("rev-parse", "wip^")  # commit before top of 'wip'
        self.repo.git_do("fetch", "origin", "--tags", unrefd_hash.strip())
        self.repo.git_do("checkout", unrefd_hash.strip(), "--recurse-submodules")
        self.assertEqual(self.repo.git_do("rev-parse", "HEAD"), unrefd_hash)
        # Ensure HEAD of 'sub' submodule has the same commit hash as ref
        # 'branch-b^' on the OG repo.
        unrefd_sub_hash = self.sub_repo.git_do("rev-parse", "branch-b^")
        self.assertEqual(
            self.repo.git_do("-C", ".git/modules/sub", "rev-parse", "HEAD"),
            unrefd_sub_hash,
        )
        # Ensure the 'sub' working copy does _not_ have a file 'b.txt' (created
        # on last commit of branch 'branch-b' on OG repo).
        self.assertFalse(os.path.exists(os.path.join(self.repo.repo_path, "sub", "b.txt")))
        # Ensure the 'sub' working copy file 'sub.txt' has same file contents
        # as the same file at referenced commit on OG repo.
        self.assertEqual(
            self.repo.do("cat", "sub/sub.txt"),
            self.sub_repo.git_do("show", f"{unrefd_sub_hash.strip()}:sub.txt"),
        )


@nottest
def setup_test_repos(root_dir):
    # ----
    # setup the submodule repo and its remote:
    # - <root_dir>/bare-sub/...
    # - <root_dir>/sub/...
    bare_sub = GitRepo(os.path.join(root_dir, "bare-sub"))
    bare_sub.git_do("init", "--bare")
    sub = GitRepo(os.path.join(root_dir, "sub"))
    sub.git_do("init", "--initial-branch", "main")
    sub.git_do("remote", "add", "origin", bare_sub.repo_path)

    # add some commits and branches
    # main branch
    sub.cmd_and_commit("touch", "sub.txt")
    sub.cmd_into_file_and_commit(["echo", "main branch"], "sub.txt")
    sub.git_do("push", "origin", "main:main")
    # other branches
    for letter in "ab":
        sub.git_do("checkout", "-b", f"branch-{letter}", "main")  # at top of main
        sub.cmd_into_file_and_commit(["echo", f"hello from {letter}"], "sub.txt")
        sub.cmd_and_commit("touch", f"{letter}.txt")
        sub.git_do("push", "origin", f"branch-{letter}:branch-{letter}")
    # switch back to main (for log clarity)
    sub.checkout_default()
    #
    # Repo history is now:
    #
    # * 3020903 - $ touch b.txt (origin/branch-b, branch-b)
    # * 7cebedf - $ echo 'hello from b' >> sub.txt
    # | * fe383b4 - $ touch a.txt (origin/branch-a, branch-a)
    # | * 1f2250c - $ echo 'hello from a' >> sub.txt
    # |/
    # * e752961 - $ echo 'main branch' >> sub.txt (HEAD -> main, origin/main)
    # * 29f2041 - $ touch sub.txt

    # ----
    # setup the "superproject" (as git-submodule calls it) and remote
    # - <root_dir>/bare-super/...
    # - <root_dir>/super/...
    bare_super = GitRepo(os.path.join(root_dir, "bare-super"))
    bare_super.git_do("init", "--bare")
    super_ = GitRepo(os.path.join(root_dir, "super"))
    super_.git_do("init", "-b", "main")
    super_.git_do("remote", "add", "origin", bare_super.repo_path)

    # add some commits and branches
    # main branch
    super_.cmd_and_commit("git", "submodule", "add", bare_sub.repo_path, "sub")
    super_.git_do("push", "origin", "main:main")
    # track-a
    super_.git_do("checkout", "-b", "track-a")
    super_.cmd_and_commit("git", "-C", ".git/modules/sub", "checkout", "origin/branch-a")
    super_.git_do("tag", "A")
    super_.git_do("push", "--tags", "origin", "track-a:track-a")
    # wip
    unrefd_hash = sub.git_do("rev-parse", "branch-b^").strip()  # commit before top of 'branch-b'
    super_.git_do("checkout", "-b", "wip", "main", "--recurse-submodules")  # at HEAD of main
    super_.cmd_and_commit("git", "-C", ".git/modules/sub", "checkout", unrefd_hash)
    super_.cmd_and_commit("touch", "last-commit-on-wip.txt")
    super_.git_do("push", "origin", "wip:wip")
    # switch back to main (for log clarity)
    super_.checkout_default()
    #
    # Repo history is now:
    #
    # * c3e8bff - $ touch last-commit-on-wip.txt (origin/wip, wip)
    # * 162ef63 - $ git -C .git/modules/sub checkout 7cebedf
    # | * d4a0510 - $ git -C .git/modules/sub checkout origin/branch-a (tag: A, origin/track-a, track-a)
    # |/
    # * 2856307 - $ git submodule add <root_dir>/bare-sub sub (HEAD -> main, origin/main)

    # return the OG repos for tests
    return sub, super_


class GitRepo:

    def __init__(self, repo_path):
        self.repo_path = repo_path
        if not os.path.exists(repo_path):
            os.mkdir(repo_path)

    def checkout_default(self):
        self.git_do("checkout", "main", "--recurse-submodules")

    def git_do(self, *cmd):
        return self.do("git", *cmd)

    def do(self, *cmd):
        cmd_str = self.cmd_str(cmd)
        print(f"[{os.path.basename(self.repo_path)}] $ {cmd_str}")
        try:
            return subprocess.check_output(
                cmd_str,
                #stderr=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
                shell=True,
                cwd=self.repo_path,
                universal_newlines=True,  # TODO: >Python 3.6: change to `text=True`
            )
        except subprocess.CalledProcessError as exc:
            print(f"failed output:\n{exc.output}")
            raise

    def cmd_str(self, cmd):
        return " ".join(quote(a) for a in cmd)

    def cmd_and_commit(self, *cmd, commit_msg=None):
        with self._cmd_and_commit(*cmd, commit_msg=commit_msg) as output:
            return output

    @contextmanager
    def _cmd_and_commit(self, *cmd, commit_msg=None):
        yield self.do(*cmd)
        self.git_do("add", "--all")
        if commit_msg is None:
            commit_msg = f"$ {self.cmd_str(cmd)}"
        self.git_do("commit", "-m", commit_msg)

    def cmd_into_file_and_commit(self, cmd, repo_file):
        filepath = os.path.join(self.repo_path, repo_file)
        commit_msg = f"$ {self.cmd_str(cmd)} >> {repo_file}"
        with self._cmd_and_commit(*cmd, commit_msg=commit_msg) as output, \
             open(filepath, "a") as file:
            file.write(output)
