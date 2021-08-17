import { html } from 'https://unpkg.com/htm/preact/standalone.module.js';
import { skipForward, square } from './icons.js';

import { Server } from './util.js';

export default function Controls(props) {
  const song = props.status.music;

  if (song)
    return html`<div>
      <button class="icon controls" onClick=${() => fetch(`${Server}/stop`).then(() => setTimeout(props.getData, 500))}>${square}</button>
      <button
        class="icon controls"
        style=${{ marginRight: '1.75rem' }}
        onClick=${() => fetch(`${Server}/next`).then(() => setTimeout(props.getData, 500))}
      >
        ${skipForward}
      </button>
    </div>`;
}
