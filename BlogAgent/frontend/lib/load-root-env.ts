/**
 * Ensure repo-root `.env` is loaded in route handlers / lib.
 * Matches Next precedence: `.env` then `.env.local` overrides.
 */
import path from "path";
import { config as loadEnv } from "dotenv";
import { fileURLToPath } from "url";

const repoRoot = path.join(
  path.dirname(fileURLToPath(import.meta.url)),
  "..",
  ".."
);

loadEnv({ path: path.join(repoRoot, ".env") });
loadEnv({ path: path.join(repoRoot, ".env.local") });

export {};
