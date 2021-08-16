export const Palette = ['#1981a4', '#43adbb', '#8bd0cf', '#f7e5d2', '#dec8b8'];

export const Server = 'https://home.amcolash.com:9090/piano-led';

// function from https://stackoverflow.com/a/22193094/2303432
export function title(val) {
  return val
    .replace(/\s+/g, ' ')
    .split(' ')
    .map((w) => w[0].toUpperCase() + w.substr(1).toLowerCase())
    .join(' ');
}
