import { html } from 'https://unpkg.com/htm/preact/standalone.module.js';
import { volume2 } from './icons.js';

import { Server } from './util.js';

export default function Volume(props) {
  const volume = props.status.volume;

  return html`<div style=${{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
    <div style=${{ color: 'var(--palette2)', width: '2.25rem', height: '2.25rem', marginRight: '0.5rem' }}>${volume2}</div>
    <input
      type="range"
      min="0"
      max="127"
      value=${volume}
      onChange=${(e) => fetch(`${Server}/volume?value=${e.target.value}`).then(() => setTimeout(props.getData, 500))}
    />
  </div>`;
}
