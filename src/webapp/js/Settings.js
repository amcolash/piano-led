import { html, useEffect, useState } from 'https://unpkg.com/htm/preact/standalone.module.js';

import { eventBus } from './eventBus.js';
import { power, refreshCw, sliders } from './icons.js';
import { Server } from './util.js';

export default function Settings(props) {
  // helper function to retry status checking multiple times in quicker intervals
  const togglePower = (cb) => {
    setToggling(true);

    fetch(`${Server}/stop`).then(() => fetch(`${Server}/power`));

    // Keep track of all timeouts set
    const timeouts = [];

    // Check multiple times in a row for the new status at a quicker interval
    for (let i = 0; i < 10; i++) {
      timeouts.push(
        setTimeout(() => {
          props.getData().then((data) => {
            // If we are out of time or the status has changed
            if (i == 9 || props.status.on !== data.on) {
              setToggling(false);

              // Clear remaining timeouts
              timeouts.forEach((t) => clearTimeout(t));

              if (cb) cb();
            }
          });
        }, i * 1500)
      );
    }
  };

  const [toggling, setToggling] = useState(false);
  const palettes = props.status.palettes || [];

  const spinning = toggling
    ? {
        animationName: 'spin',
        animationDuration: '2500ms',
        animationIterationCount: 'infinite',
        animationTimingFunction: 'linear',
      }
    : { transform: 'rotate(0deg)' };

  useEffect(() => {
    eventBus.on('power', (message) => togglePower(message.complete));

    return () => eventBus.remove('power');
  }, []);

  return html`
    <div class="settings" style=${{ position: 'absolute', top: '1rem', right: '1rem', display: 'flex' }}>
      <div class="icon">
        ${sliders}
        <select
          class="icon"
          style=${{ position: 'absolute', top: 0, left: 0, color: 'rgba(0,0,0,0)' }}
          onChange=${(e) => fetch(`${Server}/palette?value=${e.target.value}`).then(() => setTimeout(props.getData, 500))}
          value=${null}
          disabled=${palettes.length === 0}
        >
          ${palettes.map((p) => html`<option value=${p}>${p}</option>`)}
        </select>
      </div>
      <button
        class="icon"
        style=${{
          marginLeft: '0.5rem',
          filter: props.status.on && !toggling ? 'drop-shadow(0 0 0.35rem var(--palette4)) brightness(1.25)' : undefined,
          cursor: toggling ? 'default' : undefined,
          ...spinning,
        }}
        onClick=${togglePower}
        disabled=${toggling}
      >
        <div style=${{ opacity: props.status.on ? 1 : 0.6 }}>${toggling ? refreshCw : power}</div>
      </button>
    </div>
  `;
}
