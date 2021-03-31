mjml-stub
=============

This is an unofficial Python port of [mjml v4](https://github.com/mjmlio/mjml). It is implemented in pure Python and does not require JavaScript/NodeJS. mjml is a markup language created by [Mailjet](https://www.mailjet.com/) and designed to reduce the pain of coding a responsive email.

    pip install mjml


WARNING: stub implementation only!
------------------------------------
This library only implements a subset of the original MJML project. It lacks several features found in the JavaScript mjml implementation (e.g. minification, beautification and validation). Also the code likely contains many additional bugs.

The upside is that there are lot of possibilities for you to make a real difference when you improve the code :-)


Goals / Motivation
------------------------------------
This library should track the [JS version of mjml](https://github.com/mjmlio/mjml) so ideally you should get the same HTML. However even under the best circumstances this library will always lag a bit behind as each change must be translated to Python manually (a mostly mechanical process).

While I like the idea behind mjml and all the knowledge about the quirks to get acceptable HTML rendering by various email clients we did not want to deploy a Node.js-based stack on our production servers. We did not feel comfortable auditing all 220 JS packages which are installed by `npm install mjml` (and re-doing this whenever new versions are available). Also due to data-privacy concerns we were unable to use any third-party products (i.e. MJML's API offering).

After a short [spike](https://en.wikipedia.org/wiki/Spike_(software_development)) to check the viability of a Python implementation I went ahead and wrote enough code to ensure some existing messages could be converted to mjml. Currently the library is deployed in some light production scenarios.

Another benefit of using Python is that we can integrate that in our web apps more closely. As the startup overhead of CPython is much lower than Node.js we can also generate a few mails via CLI applications without massive performance problems. CPython uses ~70ms to translate a trivial mjml template to HTML while Node.JS needs ~650ms.



Documentation
------------------------------------
The idea is to implement the mjml XML dialect exactly like the JS implementation so eventually you should be able to use the [official docs](https://mjml.io/documentation/) and other online resources found on [mjml.io](https://mjml.io/). However we are nowhere near that right now! The current code can render the "Hello World" example as well as images, tables and groups but many components remain to be reimplemented. I'd love to see your pull requests to improve the current state though.


Alternatives / Additional Resources
------------------------------------

- **django-mjml**: If deploying NodeJS is not an issue and you are using Django you could use the well established [django-mjml](https://github.com/liminspace/django-mjml) library. That library integrates the mjml JavaScript implementation with Django templates so you can access all mjml features.
- **MJML.NET**: This is an unofficial port of mjml to C# ([github repo](https://github.com/LiamRiddell/MJML.NET/) which supports more components than this Python implementation.
- [email-bugs](https://github.com/hteumeuleu/email-bugs) is a github project which contains a lot of knowledge about rendering quirks in various email clients.
- [htmlemailcheck](https://www.htmlemailcheck.com/knowledge-base/) is a commercial offering to help you checking email rendering in various environments. I don't have any experience with their services but they provide a free knowledgebase.

