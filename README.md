# mjml-python

A pure Python implementation of [MJML v4](https://github.com/mjmlio/mjml), the email markup language created by [Mailjet](https://www.mailjet.com/). Build responsive HTML emails without requiring JavaScript, Node.js or Rust.

All standard MJML components are supported, and the rendered output closely follows the upstream JavaScript implementation.


## Installation

```sh
pip install mjml
```

For optional CSS inlining support:

```sh
pip install mjml[css_inlining]
```


## Usage

### Python API

```py
from mjml import mjml_to_html

# From a file
with open('my_email.mjml', 'rb') as fp:
    result = mjml_to_html(fp)

# From a string
result = mjml_to_html('<mjml><mj-body>...</mj-body></mjml>')

assert not result.errors
html: str = result.html
```

The `mjml_to_html()` function accepts several optional parameters:

- `template_dir` - base directory for resolving `<mj-include>` paths
- `keep_comments` - preserve HTML comments in output (default: `True`)
- `custom_components` - list of custom component classes to register

### CLI

```sh
# Convert and print to stdout
$ mjml my_email.mjml

# Convert and write to file
$ mjml my_email.mjml -o output.html

# Read from stdin
$ cat my_email.mjml | mjml -
```

CLI options:

- `--template-dir=<path>` - base directory for `<mj-include>` (default: directory of the input file)
- `--config.keepComments=False` - strip HTML comments from output


## Supported Components

All standard MJML v4 components are implemented. The project comes with no guarantee that additions or changes to the standard are implemented, or in which timing -- but coverage of the standard is a principal objective of the project.

**Layout:** mj-body, mj-section, mj-column, mj-group, mj-wrapper, mj-hero

**Content:** mj-text, mj-image, mj-button, mj-table, mj-divider, mj-spacer, mj-raw

**Interactive:** mj-accordion, mj-carousel, mj-navbar, mj-social

**Head:** mj-head, mj-title, mj-preview, mj-style, mj-attributes, mj-breakpoint, mj-font, mj-html-attributes

**Other:** mj-include (file includes with relative/absolute paths)

### Custom Components

You can register your own components:

```py
from mjml.core.api import Component

class MyComponent(Component):
    component_name = 'mj-my-component'
    # ...

result = mjml_to_html(mjml_input, custom_components=[MyComponent])
```


## Limitations

Compared to the JavaScript MJML implementation, the following features are **not** available:

- **Minification** of the generated HTML
- **Beautification** (pretty-printing) of the generated HTML
- **Validation** of MJML templates (attribute checks, structural rules)
- **Includes inside `<mj-head>`**

If you need these features, see the [Alternatives](#alternatives--additional-resources) section below.


## Goals / Motivation

This library tracks the [JavaScript version of mjml](https://github.com/mjmlio/mjml) so you should get the same HTML output for supported components. There may be minor differences due to the manual porting process.

Why a Python port?

- **No Node.js dependency**: avoid deploying a Node.js stack and auditing hundreds of npm packages
- **Data privacy**: no need for third-party API services
- **Fast startup**: CPython converts a trivial template in ~70ms vs ~650ms for Node.js, making it practical for CLI use and on-demand email generation
- **Tight integration**: embed directly in Python web applications, Django/Flask views, or background workers


## Alternatives / Additional Resources

- **django-mjml**: integrates the JavaScript mjml with Django templates ([github](https://github.com/liminspace/django-mjml)). Requires Node.js but gives access to all upstream features.
- **MJML.NET**: unofficial C# port of mjml ([github](https://github.com/LiamRiddell/MJML.NET/))
- **mrml**: Rust implementation of mjml ([github](https://github.com/jdrouet/mrml))
- [email-bugs](https://github.com/hteumeuleu/email-bugs): knowledge base about rendering quirks in email clients
- [htmlemailcheck](https://www.htmlemailcheck.com/knowledge-base/): commercial email rendering checker with a free knowledge base
- [#emailgeeks](https://email.geeks.chat): Slack community for email developers and designers
