const mjml2html = require('mjml');
const { registerComponent } = require('mjml-core');
const { registerDependencies } = require('mjml-validator');
const { MjTextCustom, MjTextOverride } = require('./mj-text-custom');
const fs = require('fs').promises;
const path = require('path');

async function main() {
  // Require input/output paths via CLI: `node script.js <input> <output>`
  const inputArg = process.argv[2];
  const outputArg = process.argv[3];
  if (!inputArg || !outputArg) {
    console.error('Usage: node create-expected-html-for-custom-component.js <input.mjml> <output.html>');
    process.exit(2);
  }

  registerComponent(MjTextCustom);
  registerComponent(MjTextOverride);
  // register dependencies to allow custom components inside mj-column
  registerDependencies({
    'mj-column': ['mj-text-custom'],
  });

  const mjmlPath = path.resolve(inputArg);
  const mjmlString = await fs.readFile(mjmlPath, 'utf8');

  const { html, errors } = mjml2html(mjmlString);

  const htmlPath = path.resolve(outputArg);
  await fs.writeFile(htmlPath, html, 'utf8');

  if (errors && errors.length > 0) {
    console.error('MJML Errors:', errors);
    process.exitCode = 1;
  }
}

main().catch(err => {
  console.error('Script failed:', err);
  process.exitCode = 1;
});
