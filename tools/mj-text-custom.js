const MjText = require('mjml-text');

class MjTextCustom extends MjText {
  static componentName = 'mj-text-custom';

  render() {
    const content = super.render();
    return `<div>START CUSTOM WRAPPER</div>${content}<div>END CUSTOM WRAPPER</div>`;
  }
}

class MjTextOverride extends MjText {
  // No custom componentName - inherits 'mj-text' from parent, thus overriding it
  static get defaultAttributes() {
    return {
      ...super.defaultAttributes,
      align: 'right',
      color: 'red',
      'font-size': '26px',
    };
  }

  render() {
    const content = super.render();
    return `<div>***</div>${content}<div>***</div>`;
  }
}

module.exports = { MjTextCustom, MjTextOverride };
