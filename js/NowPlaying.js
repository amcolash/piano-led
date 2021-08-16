import { html, useEffect, useState } from 'https://unpkg.com/htm/preact/standalone.module.js';
import Folder from './Folder.js';

import { folder, skipForward, square } from './icons.js';
import { Server } from './util.js';

export default function NowPlaying(props) {
  const [musicData, setMusicData] = useState({ files: {} });
  const [foldersOpen, setFoldersOpen] = useState(false);

  useEffect(() => {
    fetch(`${Server}/files`)
      .then((response) => response.json())
      .then((data) => {
        const folders = Object.keys(data.files);

        // Add all files to root
        const allFiles = [];
        folders.forEach((f) => allFiles.push(...data.files[f]));
        data.files[data.musicRoot] = allFiles;

        setMusicData(data);
      });
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

      <button class="icon" onClick=${() => setFoldersOpen(true)}>${folder}</button>

      ${foldersOpen &&
      html`<${Folder} musicData=${musicData} status=${props.status} getData=${props.getData} closeFolder=${() => setFoldersOpen(false)} />`}
    </div>
  </div>`;
}
