import { html, useState } from 'https://unpkg.com/htm/preact/standalone.module.js';

import { Button } from './Button.js';

import { volume2, volumeX } from './icons.js';
import { Server } from './util.js';

export default function Volume(props) {
  const volume = props.status.volume;
  const [lastVolume, setLastVolume] = useState(0);

  return html`<div class="volume" style=${{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
    <${Button}
      class="volumeButton"
      style=${{ color: 'var(--palette2)', marginRight: '0.5rem', cursor: 'pointer' }}
      tabindex="0"
      onClick=${() => {
        let vol = lastVolume;
        if (volume !== 0) {
          setLastVolume(volume);
          vol = 0;
        }

        fetch(`${Server}/volume?value=${vol}`)
          .then((response) => response.json())
          .then((status) => props.setStatus({ ...props.status, volume: status.volume }));
      }}
    >
      ${volume === 0 ? volumeX : volume2}
    </${Button}>
    <input
      type="range"
      min="0"
      max="1"
      step="0.05"
      value=${volume}
      onChange=${(e) =>
        fetch(`${Server}/volume?value=${e.target.value}`)
          .then((response) => response.json())
          .then((status) => props.setStatus({ ...props.status, volume: status.volume }))}
    />
  </div>`;
}
