// SPDX-License-Identifier: MIT
// The build-time illustration is shipped intact; execution needs only Node.
import { readFileSync, mkdirSync, writeFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const source = resolve(dirname(fileURLToPath(import.meta.url)), 'entry.png');
const image = readFileSync(source);
const signature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
if (!image.subarray(0, 8).equals(signature)) throw new Error('Expected PNG');
if (image.length > 1048576) throw new Error('Image exceeds 1 MiB');
const width = image.readUInt32BE(16);
const height = image.readUInt32BE(20);
if (width < 1 || height < 1 || width > 1024 || height > 1024) {
  throw new Error('Image dimensions are outside the contest limits');
}
// Validate the complete chunk stream, including CRCs and the terminal IEND.
function crc32(bytes: Buffer): number {
  let crc = 0xffffffff;
  for (const byte of bytes) {
    crc ^= byte;
    for (let bit = 0; bit < 8; bit++) {
      crc = (crc >>> 1) ^ ((crc & 1) ? 0xedb88320 : 0);
    }
  }
  return (crc ^ 0xffffffff) >>> 0;
}
let cursor = 8;
let ended = false;
while (cursor + 12 <= image.length) {
  const length = image.readUInt32BE(cursor);
  const end = cursor + 12 + length;
  if (end > image.length) throw new Error('Truncated PNG chunk');
  const type = image.toString('ascii', cursor + 4, cursor + 8);
  const actual = crc32(image.subarray(cursor + 4, end - 4));
  if (actual !== image.readUInt32BE(end - 4)) throw new Error('PNG checksum mismatch');
  cursor = end;
  if (type === 'IEND') {
    if (length !== 0) throw new Error('Invalid PNG end chunk');
    ended = true;
    break;
  }
}
if (!ended || cursor !== image.length) throw new Error('Incomplete PNG stream');
const output = resolve(process.env.MAKEFUN_OUTPUT_DIR || '/output');
mkdirSync(output, { recursive: true });
writeFileSync(resolve(output, 'entry.png'), image);
