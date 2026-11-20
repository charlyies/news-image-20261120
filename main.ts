// main.ts — entrypoint for the news-image-20261120 bounty.
//
// The graded program is deliberately small: it copies the pre-rendered
// front page (entry.png, produced at build time by compose.py) into the
// grader's output directory. Everything it does is deterministic — the
// same input bytes always produce the same output bytes — because the
// copy is a raw byte copy and no timestamps or random values are involved.
//
// Before copying, the program validates the asset so a corrupt or
// oversized image fails loudly instead of being submitted silently:
//   * the file must start with the eight PNG signature bytes
//   * the first chunk must be IHDR, from which width and height are read
//   * the image must be at most 1024 x 1024 pixels and at most 1 MiB
//   * the bytes written out must match the bytes read in, checked again
//     after the write by comparing lengths and a fresh read of the target

const fs = require("node:fs");
const path = require("node:path");

const SOURCE_NAME = "entry.png";
const MAX_BYTES = 1024 * 1024;
const MAX_WIDTH = 1024;
const MAX_HEIGHT = 1024;

// The eight bytes every PNG file starts with.
const PNG_SIGNATURE = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];

function fail(message) {
  console.error("news-image-20261120: " + message);
  process.exit(1);
}

function checkSignature(bytes) {
  if (bytes.length < 8) {
    fail("entry.png is too short to be a PNG file (" + bytes.length + " bytes)");
  }
  for (let i = 0; i < PNG_SIGNATURE.length; i++) {
    if (bytes[i] !== PNG_SIGNATURE[i]) {
      fail("entry.png does not start with the PNG signature byte " + i);
    }
  }
}

function readDimensions(bytes) {
  // A PNG is a signature followed by chunks. The first chunk must be IHDR:
  // 4 bytes of length, 4 bytes of type ("IHDR"), then 13 bytes of data
  // whose first 4 bytes are the width and next 4 bytes are the height,
  // both big-endian. Anything else means the file is not a usable PNG.
  if (bytes.length < 33) {
    fail("entry.png is too short to hold a PNG header");
  }
  const chunkType = bytes.toString("ascii", 12, 16);
  if (chunkType !== "IHDR") {
    fail("first PNG chunk is " + chunkType + ", expected IHDR");
  }
  const ihdrLength = bytes.readUInt32BE(8);
  if (ihdrLength !== 13) {
    fail("IHDR chunk length is " + ihdrLength + ", expected 13");
  }
  const width = bytes.readUInt32BE(16);
  const height = bytes.readUInt32BE(20);
  if (width === 0 || height === 0) {
    fail("PNG header reports a zero dimension");
  }
  return { width, height };
}

function main() {
  const here = __dirname;
  const sourcePath = path.join(here, SOURCE_NAME);
  const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
  const targetPath = path.join(outDir, SOURCE_NAME);

  let bytes;
  try {
    bytes = fs.readFileSync(sourcePath);
  } catch (err) {
    fail("cannot read " + sourcePath + ": " + err.message);
  }

  checkSignature(bytes);

  const dims = readDimensions(bytes);
  if (dims.width > MAX_WIDTH || dims.height > MAX_HEIGHT) {
    fail(
      "entry.png is " + dims.width + "x" + dims.height +
      ", over the 1024x1024 limit"
    );
  }
  if (bytes.length > MAX_BYTES) {
    fail("entry.png is " + bytes.length + " bytes, over the 1 MiB limit");
  }

  try {
    fs.mkdirSync(outDir, { recursive: true });
  } catch (err) {
    fail("cannot create output directory " + outDir + ": " + err.message);
  }

  try {
    fs.writeFileSync(targetPath, bytes);
  } catch (err) {
    fail("cannot write " + targetPath + ": " + err.message);
  }

  // Read the file back and confirm the copy is exact.
  const written = fs.readFileSync(targetPath);
  if (written.length !== bytes.length || !written.equals(bytes)) {
    fail("bytes written to " + targetPath + " do not match entry.png");
  }

  console.log(
    "wrote " + targetPath + " (" + dims.width + "x" + dims.height +
    ", " + bytes.length + " bytes)"
  );
}

main();
