import { html } from 'https://unpkg.com/htm/preact/standalone.module.js';

// Icons from feathericons.com
// Make sure to remove width + height from the svg

export const play = html`<svg
  xmlns="http://www.w3.org/2000/svg"
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width="2"
  stroke-linecap="round"
  stroke-linejoin="round"
  class="feather feather-play"
>
  <polygon points="5 3 19 12 5 21 5 3"></polygon>
</svg>`;

export const square = html`<svg
  xmlns="http://www.w3.org/2000/svg"
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width="2"
  stroke-linecap="round"
  stroke-linejoin="round"
  class="feather feather-square"
>
  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
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

export const folder = html`<svg
  xmlns="http://www.w3.org/2000/svg"
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width="2"
  stroke-linecap="round"
  stroke-linejoin="round"
  class="feather feather-folder"
>
  <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
</svg>`;

export const power = html`<svg
  xmlns="http://www.w3.org/2000/svg"
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width="2"
  stroke-linecap="round"
  stroke-linejoin="round"
  class="feather feather-power"
>
  <path d="M18.36 6.64a9 9 0 1 1-12.73 0"></path>
  <line x1="12" y1="2" x2="12" y2="12"></line>
</svg>`;
