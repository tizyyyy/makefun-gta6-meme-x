// Entry program for the gta6-meme-x-01 competition.
//
// Job: copy POST.json from the bot directory to the output directory,
// byte for byte, and stay silent on success.  The file itself carries
// the X post URL that the judges will look at, so this program must
// never reformat, trim or otherwise touch its contents.
//
// Only Node's standard library is used.  No network, no clock, no
// randomness, and nothing is read from outside the two directories
// named by the environment: the same input always produces the same
// output.

import { mkdir, readFile, stat, writeFile } from "node:fs/promises";
import { join } from "node:path";
import process from "node:process";

const FILE_NAME = "POST.json";

/** Read a required directory path from the environment. */
function requireDir(name: string): string {
  const value = process.env[name];
  if (value === undefined || value.trim() === "") {
    throw new Error(`environment variable ${name} is missing or empty`);
  }
  return value;
}

/** Load the source POST.json, refusing anything that is not a file. */
async function loadSource(botDir: string): Promise<Buffer> {
  const source = join(botDir, FILE_NAME);
  const info = await stat(source).catch(() => null);
  if (info === null) {
    throw new Error(`cannot read ${source}: file is missing or unreadable`);
  }
  if (!info.isFile()) {
    throw new Error(`cannot read ${source}: not a regular file`);
  }
  return readFile(source);
}

/** Write the bytes into the output directory, creating it if needed. */
async function storeCopy(outDir: string, bytes: Buffer): Promise<void> {
  await mkdir(outDir, { recursive: true });
  const target = join(outDir, FILE_NAME);
  await writeFile(target, bytes);
  // Guard against a short or altered write: the copy on disk must hold
  // exactly as many bytes as the source we read.
  const written = await stat(target);
  if (written.size !== bytes.length) {
    throw new Error(
      `write to ${target} was incomplete: ${written.size} of ${bytes.length} bytes`,
    );
  }
}

async function run(): Promise<void> {
  const botDir = requireDir("MAKEFUN_BOT_DIR");
  const outDir = requireDir("MAKEFUN_OUTPUT_DIR");
  const bytes = await loadSource(botDir);
  await storeCopy(outDir, bytes);
}

run().catch((err: unknown) => {
  const message = err instanceof Error ? err.message : String(err);
  console.error(`main: ${message}`);
  process.exit(1);
});
