import { html } from 'https://unpkg.com/htm/preact/standalone.module.js';

// Icons from feathericons.com

export const playCircle = html`<svg
  xmlns="http://www.w3.org/2000/svg"
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width="2"
  stroke-linecap="round"
  stroke-linejoin="round"
  class="feather feather-play-circle"
>
  <circle cx="12" cy="12" r="10"></circle>
  <polygon points="10 8 16 12 10 16 10 8"></polygon>
</svg>`;

export const stopCircle = html`<svg
  xmlns="http://www.w3.org/2000/svg"
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width="2"
  stroke-linecap="round"
  stroke-linejoin="round"
  class="feather feather-stop-circle"
>
  <circle cx="12" cy="12" r="10"></circle>
  <rect x="9" y="9" width="6" height="6"></rect>
</svg>`;

export const skipForward = html`<svg
  xmlns="http://www.w3.org/2000/svg"
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width="2"
  stroke-linecap="round"
  stroke-linejoin="round"
  class="feather feather-skip-forward"
>
  <polygon points="5 4 15 12 5 20 5 4"></polygon>
  <line x1="19" y1="5" x2="19" y2="19"></line>
</svg>`;
