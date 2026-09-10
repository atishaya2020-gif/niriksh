import fs from 'fs';
import path from 'path';
import { PNG } from 'pngjs';

const inputPath = 'C:\\Users\\rohil\\.gemini\\antigravity\\brain\\fabbd8f9-db01-43bf-b743-a5cee22e4a38\\media__1789030883233.png';
const outputDir = path.resolve('src/assets');
const outputPath = path.join(outputDir, 'niriksh-logo.png');

if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

fs.createReadStream(inputPath)
  .pipe(new PNG({ filterType: 4 }))
  .on('parsed', function() {
    for (let y = 0; y < this.height; y++) {
      for (let x = 0; x < this.width; x++) {
        const idx = (this.width * y + x) << 2;
        const r = this.data[idx];
        const g = this.data[idx + 1];
        const b = this.data[idx + 2];

        // Check if pixel is white / near white
        if (r > 220 && g > 220 && b > 220) {
          this.data[idx + 3] = 0; // set alpha to 0
        } else if (r > 200 && g > 200 && b > 200) {
          // Fade alpha for antialiased white edges
          const avg = (r + g + b) / 3;
          const alpha = Math.max(0, Math.floor((255 - avg) * 4.5));
          this.data[idx + 3] = Math.min(this.data[idx + 3], alpha);
        }
      }
    }

    this.pack().pipe(fs.createWriteStream(outputPath)).on('finish', () => {
      console.log('NIRIKSH logo processed successfully and saved to:', outputPath);
    });
  })
  .on('error', (err) => {
    console.error('Error processing logo:', err);
  });
