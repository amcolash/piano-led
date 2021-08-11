import { html } from 'https://unpkg.com/htm/preact/standalone.module.js';

import { play, skipForward, square } from './icons.js';
import { Server } from './util.js';

export default function NowPlaying(props) {
  console.log(props);
  const song = props.status.music;

  return html`<div>
    <div style=${{ flexGrow: '100%' }}>${song || 'Nothing Playing'}</div>
    <div style=${{ display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '2rem' }}>
      ${song &&
      html`<button class="icon" onClick=${() => fetch(`${Server}/stop`).then(() => setTimeout(props.getData, 500))}>${square}</button>`}

      <button class="icon" onClick=${() => fetch(`${Server}/play`).then(() => setTimeout(props.getData, 500))}>
        ${song ? skipForward : play}
      </button>
    </div>
  </div>`;
}
