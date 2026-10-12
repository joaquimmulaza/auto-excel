import { NextRequest, NextResponse } from "next/server";
import { appendFileSync, mkdirSync } from "fs";

const LOG_PATH = "/opt/cursor/logs/debug.log";

export async function POST(req: NextRequest) {
  // #region agent log
  try {
    const body = await req.json();
    mkdirSync("/opt/cursor/logs", { recursive: true });
    appendFileSync(
      LOG_PATH,
      JSON.stringify({
        hypothesisId: body.hypothesisId ?? "F",
        location: body.location ?? "frontend:agent-debug",
        message: body.message ?? "client event",
        data: body.data ?? {},
        timestamp: Date.now(),
      }) + "\n"
    );
  } catch {
    // ignore debug failures
  }
  // #endregion
  return NextResponse.json({ ok: true });
}
