import { html, render, useCallback, useEffect, useState } from 'https://unpkg.com/htm/preact/standalone.module.js';

import Folder from './Folder.js';
import Settings from './Settings.js';

import { useInterval } from './useInterval.js';
import { equal, Server } from './util.js';

function App() {
  const [status, setStatus] = useState({ on: false });
  const [musicData, setMusicData] = useState({ files: {} });

  const getData = useCallback(() => {
    const res = fetch(`${Server}/status`).then((response) => response.json());
    res.then((data) => {
      if (!equal(status, data)) setStatus(data);
    });

    return res;
  }, [Server, setStatus, status]);

  const getMusicData = useCallback(() => {
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
  }, [Server, setMusicData]);

  // Fetch inital data
  useEffect(getData, []);
  useEffect(getMusicData, []);

  // Schedule data updates every 7 seconds
  useInterval(getData, 7000);

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
        ${!musicData.musicRoot || !status.palettes
          ? html`<div>Loading...</div>`
          : html`<${Folder} musicData=${musicData} status=${status} getData=${getData} />`}
      </div>
    </div>
  `;
}

render(html`<${App} />`, document.body);
