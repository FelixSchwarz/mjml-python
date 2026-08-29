#!/usr/bin/env python3
#
# SPDX-License-Identifier: MIT
# AI generated script so there is no copyright on this script. In case your
# jurisdiction is different, use MIT.
#
# /// script
# requires-python = ">= 3.9"
# dependencies = []
# ///
"""Pin GitHub Actions to full commit SHAs and update them to the latest release.

usage: update-workflow-actions.py [--check] [--allow-major-upgrades]
                                  [--cooldown-days DAYS] [--exclude ACTION] [FILE ...]

Every "uses: owner/repo@ref" is rewritten to

    uses: owner/repo@<40 char sha>  # <tag>

so the workflow always runs a known-good commit while the trailing comment keeps
the file readable. Without FILE all workflows in ".github/workflows/" are
processed.

By default an action is only updated within its current major version (taken
from the version comment, or from the ref if that is still a tag) because a new
major usually means changed inputs. "--allow-major-upgrades" lifts that
restriction.
"--check" reports outdated pins without touching any file and exits non-zero,
which makes it usable in CI.

"--exclude" can be repeated to leave named actions untouched.

Releases younger than "--cooldown-days" days (7 by default, 0 disables the
check) are skipped so a freshly published — possibly broken or compromised —
action is not picked up right away. The release date comes from the GitHub
release for that tag, falling back to the date of the tagged commit.

Local ("./foo"), docker ("docker://…") and fully qualified actions
("https://codeberg.org/…") are ignored as they are not on github.com.

The GitHub API allows only 60 unauthenticated requests per hour. The script uses
$GITHUB_TOKEN/$GH_TOKEN or the token from the "gh" CLI, but falls back to
unauthenticated requests if that token is not accepted.
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path


API_ROOT = 'https://api.github.com'
WORKFLOW_DIR = Path('.github/workflows')
MAX_TAG_PAGES = 5
MAX_RELEASE_PAGES = 5

# "- uses: owner/repo[/subdir]@ref" with an optional trailing "# version" comment
USES_RE = re.compile(
    r"""^(?P<prefix>\s*-?\s*uses:\s*['\"]?)
         (?P<action>[\w.-]+/[\w.-]+(?:/[\w./-]+)?)
         @(?P<ref>[^\s'\"\#]+)
         (?P<suffix>['\"]?[^\S\n]*(?:\#.*)?)$""",
    re.VERBOSE,
)
SEMVER_RE = re.compile(r'^v?(\d+)\.(\d+)\.(\d+)$')
MAJOR_RE = re.compile(r'^v?(\d+)\b')
SHA_RE = re.compile(r'^[0-9a-f]{40}$')


class Updater:
    def __init__(self, token, allow_major, cooldown_days, excluded_actions):
        self.token = token
        self.allow_major = allow_major
        self.cooldown_days = cooldown_days
        self.excluded_actions = set(excluded_actions)
        self.tag_cache = {}
        self.release_cache = {}
        self.commit_date_cache = {}
        self.errors = []

    # --- GitHub API ------------------------------------------------------
    def fetch_json(self, url):
        request = urllib.request.Request(url)
        request.add_header('Accept', 'application/vnd.github+json')
        request.add_header('X-GitHub-Api-Version', '2022-11-28')
        if self.token:
            request.add_header('Authorization', 'Bearer ' + self.token)
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response), response.headers.get('Link', '')

    def fetch_tags(self, repo):
        """Return {tag name: commit sha} for a "owner/repo" string, {} on error."""
        if repo in self.tag_cache:
            return self.tag_cache[repo]
        tags = {}
        url = '%s/repos/%s/tags?per_page=100' % (API_ROOT, repo)
        try:
            for _ in range(MAX_TAG_PAGES):
                if not url:
                    break
                payload, link_header = self.fetch_json(url)
                for tag in payload:
                    tags[tag['name']] = tag['commit']['sha']
                url = next_page_url(link_header)
        except urllib.error.HTTPError as e:
            hint = ' (rate limit exceeded?)' if (e.code == 403) else ''
            self.errors.append('%s: GitHub API error %s %s%s' % (repo, e.code, e.reason, hint))
            tags = {}
        except (urllib.error.URLError, OSError) as e:
            self.errors.append('%s: could not reach the GitHub API (%s)' % (repo, e))
            tags = {}
        self.tag_cache[repo] = tags
        return tags

    def fetch_release_dates(self, repo):
        """Return {tag name: publication date} from the repo's GitHub releases."""
        if repo in self.release_cache:
            return self.release_cache[repo]
        dates = {}
        url = '%s/repos/%s/releases?per_page=100' % (API_ROOT, repo)
        try:
            for _ in range(MAX_RELEASE_PAGES):
                if not url:
                    break
                payload, link_header = self.fetch_json(url)
                for release in payload:
                    published = parse_timestamp(release.get('published_at'))
                    if release.get('draft') or (published is None):
                        continue
                    dates[release['tag_name']] = published
                url = next_page_url(link_header)
        except urllib.error.HTTPError as e:
            # 404 just means the repository publishes tags but no releases
            if e.code != 404:
                self.errors.append('%s: could not read releases (%s %s), the cooldown '
                                   'may not be applied' % (repo, e.code, e.reason))
            dates = {}
        except (urllib.error.URLError, OSError) as e:
            self.errors.append('%s: could not read releases (%s), the cooldown '
                               'may not be applied' % (repo, e))
            dates = {}
        self.release_cache[repo] = dates
        return dates

    def fetch_commit_date(self, repo, sha):
        if sha in self.commit_date_cache:
            return self.commit_date_cache[sha]
        try:
            payload, _ = self.fetch_json('%s/repos/%s/commits/%s' % (API_ROOT, repo, sha))
            date = parse_timestamp(payload['commit']['committer']['date'])
        except (urllib.error.HTTPError, urllib.error.URLError, OSError) as e:
            self.errors.append('%s: could not read the date of commit %s (%s), the '
                               'cooldown may not be applied' % (repo, sha[:10], e))
            date = None
        except (KeyError, TypeError):
            date = None
        self.commit_date_cache[sha] = date
        return date

    def age_in_days(self, repo, tag, sha):
        """Age of a release, None if neither a release nor a commit date is known."""
        published = self.fetch_release_dates(repo).get(tag)
        if published is None:
            published = self.fetch_commit_date(repo, sha)
        if published is None:
            return None
        return (utc_now() - published).days

    def latest_tag(self, repo, tags, major):
        """Newest release tag which is not inside the cooldown period."""
        candidates = []
        for name, sha in tags.items():
            match = SEMVER_RE.match(name)
            if not match:
                # skips floating tags ("v7") and pre-releases ("v8.0.0-rc1")
                continue
            version = tuple(int(part) for part in match.groups())
            if (major is not None) and (version[0] != major):
                continue
            candidates.append((version, name, sha))
        candidates.sort(reverse=True)

        skipped = []
        for _, name, sha in candidates:
            if self.cooldown_days <= 0:
                return (name, sha, skipped)
            age = self.age_in_days(repo, name, sha)
            if (age is None) or (age >= self.cooldown_days):
                # an unknown age must not block the update forever
                return (name, sha, skipped)
            skipped.append(name)
        return (None, None, skipped)

    # --- rewriting -------------------------------------------------------
    def process_line(self, line):
        """Return (new line or None, message or None)."""
        match = USES_RE.match(line)
        if not match:
            return (None, None)
        action = match.group('action')
        if action in self.excluded_actions:
            return (None, None)
        ref = match.group('ref')
        repo = '/'.join(action.split('/')[:2])
        tags = self.fetch_tags(repo)
        if not tags:
            # the error was already recorded by fetch_tags()
            return (None, '%s: lookup failed, left unchanged' % action)
        major = None
        if not self.allow_major:
            major = current_major(ref, comment_version(match.group('suffix')), tags)
        tag, sha, skipped = self.latest_tag(repo, tags, major)
        cooled = ''
        if skipped:
            cooled = ' (%s: less than %d days old)' % (', '.join(skipped), self.cooldown_days)
        if not tag:
            return (None, '%s: no usable release tag found%s' % (action, cooled))
        new_line = rewrite(match, action, sha, tag)
        if new_line == line:
            return (None, '%s: %s (up to date)%s' % (action, tag, cooled))
        old = ref[:10] if SHA_RE.match(ref) else ref
        return (new_line, '%s: %s -> %s%s' % (action, old, tag, cooled))

    def process_file(self, path, check_only):
        lines = path.read_text(encoding='utf-8').splitlines(keepends=True)
        changed = False
        for i, line in enumerate(lines):
            stripped = line.rstrip('\n')
            new_line, message = self.process_line(stripped)
            if message:
                print('  %s' % message)
            if new_line is None:
                continue
            changed = True
            lines[i] = new_line + line[len(stripped):]
        if changed and not check_only:
            path.write_text(''.join(lines), encoding='utf-8')
        return changed


def next_page_url(link_header):
    for link in link_header.split(','):
        if 'rel="next"' not in link:
            continue
        match = re.search(r'<([^>]+)>', link)
        if match:
            return match.group(1)
    return None


def current_major(ref, version_comment, tags):
    """Guess the major version an action is currently pinned to."""
    for candidate in (version_comment, ref):
        if not candidate:
            continue
        match = MAJOR_RE.match(candidate)
        if match:
            return int(match.group(1))
    if SHA_RE.match(ref):
        # a bare sha without version comment: derive the major from a matching tag
        majors = [SEMVER_RE.match(name) for name, sha in tags.items() if sha == ref]
        known = [int(m.group(1)) for m in majors if m]
        if known:
            return max(known)
    return None


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc)


def parse_timestamp(value):
    """Parse a GitHub API timestamp ("2026-08-17T12:34:56Z")."""
    try:
        stamp = datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')
    except (TypeError, ValueError):
        return None
    return stamp.replace(tzinfo=datetime.timezone.utc)


def comment_version(suffix):
    _, _, comment = suffix.partition('#')
    tokens = comment.split()
    return tokens[0] if tokens else None


def rewrite(match, action, sha, tag):
    prefix = match.group('prefix')
    suffix = match.group('suffix')
    quote = prefix[-1] if prefix.endswith(("'", '"')) else ''
    spacing = ' '
    if '#' in suffix:
        spacing = suffix.partition('#')[0].lstrip("'\"") or ' '
    return '%s%s@%s%s%s# %s' % (prefix, action, sha, quote, spacing, tag)


def github_token():
    for env_name in ('GITHUB_TOKEN', 'GH_TOKEN'):
        token = os.environ.get(env_name)
        if token:
            return token
    try:
        gh = subprocess.run(
            ['gh', 'auth', 'token'],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            timeout=10, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return gh.stdout.decode('utf-8').strip() if (gh.returncode == 0) else None


def usable_token():
    """Return the token only if GitHub actually accepts it."""
    token = github_token()
    if not token:
        print('note: no GitHub token found, API requests are rate limited to 60/h')
        return None
    request = urllib.request.Request(API_ROOT + '/rate_limit')
    request.add_header('Authorization', 'Bearer ' + token)
    try:
        urllib.request.urlopen(request, timeout=30).close()
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            print('note: GitHub rejected the token (%s), continuing unauthenticated.\n'
                  '      Run "gh auth refresh -h github.com" or set $GITHUB_TOKEN.' % e.code)
            return None
        raise
    except (urllib.error.URLError, OSError):
        return token
    return token


def main():
    if sys.version_info < (3, 9):
        sys.exit('error: this script requires Python 3.9 or later')
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--check', action='store_true',
                        help='only report outdated pins, exit 1 if any were found')
    parser.add_argument('--allow-major-upgrades', action='store_true',
                        help='also update across major versions')
    parser.add_argument('--cooldown-days', type=int, default=7, metavar='DAYS',
                        help='ignore releases younger than DAYS days (default: 7, 0 disables)')
    parser.add_argument('--exclude', action='append', default=[], metavar='ACTION',
                        help='leave ACTION unchanged (may be repeated)')
    parser.add_argument('files', nargs='*', type=Path, metavar='FILE')
    args = parser.parse_args()

    paths = args.files
    if not paths:
        paths = sorted(WORKFLOW_DIR.glob('*.yml')) + sorted(WORKFLOW_DIR.glob('*.yaml'))
    if not paths:
        sys.exit('error: no workflow files found in "%s"' % WORKFLOW_DIR)

    updater = Updater(usable_token(), args.allow_major_upgrades, args.cooldown_days,
                      args.exclude)
    outdated = []
    for path in paths:
        print('%s' % path)
        if updater.process_file(path, args.check):
            outdated.append(path)

    if updater.errors:
        print('\n%d action(s) could not be checked:' % len(updater.errors))
        for error in updater.errors:
            print('  %s' % error)
        sys.exit(1)
    if not outdated:
        print('\nall actions are up to date')
    elif args.check:
        print('\n%d file(s) contain outdated action pins, '
              'run "just update-workflow-actions"' % len(outdated))
        sys.exit(1)
    else:
        print('\nupdated %d file(s)' % len(outdated))


if __name__ == '__main__':
    main()
