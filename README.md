mjml-stub
=============

This is an unofficial Python port of [mjml](https://github.com/mjmlio/mjml) - a markup language created by [Mailjet](https://www.mailjet.com/) and designed to reduce the pain of coding a responsive email.

WARNING: stub implementation only!
------------------------------------
This library only implements a bare minimum to generate HTML from some mjml elements. It lacks most important features found in the JavaScript mjml implementation. Also the code likely contains many additional bugs and is not used in production anywhere!

The upside is that there are lot of possibilities for you to make a real difference when you improve the code :-)


Goals / Motivation
------------------------------------
This library should track the [JS version of mjml](https://github.com/mjmlio/mjml) closely so ideally you should get the same HTML. However even under the best circumstances this library will always lag a bit behind as each changes must be translated to Python manually (a mostly mechanical process).

While I like the idea behind mjml and all the knowledge about the quirks to get acceptable HTML rendering by various email clients we did not want to deploy a Node.js-based stack on our production servers. We did not feel comfortable auditing all 220 JS packages which are installed by `npm install mjml` (and re-doing this whenever new versions are available). Therefore I decided to spent a few days in a spike to check if we could do a minimal Python port. I'm not sure yet if this code will ever be used in production but let's publish what we have.

Another benefit of using Python is that we can integrate that in our web apps more closely. Also the startup overhead of CPython is much lower than Node.js so we can also generate a few mails via CLI applications without massive performance problems (CPython uses ~70ms to translate a trivial mjml template to HTML while Node.JS needs ~650ms).



Documentation
------------------------------------
The idea is to implement the mjml XML dialect exactly like the JS implementation so eventually you should be able to use the [official docs](https://mjml.io/documentation/) and other online resources found on [mjml.io](https://mjml.io/). However we are nowhere near that right now! The current code is barely able to render the "Hello World" example. I'd love to see your pull requests to improve the current state though.

