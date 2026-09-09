# mjml-python

A pure Python implementation of [MJML v5](https://github.com/mjmlio/mjml) (unreleased, "main" branch), the email markup language created by [Mailjet](https://www.mailjet.com/). Build responsive HTML emails without requiring JavaScript, Node.js or Rust. For MJML v4, use the 0.x release series.

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
- `validation_level` - `'skip'`, `'soft'` (default), or `'strict'`, see [Validation](#validation)

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
- `--validate` - report problems in the template, generate no HTML and exit
  nonzero when something was found
- `--validation-level=<level>` - `skip`, `soft` (default), or `strict`

## Validation

Validation checks an MJML template either on its own or before generating HTML.
It reports unknown or misplaced elements, unsupported attributes, invalid
attribute values, unreadable includes, and MJML JS features which this Python
port cannot reproduce correctly.

### Validation levels

`mjml_to_html()` supports three validation levels:

| Level            | Behavior                                                                                              |
| ---------------- | ----------------------------------------------------------------------------------------------------- |
| `skip`           | Generate HTML without validating the template.                                                        |
| `soft` (default) | Validate and generate HTML. Problems are returned in `result.errors`.                                 |
| `strict`         | Validate first. Generate HTML only when no errors were found; otherwise raise `MJMLValidationErrors`. |

### Command line

Use `--validation-level` to validate while converting a template:

```sh
# Report problems (on stderr) but generate HTML anyway if at all possible

# Refuse to generate HTML when validation fails
mjml --validation-level=strict my_email.mjml
```

To validate without generating HTML, use:

```sh
mjml --validate my_email.mjml
```

`--validate` writes problems to standard error and exits with a nonzero status
when any were found.

### Python API

Soft validation lets an application report problems without preventing HTML
generation:

```py
from mjml import mjml_to_html

result = mjml_to_html(mjml_input, validation_level='soft')

for error in result.errors:
    print(error.formatted_message())

html = result.html
```

Strict validation prevents generation when the template contains errors:

```py
from mjml import MJMLValidationErrors, mjml_to_html

try:
    result = mjml_to_html(mjml_input, validation_level='strict')
except MJMLValidationErrors as error:
    for validation_error in error.errors:
        print(validation_error.formatted_message())
```

#### Validation without rendering

Use `validate()` when only the validation result is needed:

```py
from mjml import validate

errors = validate(mjml_input)

for error in errors:
    print(error.formatted_message())
```

Each `ValidationError` provides a message, the affected element, its source
location when available, and the rule which reported it. Included templates
also retain information about the chain of files through which they were
included. `formatted_message()` combines this information into a
human-readable line.


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
from mjml.core.api import ComponentCategory
from mjml.elements import BodyComponent

class MyComponent(BodyComponent):
    component_name = 'mj-my-component'
    categories = frozenset({ComponentCategory.BODY_ELEMENT})

    @classmethod
    def allowed_attrs(cls):
        # the element it is placed in reads these from every child
        return {
            'padding'       : 'unit(px,%){1,4}',
            'padding-top'   : 'unit(px,%)',
            'padding-right' : 'unit(px,%)',
            'padding-bottom': 'unit(px,%)',
            'padding-left'  : 'unit(px,%)',
        }

    def render(self):
        return '<p>whatever this component renders</p>'

result = mjml_to_html(mjml_input, custom_components=[MyComponent])
```

`categories` says where the component may be used and is what
`registerDependencies()` declares in the JavaScript implementation. A component
which declares none is reported as misplaced wherever it is put, exactly as
mjml js rejects a custom component which registered no dependencies. A subclass
of a built-in component inherits the categories of the element it derives from.


## Limitations

Compared to the JavaScript MJML implementation, the following features are **not** available:

- **Minification** of the generated HTML
- **Beautification** (pretty-printing) of the generated HTML

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
