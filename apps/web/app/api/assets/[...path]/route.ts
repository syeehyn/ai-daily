import fs from "node:fs";
import path from "node:path";
import { NextRequest } from "next/server";

const ROOT = path.resolve(process.cwd(), "../..");
const ISSUES_DIR = path.join(ROOT, "issues");

export async function GET(_req: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const params = await context.params;
  const pieces = params.path || [];

  if (pieces.length < 3 || pieces[1] !== "figures") {
    return new Response("Not found", { status: 404 });
  }

  const [date, , ...rest] = pieces;
  const filename = rest.join("/");
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date) || filename.includes("..")) {
    return new Response("Bad request", { status: 400 });
  }

  const full = path.join(ISSUES_DIR, date, "assets", "figures", filename);
  if (!fs.existsSync(full) || !fs.statSync(full).isFile()) {
    return new Response("Not found", { status: 404 });
  }

  const ext = path.extname(full).toLowerCase();
  const contentType =
    ext === ".png"
      ? "image/png"
      : ext === ".jpg" || ext === ".jpeg"
        ? "image/jpeg"
        : ext === ".webp"
          ? "image/webp"
          : ext === ".gif"
            ? "image/gif"
            : "image/svg+xml";

  return new Response(fs.readFileSync(full), {
    status: 200,
    headers: {
      "Content-Type": contentType,
      "Cache-Control": "public, max-age=3600"
    }
  });
}
