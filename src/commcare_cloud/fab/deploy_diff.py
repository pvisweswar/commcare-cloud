import re
from collections import defaultdict

from fabric.colors import red, blue, cyan, yellow
from gevent.pool import Pool

from commcare_cloud.fab.git_repo import _github_auth_provided


LABELS_TO_EXPAND = [
    "reindex/migration",
]


class DeployDiff:
    def __init__(self, repo, last_commit, deploy_commit):
        self.repo = repo
        self.last_commit = last_commit
        self.deploy_commit = deploy_commit

    @property
    def url(self):
        """Human-readable diff URL"""
        return "{}/compare/{}...{}".format(self.repo.html_url, self.last_commit, self.deploy_commit)

    def print_deployer_diff(self):
        if not (_github_auth_provided() and self.last_commit and self.deploy_commit):
            return

        short, long = sorted([self.last_commit, self.deploy_commit], key=lambda x: len(x))
        if (self.last_commit == self.deploy_commit or (
            long.startswith(short)
        )):
            print(red("Versions are identical. No changes since last deploy."))
            return

        pr_numbers = self._get_pr_numbers()
        if len(pr_numbers) > 500:
            print(red("There are too many PRs to display"))
            return
        elif not pr_numbers:
            print(blue("No PRs merged since last release."))
            print(f"\tView full diff here: {self.url}")
            return

        pool = Pool(5)
        pr_infos = [_f for _f in pool.map(self._get_pr_info, pr_numbers) if _f]

        print(blue("\nList of PRs since last deploy:"))
        self._print_prs_formatted(pr_infos)

        prs_by_label = self._get_prs_by_label(pr_infos)
        if prs_by_label:
            print(red('You are about to deploy the following PR(s), which will trigger a reindex or migration. Click the URL for additional context.'))
            self._print_prs_formatted(prs_by_label['reindex/migration'])

    def _get_pr_numbers(self):
        comparison = self.repo.compare(self.last_commit, self.deploy_commit)
        return [
            int(re.search(r'Merge pull request #(\d+)',
                          repo_commit.commit.message).group(1))
            for repo_commit in comparison.commits
            if repo_commit.commit.message.startswith('Merge pull request')
        ]

    def _get_pr_info(self, pr_number):
        pr_response = self.repo.get_pull(pr_number)
        if not pr_response.number:
            # Likely rate limited by Github API
            return None
        assert pr_number == pr_response.number, (pr_number, pr_response.number)

        labels = [label.name for label in pr_response.labels]

        return {
            'title': pr_response.title,
            'url': pr_response.html_url,
            'labels': labels,
        }

    def _get_prs_by_label(self, pr_infos):
        prs_by_label = defaultdict(list)
        for pr in pr_infos:
            for label in pr['labels']:
                if label in LABELS_TO_EXPAND:
                    prs_by_label[label].append(pr)
        return dict(prs_by_label)

    def _print_prs_formatted(self, pr_list):
        for pr in pr_list:
            print(
                "- ", cyan(pr['title']),
                yellow(pr['url']),
                ", ".join(label for label in pr['labels']),
            )
