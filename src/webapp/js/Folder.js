import { html, useState } from 'https://unpkg.com/htm/preact/standalone.module.js';

import { Button } from './Button.js';
import Controls from './Controls.js';

import { eventBus } from './eventBus.js';
import { folder, shuffle, volume2 } from './icons.js';
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
        color: 'var(--palette1)',
        background: 'var(--palette3)',
        boxShadow: '0 0 2rem rgba(0,0,0,0.3)',
        overflow: 'hidden',
        borderRadius: '0.5rem',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <div class="container" style=${{ display: 'flex', height: '100%', overflow: 'hidden' }}>
        <div class="folderBar">
          <!-- Different UI is used based on if the device is mobile / desktop -->

          <!-- Mobile Folder View -->
          <div class="mobile" style=${{
            position: 'relative',
            alignItems: 'center',
            marginLeft: '0.5rem',
            marginBottom: '1.25rem',
            height: '1.75rem',
          }}>
            ${folder}
            <select
              class="icon"
              style=${{ position: 'absolute', top: 0, left: 0, color: 'rgba(0,0,0,0)', width: '100%', height: '100%' }}
              onInput=${(e) => setSelectedFolder(e.target.value)}
              value=${selectedFolder}
            >
              ${folders.map(
                (f) => html`<option value=${f}>${title(f.replace(musicRoot + '/', '').replace(musicRoot, 'All Music'))}</option>`
              )}
            </select>
            <div class="folderName" style=${{
              marginLeft: '0.25rem',
              fontSize: '1.15rem',
            }}>
              ${title(selectedFolder.replace(musicRoot + '/', '').replace(musicRoot, 'All Music'))}
            </div>
          </div>

          <!-- Desktop Folder View -->
          <div class="desktop" style=${{ height: '100%' }}>
            <div class="folderLabel" style=${{
              display: 'flex',
              justifyContent: 'flex-begin',
              height: '1.35rem',
              marginBottom: '0.75rem',
              padding: '0.5rem',
              fontSize: '1.15rem',
            }}>
              ${folder}
              <div>Folders</div>
            </div>

            <div class="select" style=${{ overflow: 'hidden' }}>
              ${folders.map(
                (f) =>
                  html`<${Button} class=${`option ${selectedFolder === f ? 'selected' : ''}`} onClick=${(e) => setSelectedFolder(f)}>
                    ${title(f.replace(musicRoot + '/', '').replace(musicRoot, 'All Music'))}
                  </${Button}>`
              )}
            </div>
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
