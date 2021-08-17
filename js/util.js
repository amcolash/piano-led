export const Server = 'https://home.amcolash.com:9090/piano-led';

// function from https://stackoverflow.com/a/22193094/2303432
export function title(val) {
  return val
    .replace(/\s+/g, ' ')
    .split(' ')
    .map((w) => w[0].toUpperCase() + w.substr(1).toLowerCase())
    .join(' ');
}
