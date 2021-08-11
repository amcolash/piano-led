import { html, render } from 'https://unpkg.com/htm/preact/standalone.module.js';

import NowPlaying from './NowPlaying.js';
import { Palette } from './util.js';

function App(props) {
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
      }}
    >
      <${NowPlaying} />
    </div>
  `;
}

render(html`<${App} />`, document.body);
