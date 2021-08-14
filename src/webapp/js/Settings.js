import { html } from 'https://unpkg.com/htm/preact/standalone.module.js';

import { sliders } from './icons.js';
import { Server } from './util.js';

export default function Settings(props) {
  const palettes = props.status.palettes || [];

  return html`
    <div class="icon" style=${{ position: 'absolute', top: '1rem', right: '1rem' }}>
      ${sliders}
      <select
        class="icon"
        style=${{ position: 'absolute', top: 0, left: 0, color: 'rgba(0,0,0,0)' }}
        onChange=${(e) => fetch(`${Server}/palette?value=${e.target.value}`).then(() => setTimeout(props.getData, 500))}
        value=${null}
      >
        ${palettes.map((p) => html`<option value=${p}>${p}</option>`)}
      </select>
    </div>
  `;
}
