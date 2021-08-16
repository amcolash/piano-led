import { html, useState } from 'https://unpkg.com/htm/preact/standalone.module.js';
import { shuffle, volume2, x } from './icons.js';

import { Button } from './Button.js';
import { Palette, Server, title } from './util.js';

export default function Folder(props) {
  const musicRoot = props.musicData.musicRoot;
  const folders = Object.keys(props.musicData.files).sort((a, b) => {
    if (a === musicRoot) return -1;
    return a.localeCompare(b);
  });

  const [selectedFolder, setSelectedFolder] = useState(musicRoot);

  return html`
    <div
      class="folderList"
      style=${{
        position: 'absolute',
        padding: '1rem',
        background: Palette[2],
        boxShadow: '0 0 2rem rgba(0,0,0,0.3)',
        overflow: 'hidden',
        borderRadius: '0.5rem',
      }}
    >
      <div style=${{ color: Palette[0] }}>Select Music</div>
      <button
        class="icon"
        style=${{ position: 'absolute', right: '0.5rem', top: '0.5rem', color: Palette[0] }}
        onClick=${props.closeFolder}
      >
        ${x}
      </button>
      <div style=${{ display: 'flex', overflow: 'hidden', height: 'calc(100% - 2.75rem)', marginTop: '1rem' }}>
        <div class="select" style=${{ width: '30%', marginRight: '0.5rem' }}>
          ${folders.map(
            (f) =>
              html`<${Button} class=${`option ${selectedFolder === f ? 'selected' : ''}`} onClick=${(e) => setSelectedFolder(f)}>
                ${title(f.replace(musicRoot + '/', '').replace(musicRoot, 'All Music'))}
              </${Button}>`
          )}
        </div>
        <div class="select" style=${{ width: '100%' }}>
          <${Button}
            class="option"
            onClick=${(e) => fetch(`${Server}/play?folder=${selectedFolder}`).then(() => setTimeout(props.getData, 500))}
          >
            <div style=${{ width: '1.5rem', height: '1.5rem', marginRight: '1rem' }}>${shuffle}</div>
            <div>Shuffle Folder</div>
          </${Button}>
          ${props.musicData.files[selectedFolder].map((f) => {
            const isPlaying = props.status.music && f.toLowerCase().indexOf(props.status.music.toLowerCase()) !== -1;
            return html`<${Button} class="option" onClick=${(e) =>
              fetch(`${Server}/play?file=${f}`).then(() => setTimeout(props.getData, 500))}>
              ${isPlaying && html`<div style=${{ width: '1.5rem', height: '1.5rem', marginRight: '1rem' }}>${volume2}</div>`}
              <div style=${{ marginLeft: !isPlaying ? '2.5rem' : undefined }}>${f.replace(selectedFolder + '/', '')}</div>
            </${Button}>`;
          })}
        </div>
      </div>
    </div>
  `;
}
