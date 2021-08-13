import { html } from 'https://unpkg.com/htm/preact/standalone.module.js';

import { sliders } from './icons.js';
import { Server, title } from './util.js';

export default function Settings(props) {
  const folders = props.status.folders;
  const musicRoot = props.status.musicRoot;

  return html`
    <div class="icon" style=${{ position: 'absolute', top: '1rem', right: '1rem' }}>
      ${sliders}
      <select
        class="icon"
        style=${{ position: 'absolute', top: 0, left: 0 }}
        onChange=${(e) => fetch(`${Server}/play?folder=${e.target.value}`).then(() => setTimeout(props.getData, 500))}
        value=${null}
      >
        <option value=${musicRoot}>All Music</option>
        ${folders.map((f) => html`<option value=${f}>${title(f.replace(musicRoot + '/', ''))}</option>`)}
      </select>
    </div>
  `;
}
