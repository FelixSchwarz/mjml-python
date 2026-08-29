# query OSV for known malware before syncing
export UV_MALWARE_CHECK := "1"

# Install the build backend used by the current lockfile.
install-locked-dependencies:
    uv sync --locked --only-group build

# update "uv.lock" to the latest versions
update-dependencies:
    uv lock --upgrade

# Build isolation deliberately does not use "uv.lock". Export the locked build
# backend and pass the resulting, hashed constraints to "uv build" instead.
update-build-constraints:
    uv lock --upgrade-package hatchling
    uv export --frozen --only-group build --output-file build-constraints.txt

build:
    uv build --wheel --build-constraint build-constraints.txt --require-hashes

update-prek-hooks:
    uv run --group quality prek update --freeze --cooldown-days=7

# pin GitHub Actions in ".github/workflows" to the latest commit sha
# (stays within the current major version unless `--allow-major-upgrades`
# is used)
update-workflow-actions *ARGS:
    ./tools/update-workflow-actions.py --cooldown-days=7 {{ARGS}}
