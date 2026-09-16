#!/usr/bin/env node
// Rasterize our original vector sources; this does not modify the supplied reference.
const sharp = require('sharp');
const path = require('node:path');
const fs = require('node:fs/promises');
const root = path.resolve(__dirname, '..');
async function main() {
  const preview = path.join(root, 'preview', 'Cat Paw Cursor Theme Preview');
  await sharp(preview + '.svg').png().toFile(preview + '.png');
  const audit = path.join(root, 'preview', 'Native Size State Audit');
  await sharp(audit + '.svg').png().toFile(audit + '.png');
  const detail = path.join(root, 'preview', 'Cat Paw Detail Review');
  await sharp(detail + '.svg').png().toFile(detail + '.png');
  const manifest = JSON.parse(await fs.readFile(path.join(root, 'assets/manifest.json'), 'utf8'));
  // Native-size PNGs are a review aid, not CUR/Xcursor binaries.
  for (const item of manifest.cursors) {
    const dest = path.join(root, 'preview/raster', item.color, String(item.size), item.state + '.png');
    await fs.mkdir(path.dirname(dest), { recursive: true });
    await sharp(path.join(root, item.file)).png().toFile(dest);
  }
  console.log('Rendered overview and 168 native-size transparent PNGs.');
}
main().catch(error => { console.error(error); process.exitCode = 1; });
