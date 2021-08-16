import { html } from 'https://unpkg.com/htm/preact/standalone.module.js';

import { folder } from './icons.js';
import { Server, title } from './util.js';

export default function Folder(props) {
  const folders = Object.keys(props.musicData.files) || [];
  const musicRoot = props.musicData.musicRoot;

  return html`
    <div class="icon" style=${{ position: 'relative' }}>
      ${folder}
      <select
        class="icon"
        style=${{ position: 'absolute', top: 0, left: 0, color: 'rgba(0,0,0,0)' }}
        onChange=${(e) => fetch(`${Server}/play?folder=${e.target.value}`).then(() => setTimeout(props.getData, 500))}
        value=${null}
      >
        <option value=${musicRoot}>All Music</option>
        ${folders.map((f) => html`<option value=${f}>${title(f.replace(musicRoot + '/', ''))}</option>`)}
      </select>
    </div>
  `;
}
