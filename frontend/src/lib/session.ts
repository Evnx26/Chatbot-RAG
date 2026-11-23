import "server-only";
import { cookies } from "next/headers";

const COOKIE_NAME = "session";
const FALLBACK_MAX_AGE_SECONDS = 60 * 60;

// Masa hidup cookie mengikuti `exp` di JWT. Hanya untuk umur cookie:
// keabsahan token tetap diputuskan backend.
function secondsUntilExpiry(token: string): number {
  try {
    const payload = JSON.parse(
      Buffer.from(token.split(".")[1], "base64url").toString("utf8"),
    );
    const remaining = Math.floor(payload.exp - Date.now() / 1000);
    return remaining > 0 ? remaining : FALLBACK_MAX_AGE_SECONDS;
  } catch {
    return FALLBACK_MAX_AGE_SECONDS;
  }
}

export async function setSession(token: string) {
  (await cookies()).set(COOKIE_NAME, token, {
    httpOnly: true,
    sameSite: "lax",
    // Aktifkan lewat env bila nanti dijalankan di balik HTTPS.
    secure: process.env.COOKIE_SECURE === "true",
    path: "/",
    maxAge: secondsUntilExpiry(token),
  });
}

export async function getSessionToken(): Promise<string | undefined> {
  return (await cookies()).get(COOKIE_NAME)?.value;
}

export async function clearSession() {
  (await cookies()).delete(COOKIE_NAME);
}
