import { html, useEffect, useReducer } from 'https://unpkg.com/htm/preact/standalone.module.js';

import { Button } from './Button.js';

import { skipForward, square } from './icons.js';
import { Server } from './util.js';

export default function Progress(props) {
  const progress = Math.min(1, (Date.now() / 1000 - props.status.playStart) / props.status.musicDuration);

  // Force updates every half second to make things look nice
  const [ignored, forceUpdate] = useReducer((x) => x + 1, 0);
  useEffect(() => {
    const i = setInterval(forceUpdate, 500);
    return () => clearInterval(i);
  }, []);

  // <input type="range" min="0" max="1" step="0.01" disabled value=${progress} style=${{ margin: '0 0.75rem' }} />
  return html`<div class="progress" style=${{ display: 'flex', justifyContent: 'center', alignItems: 'center', fontSize: '1.15rem' }}>
    <${Button}
      class="controls stop"
      onClick=${() =>
        fetch(`${Server}/stop`)
          .then((response) => response.json())
          .then(() => props.setStatus({ ...props.status, music: null }))}
    >
      ${square}
    </${Button}>
    <${Button}
      class="controls next"
      onClick=${() =>
        fetch(`${Server}/next`)
          .then((response) => response.json())
          .then((status) => props.setStatus({ ...props.status, music: status.music }))}
    >
      ${skipForward}
    </${Button}>
    <div style=${{ marginTop: '0.1rem' }}>${new Date(progress * props.status.musicDuration * 1000)
    .toISOString()
    .substr(14, 5)} / ${new Date(props.status.musicDuration * 1000).toISOString().substr(14, 5)}</div>
  </div>`;
}
