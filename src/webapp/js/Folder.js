import { html, useState } from 'https://unpkg.com/htm/preact/standalone.module.js';

import { Button } from './Button.js';
import Controls from './Controls.js';

import { eventBus } from './eventBus.js';
import { shuffle, volume2 } from './icons.js';
import { Server, title } from './util.js';

export default function Folder(props) {
  const musicRoot = props.musicData.musicRoot;
  const folders = Object.keys(props.musicData.files).sort((a, b) => {
    if (a === musicRoot) return -1;
    return a.localeCompare(b);
  });

  const [selectedFolder, setSelectedFolder] = useState(musicRoot);
  const [toBePlayed, setToBePlayed] = useState();

  const play = (file, folder) => {
    if (!props.status.on) {
      eventBus.dispatch('power', {
        complete: () => {
          fetch(`${Server}/play?file=${file}&folder=${folder}`).then(() => setTimeout(props.getData, 500));
        },
      });
    } else fetch(`${Server}/play?file=${file}&folder=${folder}`).then(() => setTimeout(props.getData, 500));
  };

  return html`
    <div
      class="folderList"
      style=${{
        position: 'absolute',
        padding: '1rem',
        marginTop: '3.5rem',
        background: 'var(--palette3)',
        boxShadow: '0 0 2rem rgba(0,0,0,0.3)',
        overflow: 'hidden',
        borderRadius: '0.5rem',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <div style=${{ display: 'flex', height: '100%', overflow: 'hidden' }}>
        <div style=${{ width: '30%', marginRight: '0.5rem', position: 'relative' }}>
          <div class="select" style=${{ overflow: 'hidden' }}>
            ${folders.map(
              (f) =>
                html`<${Button} class=${`option ${selectedFolder === f ? 'selected' : ''}`} onClick=${(e) => setSelectedFolder(f)}>
                  ${title(f.replace(musicRoot + '/', '').replace(musicRoot, 'All Music'))}
                </${Button}>`
            )}
          </div>
        </div>
        <div class="select" style=${{ width: '100%' }}>
          <${Button}
            class="option"
            onClick=${(e) => play(undefined, selectedFolder)}
          >
            <div class="optionIcon">${shuffle}</div>
            <div>Shuffle Folder</div>
          </${Button}>
          ${(props.musicData.files[selectedFolder] || []).map((f) => {
            const isPlaying = props.status.music && f.toLowerCase().indexOf(props.status.music.toLowerCase()) !== -1;
            return html`<${Button} class=${`option ${isPlaying || f === toBePlayed ? 'selected' : ''}`} onClick=${(e) =>
              play(f, selectedFolder)}>
              ${isPlaying && html`<div class="optionIcon">${volume2}</div>`}
              <div style=${{ marginLeft: !isPlaying ? '2.5rem' : undefined }}>
              ${f
                .replace(selectedFolder + '/', '')
                .replace('.mid', '')
                .replace('/', ' / ')}
              </div>
            </${Button}>`;
          })}
        </div>
      </div>
      ${
        props.status.music &&
        props.status.on &&
        html`<div
          style=${{
            padding: '1rem',
            width: '100%',
            background: 'var(--palette5)',
            // borderRadius: '0.5rem',
            marginLeft: '-1rem',
            marginBottom: '-1rem',
          }}
        >
          <div style=${{ fontSize: '1.35rem', color: 'var(--palette2)', marginBottom: '0.5rem' }}>${props.status.music}</div>
          <${Controls} status=${props.status} getData=${props.getData} />
        </div>`
      }
    </div>
  `;
}
