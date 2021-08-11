import { html, useEffect, useState } from 'https://unpkg.com/htm/preact/standalone.module.js';

import { playCircle, skipForward, stopCircle } from './icons.js';
import { useInterval } from './useInterval.js';
import { Palette, Server } from './util.js';

const icon = {
  background: 'unset',
  border: 'none',
  color: Palette[2],
  marginTop: '2rem',
  width: '5rem',
  height: '5rem',
  cursor: 'pointer',
  borderRadius: '50%',
};

export default function NowPlaying() {
  const [song, setSong] = useState();

  const getData = () => {
    fetch(`${Server}/music`)
      .then((response) => response.text())
      .then((data) => setSong(data));
  };

  useEffect(getData, []);
  useInterval(getData, 10000);

  return html`<div>
    <div style=${{ flexGrow: '100%' }}>${song || 'Nothing Playing'}</div>
    <div style=${{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      ${song &&
      html`<button
        style=${icon}
        onClick=${() => {
          fetch(`${Server}/stop`).then(() => setTimeout(getData, 500));
          setSong('');
        }}
      >
        ${stopCircle}
      </button>`}

      <button
        style=${{ ...icon, height: song ? '3.75rem' : icon.height, width: song ? '3.75rem' : icon.width }}
        onClick=${() => {
          fetch(`${Server}/play`).then(() => setTimeout(getData, 500));
          setSong('Starting Music...');
        }}
      >
        ${song ? skipForward : playCircle}
      </button>
    </div>
  </div>`;
}
