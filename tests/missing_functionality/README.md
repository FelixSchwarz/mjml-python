# Imported MRML test templates

The `.mjml` files in this directory were imported from MRML, the Rust MJML
implementation by Jérémie Drouet (<https://github.com/jdrouet/mrml>), from
`packages/mrml-core/resources/compare/success/`.

The whole MRML corpus (156 templates) was imported and rendered with this port;
the output was compared against upstream mjml 5.4.0 using `htmlcompare`, the
same comparison the regular test suite uses. **Only the templates whose output
differs were kept** — the other 129 already render identically here and would
add no coverage.

The `-expected.html` files were *not* taken from MRML. They were generated from
the imported `.mjml` with `tools/update-expected-html.py` and the real Node
mjml 5.4.0, exactly like the files in `tests/testdata/`.

Every test here is marked `xfail`: each one is a known deviation from upstream.
Once a deviation is fixed, move the template pair to `tests/testdata/` and add
its id to `tests/upstream_alignment_test.py` instead.


## Licensing

MRML is MIT licensed (`LICENSE` in the repository root, `license = "MIT"` in
`Cargo.toml`). Provenance was checked per file:

- 24 of the 27 templates were written by Jérémie Drouet in 2020, who is the
  repository owner and their sole author.
- `mj-hero-divider` and `mj-wrapper-full-width-section-background` were added
  by Jérémie Drouet in 2026 (mrml commits 9d831ce, c09fcfb).
- `mj-divider-alignment` was added by Alex Lurvey in 2025 (mrml commit
  14e6a82, with a DCO `Signed-off-by`).

None of the files carries a license header, a copyright notice, or a comment
pointing to a different origin, and no commit message indicates that a template
was copied in from a third party.

One historical detail worth recording: MRML was **not** MIT licensed from the
start. Until March 2024 it used the "Jolimail Source Available License", a
source-available and *not* open-source license; commit 7272087 ("chore: switch
license to MIT", 2024-03-21) replaced it with MIT for the entire repository.
The 2020 templates are therefore only usable under MIT via that relicensing —
which the copyright holder performed himself, so it covers his own earlier
files. Consequently the current MRML `main` is the valid source for these
files; an old checkout from before March 2024 is not.
