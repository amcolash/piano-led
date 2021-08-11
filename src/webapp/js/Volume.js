import { html } from 'https://unpkg.com/htm/preact/standalone.module.js';

import { Server } from './util.js';

export default function Volume(props) {
  const volume = props.status.volume;

  return html`<div style=${{ display: 'flex', justifyContent: 'center' }}>
    <input
      type="range"
      min="0"
      max="127"
      value=${volume}
      onChange=${(e) => fetch(`${Server}/volume?value=${e.target.value}`).then(props.getData)}
    />
  </div>`;
}
