import 'https://cdn.skypack.dev/preact/debug';

import { html, render, useState, useEffect } from 'https://unpkg.com/htm/preact/standalone.module.js';

import Folder from './Folder.js';
import Settings from './Settings.js';

import { useInterval } from './useInterval.js';
import { Server } from './util.js';

function App() {
  const [status, setStatus] = useState({});
  const [musicData, setMusicData] = useState({ files: {} });

  const getData = () => {
    const res = fetch(`${Server}/status`).then((response) => response.json());

    res.then((data) => setStatus(data));

    return res;
  };

  useEffect(getData, []);
  useInterval(getData, 7000);

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

  return html`
    <div
      style=${{
        background: 'var(--palette1)',
        color: 'var(--palette4)',
        fontFamily: 'sans-serif',
        fontSize: '2rem',
        width: '100vw',
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexDirection: 'column',
      }}
    >
      <div style=${{ padding: '1rem', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column' }}>
        <${Settings} status=${status} getData=${getData} />
        ${!musicData.musicRoot
          ? html`<div>Loading...</div>`
          : status.on
          ? html`<${Folder} musicData=${musicData} status=${status} getData=${getData} />`
          : html`<div>Piano Off</div>`}
      </div>
    </div>
  `;
}

render(html`<${App} />`, document.body);
