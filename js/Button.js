import { html } from 'https://unpkg.com/htm/preact/standalone.module.js';

// Code from: https://dev.to/johnlucasg/make-react-navigation-accessible-again

const buildHandleEnterKeyPress =
  (onClick) =>
  ({ key }) => {
    if (key === 'Enter') {
      onClick();
    }
  };

export const Button = (props) =>
  html`<div
    class=${props.class}
    onClick=${props.onClick}
    onKeyPress=${buildHandleEnterKeyPress(props.onClick)}
    tabindex="0"
    style=${{ ...props.style, cursor: 'pointer' }}
  >
    ${props.children}
  </div>`;
