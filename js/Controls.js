import { html } from 'https://unpkg.com/htm/preact/standalone.module.js';

import Progress from './Progress.js';
import Volume from './Volume.js';

export default function Controls(props) {
  return html`<div class="allControls">
    <${Progress} status=${props.status} />
    <${Volume} status=${props.status} getData=${props.getData} />
  </div>`;
}
