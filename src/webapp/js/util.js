export const Palette = ['#1981a4', '#43adbb', '#8bd0cf', '#f7e5d2', '#dec8b8'];

export const Server = 'http://192.168.1.116:8080';

// function from https://stackoverflow.com/a/22193094/2303432
export function title(val) {
  return val
    .split(' ')
    .map((w) => w[0].toUpperCase() + w.substr(1).toLowerCase())
    .join(' ');
}
