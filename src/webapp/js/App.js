import 'https://cdn.skypack.dev/preact/debug';

import { html, render, useState, useEffect } from 'https://unpkg.com/htm/preact/standalone.module.js';

import NowPlaying from './NowPlaying.js';
import Volume from './Volume.js';

import { power } from './icons.js';
import { useInterval } from './useInterval.js';
import { Palette, Server } from './util.js';

function App() {
  const [status, setStatus] = useState({});

  const getData = () => {
    fetch(`${Server}/status`)
      .then((response) => response.json())
      .then((data) => setStatus(data));
  };

  useEffect(getData, []);
  useInterval(getData, 7000);

  return html`
    <div
      style=${{
        background: Palette[0],
        color: Palette[3],
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
        ${status.on
          ? html`<${NowPlaying} status=${status} getData=${getData} /><${Volume} status=${status} getData=${getData} />`
          : html`<div>Piano Off</div>
              <div class="icon" style=${{ marginTop: '1rem' }}>${power}</div>`}
      </div>
    </div>
  `;
}

render(html`<${App} />`, document.body);
