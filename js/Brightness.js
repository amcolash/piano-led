import { html } from 'https://unpkg.com/htm/preact/standalone.module.js';

import { sun } from './icons.js';
import { Server } from './util.js';

export default function Brightness(props) {
  const brightness = props.status.brightness;

  return html`<div class="brightness" style=${{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
    <div style=${{ color: 'var(--palette3)', width: '2.25rem', height: '2.25rem', marginRight: '0.5rem' }}>${sun}</div>
    <input
      type="range"
      min="0"
      max="20"
      value=${brightness}
      onChange=${(e) => fetch(`${Server}/brightness?value=${e.target.value}`).then(() => setTimeout(props.getData, 500))}
    />
  </div>`;
}
