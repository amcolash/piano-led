import { html, useEffect, useState } from 'https://unpkg.com/htm/preact/standalone.module.js';

import { Button } from './Button.js';
import Controls from './Controls.js';

import { eventBus } from './eventBus.js';
import { chevronDown, chevronUp, folder, shuffle, volume2 } from './icons.js';
import { lev, Server, title } from './util.js';

export default function Folder(props) {
  const musicRoot = props.musicData.musicRoot;
  const folders = Object.keys(props.musicData.files).sort((a, b) => {
    if (a === musicRoot) return -1;
    return a.localeCompare(b);
  });

  const [selectedFolder, setSelectedFolder] = useState(musicRoot);
  const [search, setSearch] = useState('');
  const [playerShown, setPlayerShown] = useState(false);

  const play = (file, folder) => {
    if (!props.status.on) {
      eventBus.dispatch('power', {
        complete: () => {
          fetch(`${Server}/play?${file && `file=${file}`}&folder=${folder}`)
            .then((response) => response.json())
            .then((status) => props.setStatus({ ...props.status, music: status.music }));
        },
      });
    } else
      fetch(`${Server}/play?${file && `file=${file}`}&folder=${folder}`)
        .then((response) => response.json())
        .then((status) => props.setStatus({ ...props.status, music: status.music }));
  };

  const focusNowPlaying = () => {
    const options = Array.from(document.querySelectorAll('.files .option'));
    options.forEach((o) => {
      const f = o.innerText.replace('/ ', '/').replace(' /', '/');
      const file = f.substring(f.lastIndexOf('/') + 1, f.length);

      if (search.length === 0 && file.trim().toLowerCase() === (props.status.music || '').trim().toLowerCase()) {
        o.scrollIntoView({ block: 'center' });
        document.querySelector('.container').scrollTop = 0;
      }
    });
  };

  const folderName = (f) => {
    return title(f.replace(musicRoot + '/', '').replace(musicRoot, 'All Music'));
  };

  const fileName = (f) => {
    return f
      .replace(selectedFolder + '/', '')
      .replace('.mid', '')
      .replace('/', ' / ');
  };

  useEffect(focusNowPlaying, [props.status.music, selectedFolder, search]);
  useEffect(() => {
    const selectedFolder = sessionStorage.getItem('piano-led-selectedFolder');
    setSelectedFolder(selectedFolder || musicRoot);
  }, []);

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
          <div class="mobile folderLabel" style=${{
            position: 'relative',
            alignItems: 'center',
            marginBottom: '0.25rem',
            height: '1.75rem',
            padding: '0.5rem',
            borderRadius: '0.25rem',
          }}>
            ${folder}
            <select
              class="icon"
              style=${{ position: 'absolute', top: 0, left: 0, color: 'rgba(0,0,0,0)', width: '100%', height: '100%' }}
              onInput=${(e) => {
                setSelectedFolder(e.target.value);
                sessionStorage.setItem('piano-led-selectedFolder', e.target.value);
              }}
              value=${selectedFolder}
            >
              ${folders.map((f) => html`<option value=${f}>${folderName(f)}</option>`)}
            </select>
            <div class="folderName" style=${{
              marginLeft: '0.25rem',
              fontSize: '1.15rem',
            }}>
              ${folderName(selectedFolder)}
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
                  html`<${Button} class=${`option ${selectedFolder === f ? 'selected' : ''}`} onClick=${(e) => {
                    setSelectedFolder(f);
                    sessionStorage.setItem('piano-led-selectedFolder', f);
                  }}>
                    ${folderName(f)}
                  </${Button}>`
              )}
            </div>
          </div>
        </div>

        <div class="files" style=${{
          width: '100%',
          height: 'calc(100% - 0.5rem)',
          paddingBottom: '0.5rem',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          overflowX: 'hidden',
          overflowY: 'hidden',
        }}>
          <div class="searchWrap" style=${{ display: 'flex', width: '100%' }}>
          <input class="search" type="search" placeholder="Search" value=${search} onInput=${(e) => setSearch(e.target.value)}
            style=${{ width: '100%', marginBottom: '1rem' }}
          />
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
              const fLower = fileName(f.toLowerCase());
              const sLower = fileName(search.toLowerCase());

              if (search.length > 0 && !(lev(fLower, sLower) < 5 || fLower.indexOf(sLower) !== -1)) return null;

              const isPlaying = props.status.music && f.toLowerCase().indexOf(props.status.music.toLowerCase()) !== -1;
              return html`<${Button} class=${`option ${isPlaying ? 'selected' : ''}`} onClick=${(e) => play(f, selectedFolder)}>
                ${isPlaying && html`<div class="optionIcon">${volume2}</div>`}
                <div style=${{ marginLeft: !isPlaying ? '2.5rem' : undefined }}>
                  ${fileName(f)}
                </div>
              </${Button}>`;
            })}
          </div>
        </div>
      </div>
      ${
        props.status.music &&
        props.status.on &&
        html`<div
          class="player ${playerShown ? '' : 'hidden'}"
          style=${{
            padding: '1rem',
            width: '100%',
            background: 'var(--palette5)',
            color: 'var(--palette2)',
            // borderRadius: '0.5rem',
            marginLeft: '-1rem',
            marginBottom: '-1rem',
          }}
        >
          <div class="nowPlaying" style=${{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <${Button}
              class="focusNowPlaying"
              style=${{ fontSize: '1.35rem', textAlign: 'left' }}
              onClick=${focusNowPlaying}
            >
              ${props.status.music}
            </${Button}>
            <${Button}
              class="toggle"
              style=${{ height: '2.5rem', marginLeft: '1rem' }}
              onClick=${() => setPlayerShown(!playerShown)}
            >
              ${playerShown ? html`${chevronDown}` : html`${chevronUp}`}
            </${Button}>
          </div>
          <${Controls} status=${props.status} getData=${props.getData} setStatus=${props.setStatus} />
        </div>`
      }
    </div>
  `;
}
