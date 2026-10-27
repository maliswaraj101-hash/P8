import "@/lib/load-root-env";

import { getToken } from "next-auth/jwt";
import { SignJWT } from "jose";
import { NextRequest, NextResponse } from "next/server";

/**
 * Returns an HS256 JWT for `Authorization: Bearer` on FastAPI.
 * NextAuth v4 stores the session cookie as an encrypted JWE; `PyJWT` cannot verify that,
 * so we decrypt via getToken() then sign a short-lived API token with the same secret.
 */
export async function GET(req: NextRequest) {
  const secret = process.env.NEXTAUTH_SECRET;
  if (!secret) {
    return NextResponse.json(
      { error: "NEXTAUTH_SECRET is not configured" },
      { status: 500 }
    );
  }

  const session = await getToken({
    req,
    secret,
    raw: false,
  });

  if (!session || typeof session.sub !== "string" || !session.sub) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const key = new TextEncoder().encode(secret);
  const token = await new SignJWT({ sub: session.sub })
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime("24h")
    .sign(key);

  return NextResponse.json({ token });
}
