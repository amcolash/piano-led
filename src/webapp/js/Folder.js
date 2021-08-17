import { html, useState } from 'https://unpkg.com/htm/preact/standalone.module.js';
import { shuffle, volume2, x } from './icons.js';

import { Button } from './Button.js';
import { Server, title } from './util.js';
import Controls from './Controls.js';

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
        background: 'var(--palette3)',
        boxShadow: '0 0 2rem rgba(0,0,0,0.3)',
        overflow: 'hidden',
        borderRadius: '0.5rem',
      }}
    >
      <div style=${{ color: 'var(--palette1)' }}>Select Music</div>
      <button
        class="icon"
        style=${{ position: 'absolute', right: '0.5rem', top: '0.5rem', color: 'var(--palette1)' }}
        onClick=${props.closeFolder}
      >
        ${x}
      </button>
      <div style=${{ display: 'flex', height: 'calc(100% - 2.25rem)', marginTop: '1rem' }}>
        <div style=${{ width: '30%', marginRight: '0.5rem', position: 'relative' }}>
          <div class="select" style=${{ overflow: 'hidden' }}>
            ${folders.map(
              (f) =>
                html`<${Button} class=${`option ${selectedFolder === f ? 'selected' : ''}`} onClick=${(e) => setSelectedFolder(f)}>
                  ${title(f.replace(musicRoot + '/', '').replace(musicRoot, 'All Music'))}
                </${Button}>`
            )}
          </div>

          ${
            props.status.music &&
            html`<div
              style=${{
                position: 'absolute',
                left: '-1rem',
                bottom: '-0.5rem',
                padding: '1rem 0rem 1rem 1rem',
                width: '100%',
                background: 'var(--palette2)',
                borderTopRightRadius: '0.5rem',
              }}
            >
              <div style=${{ fontSize: '1.35rem', color: 'var(--palette1)', marginBottom: '0.5rem' }}>${props.status.music}</div>
              <${Controls} status=${props.status} getData=${props.getData} />
            </div>`
          }

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
            return html`<${Button} class=${`option ${isPlaying ? 'selected' : ''}`} onClick=${(e) =>
              fetch(`${Server}/play?file=${f}`).then(() => setTimeout(props.getData, 500))}>
              ${isPlaying && html`<div style=${{ width: '1.5rem', height: '1.5rem', marginRight: '1rem' }}>${volume2}</div>`}
              <div style=${{ marginLeft: !isPlaying ? '2.5rem' : undefined }}>${f
              .replace(selectedFolder + '/', '')
              .replace('.mid', '')
              .replace('/', ' / ')}</div>
            </${Button}>`;
          })}
        </div>
      </div>
    </div>
  `;
}
