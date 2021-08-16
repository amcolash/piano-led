import { html, useEffect, useState } from 'https://unpkg.com/htm/preact/standalone.module.js';
import Folder from './Folder.js';

import { skipForward, square } from './icons.js';
import { Server } from './util.js';

export default function NowPlaying(props) {
  const [musicData, setMusicData] = useState({ files: {} });

  useEffect(() => {
    fetch(`${Server}/files`)
      .then((response) => response.json())
      .then((data) => setMusicData(data));
  }, []);

  const song = props.status.music;

  return html`<div>
    <div style=${{ flexGrow: '100%', textAlign: 'center' }}>${song || 'Nothing Playing'}</div>
    <div style=${{ display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '2rem' }}>
      ${song &&
      html`<button class="icon" onClick=${() => fetch(`${Server}/stop`).then(() => setTimeout(props.getData, 500))}>${square}</button
        ><button
          class="icon"
          style=${{ marginRight: '1.75rem' }}
          onClick=${() => fetch(`${Server}/next`).then(() => setTimeout(props.getData, 500))}
        >
          ${skipForward}
        </button>`}

      <${Folder} musicData=${musicData} getData=${props.getData} />
    </div>
  </div>`;
}
