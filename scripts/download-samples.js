import fs from 'fs';
import path from 'path';
import https from 'https';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const notes = [
  'A0', 'C1', 'D#1', 'F#1', 'A1', 'C2', 'D#2', 'F#2', 'A2', 'C3', 'D#3', 'F#3', 'A3',
  'C4', 'D#4', 'F#4', 'A4', 'C5', 'D#5', 'F#5', 'A5', 'C6', 'D#6', 'F#6', 'A6',
  'C7', 'D#7', 'F#7', 'A7', 'C8'
];

const destDir = path.join(__dirname, '..', 'public', 'audio', 'piano');
if (!fs.existsSync(destDir)) {
  fs.mkdirSync(destDir, { recursive: true });
}

function getSafeFilename(note) {
  return note.replace('#', 's') + '.mp3';
}

function getUrlFilename(note) {
  return note.replace('#', 's') + '.mp3';
}

const baseUrl = 'https://tonejs.github.io/audio/salamander/';

async function downloadFile(url, dest) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(dest);
    https.get(url, (response) => {
      if (response.statusCode !== 200) {
        reject(new Error(`Failed to get '${url}' (${response.statusCode})`));
        return;
      }
      response.pipe(file);
      file.on('finish', () => {
        file.close();
        resolve();
      });
    }).on('error', (err) => {
      fs.unlink(dest, () => {});
      reject(err);
    });
  });
}

async function main() {
  console.log('Downloading piano samples to:', destDir);
  for (const note of notes) {
    const filename = getSafeFilename(note);
    const urlFilename = getUrlFilename(note);
    const url = `${baseUrl}${urlFilename}`;
    const dest = path.join(destDir, filename);

    if (fs.existsSync(dest)) {
      console.log(`[Skip] ${note} already exists.`);
      continue;
    }

    try {
      console.log(`[Downloading] ${note}...`);
      await downloadFile(url, dest);
    } catch (error) {
      console.error(`[Error] Failed to download ${note}:`, error.message);
    }
  }
  console.log('All downloads completed!');
}

main();
