"""Goose workflow: Fedora/EPEL release automation for goose."""

from downstream_release import forge
from downstream_release import git
from downstream_release import srpm
from downstream_release import utils


class GooseWorkflow:
    """Release workflow for the goose project."""

    REPO_URL = "git@github.com:rhel-lightspeed/goose.git"

    DIST_GIT_URLS = {
        "pagure": "https://src.fedoraproject.org/rpms/goose",
        "gitlab": "https://gitlab.com/redhat/rhel/rpms/goose",
    }

    DIST_GIT_BRANCHES = {
        "pagure": ["rawhide", "f44", "f43", "epel9", "epel10", "epel10.2"],
        "gitlab": ["ext-rhel-10.2", "ext-rhel-9.8"],
    }

    COMMIT_MESSAGE = "Rebase for goose {version}"
    VENDOR_TARBALL_TARGET = "vendor-tarball"

    def propose(
        self,
        forge_name: str,
        version: str,
        branches: list[str] | None,
        dry_run: bool,
        offline: bool,
        yes: bool,
        keep: bool,
    ) -> None:
        """Stage 1: generate SRPM, import SRPM, open dist-git PRs."""
        valid_branches = self.DIST_GIT_BRANCHES[forge_name]
        branches = branches or valid_branches

        unknown = sorted(set(branches) - set(valid_branches))
        if unknown:
            raise SystemExit(
                f"Unknown branch(es) for goose on {forge_name!r}: "
                f"{', '.join(unknown)}\n"
                f"Valid branches: {', '.join(valid_branches)}"
            )

        url = self.DIST_GIT_URLS[forge_name]

        if dry_run:
            for branch in branches:
                source_branch = f"downstream-release/{version}/{branch}"
                flags = ", ".join(f for f in ["offline" if offline else "", "skip-diffs" if yes else ""] if f)
                import_note = f" ({flags})" if flags else ""
                print(
                    f"[{branch}] [dry-run] Would clone, import{import_note}, "
                    f"push, and open PR: {source_branch} -> {branch} on {url}"
                )
            return

        with git.clone(self.REPO_URL, branch="main", keep=keep) as upstream_dir:
            utils.run_make(upstream_dir, self.VENDOR_TARBALL_TARGET)
            srpm_path = srpm.generate_srpm(upstream_dir)

            project = forge.get_project(url)
            fork_username = forge.get_fork_username(project)
            fork_push_url = forge.get_fork_push_url(project)
            pkg = project.repo
            commit_message = self.COMMIT_MESSAGE.format(version=version)

            with git.clone(url, branch=valid_branches[0], single_branch=False, shallow=False, keep=keep) as distgit_dir:
                for branch in branches:
                    source_branch = f"downstream-release/{version}/{branch}"

                    git.checkout(distgit_dir, branch)
                    git.create_branch(distgit_dir, source_branch)
                    srpm.import_srpm(distgit_dir, srpm_path, offline=offline, skip_diffs=yes)
                    git.commit(distgit_dir, commit_message)
                    git.push(distgit_dir, fork_push_url, source_branch)

                    pr = forge.open_pr(
                        project=project,
                        title=f"Release {pkg} {version} for {branch}",
                        body=f"Automated downstream release of {pkg} {version}.",
                        target_branch=branch,
                        source_branch=source_branch,
                        fork_username=fork_username,
                    )
                    if pr:
                        print(f"[{branch}] PR #{pr.id}: {pr.url}")

    def build(
        self,
        branches: list[str] | None,
        dry_run: bool,
    ) -> None:
        """Stage 2: kick off Koji builds for merged PRs."""
        raise NotImplementedError("build stage is not yet implemented for goose.")

    def update(
        self,
        update_type: str,
        severity: str,
        bugs: list[str] | None,
        branches: list[str] | None,
        dry_run: bool,
    ) -> None:
        """Stage 3: create Bodhi updates."""
        raise NotImplementedError("update stage is not yet implemented for goose.")
