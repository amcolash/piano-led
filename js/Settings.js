import { html, useEffect, useState } from 'https://unpkg.com/htm/preact/standalone.module.js';
import Brightness from './Brightness.js';
import { Button } from './Button.js';

import { eventBus } from './eventBus.js';
import { alertOctagon, power, refreshCw, sliders } from './icons.js';
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
        opacity: 1,
      }
    : { transform: 'rotate(0deg)' };

  useEffect(() => {
    eventBus.on('power', (message) => togglePower(message.complete));

    return () => eventBus.remove('power');
  }, []);

  return html`
    <div
      class="settings"
      style=${{ position: 'absolute', top: '1rem', right: '1rem', left: '1rem', display: 'flex', justifyContent: 'flex-end' }}
    >
      <${Brightness} status=${props.status} setStatus=${props.setStatus} />
      <${Button}
        class="icon"
        onClick=${() => {
          if (confirm('Are you sure you want to stop server?')) {
            fetch(`${Server}/exit`).then(() => setTimeout(props.getData, 500));
          }
        }}
      >
        ${alertOctagon}
      </${Button}>
      <div class="icon" style=${{ position: 'relative', marginLeft: '0.5rem' }}>
        ${sliders}
        <select
          class="icon"
          style=${{ position: 'absolute', top: 0, left: 0, color: 'rgba(0,0,0,0)' }}
          onInput=${(e) => fetch(`${Server}/palette?value=${e.target.value}`).then(() => setTimeout(props.getData, 500))}
          value=${null}
          disabled=${palettes.length === 0}
        >
          ${palettes.map((p) => html`<option value=${p}>${p}</option>`)}
        </select>
      </div>
      <${Button}
        class="icon"
        style=${{
          marginLeft: '0.5rem',
          cursor: toggling ? 'default' : undefined,
        }}
        onClick=${() => togglePower()}
        disabled=${toggling}
      >
        <div
          style=${{
            opacity: props.status.on ? 1 : 0.5,
            filter: props.status.on && !toggling ? 'drop-shadow(0 0 0.4rem var(--palette4)) brightness(1.25)' : undefined,
            transition: 'all 0.2s',
            width: '100%',
            height: '100%',
            ...spinning,
          }}
        >
          ${toggling ? refreshCw : power}
        </div>
      </${Button}>
    </div>
  `;
}
