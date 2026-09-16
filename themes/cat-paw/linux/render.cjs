const sharp = require('sharp');
const fs = require('node:fs/promises');
const path = require('node:path');
async function main() {
  if (process.argv[2] === '--preview') {
    const name = path.join(__dirname, '../preview/Cat Paw Linux Roles');
    await sharp(name + '.svg').png().toFile(name + '.png');
    return;
  }
  const jobs = JSON.parse(await fs.readFile(process.argv[2], 'utf8'));
  for (const job of jobs) await sharp(job.source).png().toFile(job.dest);
  console.log(`Rendered ${jobs.length} native cursor frames.`);
}
main().catch(e => { console.error(e); process.exitCode = 1; });
