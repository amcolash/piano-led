import { html } from 'https://unpkg.com/htm/preact/standalone.module.js';

import { folder } from './icons.js';
import { Server, title } from './util.js';

// This is really not accessible, but meh - just my little project

export default function Folder(props) {
  const folders = props.status.folders;
  const musicRoot = props.status.musicRoot;

  return html`
    <button class="icon" style=${{ position: 'relative' }}>
      ${folder}
      <select
        class="icon"
        style=${{ position: 'absolute', top: 0, left: 0, opacity: 0 }}
        onChange=${(e) => fetch(`${Server}/play?folder=${e.target.value}`).then(() => setTimeout(props.getData, 500))}
        value=${null}
      >
        <option value=${musicRoot}>All Music</option>
        ${folders.map((f) => html`<option value=${f}>${title(f.replace(musicRoot + '/', ''))}</option>`)}
      </select>
    </button>
  `;
}
