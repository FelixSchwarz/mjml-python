# Install the build backend used by the current lockfile.
install-locked-dependencies:
    uv sync --locked --only-group build

# update "uv.lock" to the latest versions
update-dependencies:
    uv lock --upgrade

update-prek-hooks:
    uv run --group dev prek update --freeze --cooldown-days=7

# pin GitHub Actions in ".github/workflows" to the latest commit sha
# (stays within the current major version unless `--allow-major-upgrades`
# is used)
update-workflow-actions *ARGS:
    ./tools/update-workflow-actions.py --cooldown-days=7 {{ARGS}}
