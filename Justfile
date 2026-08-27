# "--inexact" so this does not prune a local dev venv, in CI the venv is empty anyway
install-locked-dependencies:
    uv sync --locked --inexact --only-group build

# update "uv.lock" to the latest versions
update-dependencies:
    uv lock --upgrade
