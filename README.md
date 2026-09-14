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

- `includes` - enable `<mj-include>`, which is off by default, see [Includes](#includes)
- `template_dir` - where relative `<mj-include>` paths start when the template was not read from a file, see [Includes](#includes)
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

- `--include-path=<dir>` - enable `<mj-include>` for files below this directory, repeatable, see [Includes](#includes)
- `--template-dir=<path>` - where relative `<mj-include>` paths start; required when `-` is used with `--include-path`, rejected otherwise
- `--config.keepComments=False` - strip HTML comments from output
- `--validate` - report problems in the template, generate no HTML and exit
  nonzero when something was found
- `--validation-level=<level>` - `skip`, `soft` (default), or `strict`

A missing input file, an output file which cannot be written and input which
is not UTF-8 or contains no `<mjml>` are reported in one line on stderr, with
exit status 1.

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

`mj-include` is the exception: an include which was not expanded leaves the mail
without the file it names, which no validation level makes acceptable. It raises
`MJMLIncludeError` before rendering, `skip` included. See [Includes](#includes).

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

`MJMLValidationErrors` derives from `MJMLError`, the common base class of the
exceptions `mjml` raises itself.

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

All standard MJML v5.4 components are implemented. The project comes with no guarantee that additions or changes to the standard are implemented, or in which timing -- but coverage of the standard is a principal objective of the project.

**Layout:** mj-body, mj-section, mj-column, mj-group, mj-wrapper, mj-hero

**Content:** mj-text, mj-image, mj-button, mj-table, mj-divider, mj-spacer, mj-raw

**Interactive:** mj-accordion, mj-carousel, mj-navbar, mj-social

**Head:** mj-head, mj-title, mj-preview, mj-style, mj-attributes, mj-breakpoint, mj-font, mj-html-attributes

**Other:** mj-include (disabled by default, see [Includes](#includes))

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


## Includes

`mj-include` inserts other MJML, HTML or CSS files into a template. A template
which reads files is only safe when every template is trusted. Therefore `mj-include`
is disabled by default, as in MJML JS since version 5. Please consider using a
templating engine such as Jinja2 or the Django template language if you want to
split your MJML into reusable parts.

To enable includes, name the directories they may read:

```py
from mjml import IncludePolicy, mjml_to_html

with open('templates/newsletter.mjml', 'rb') as fp:
    result = mjml_to_html(fp, includes=IncludePolicy(roots=['templates']))
```

```sh
$ mjml --include-path=templates templates/newsletter.mjml
```

`validate()` accepts `includes` as well.

### Include types

- `type="mjml"` (the default) parses the included file as a template: its
  `mj-head` joins the document's head, its body content takes the place of the
  `mj-include`. A file without `<mjml>` is wrapped in `<mjml><mj-body>`.
- `type="css"` becomes an `mj-style` at the end of the head, no matter where
  the include appears; `css-inline="inline"` makes it an inlined one.
- `type="html"` is inserted verbatim.

### Where includes may read

- only below the directories in `roots`, and at least one is required. Unlike
  MJML JS, the directory of the template is not allowed implicitly.
- a relative include path is resolved against the file which contains it. The
  directory it starts from is not readable by itself:
  `path="../shared/head.mjml"` is denied unless the file it names lies below
  `roots`.
- a template which was not read from a file has no such directory and needs
  `template_dir`, on the command line `--template-dir` with `-`.

```py
policy = IncludePolicy(roots=['templates', '/app/code/shared-layouts'])
result = mjml_to_html(mjml_input, template_dir='templates', includes=policy)
```

A template read from stdin has no file of its own, so it needs `--template-dir`:

```sh
$ mjml --include-path=templates --template-dir=templates - < templates/newsletter.mjml
```

### Denied includes

An include path must be relative and must not contain a NUL byte; a path which
names a Windows drive or a UNC share is refused on every platform, not just on
Windows. Symlinks are resolved before a target is compared with the allowed
directories, and an include is denied when its path

- leads outside the allowed directories, or
- leads nowhere.

**An include policy confines which files a template may name. It does not hold
against an attacker who can write to the file system.** The path is resolved
and checked before the file is opened, so a directory which is replaced by a
symlink in between is not caught: the allowed directories and every directory
above them must be writable only by the deployment itself.

### When an include fails

A disabled, denied or unusable `mj-include` leaves the mail without the file it
names, so `mjml_to_html()` refuses to render it at all: it raises
`MJMLIncludeError` at every validation level, `skip` included. The `mjml`
command prints the problem, writes no output file and exits 1.

`validate()` never raises. It reports the problem as an error, like any other
validation error.


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
