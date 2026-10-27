import "./load-root-env";

import type { NextAuthOptions } from "next-auth";
import GoogleProvider from "next-auth/providers/google";

const googleId = process.env.GOOGLE_CLIENT_ID?.trim() ?? "";
const googleSecret = process.env.GOOGLE_CLIENT_SECRET?.trim() ?? "";

export const authOptions: NextAuthOptions = {
  providers: [
    GoogleProvider({
      clientId: googleId,
      clientSecret: googleSecret,
    }),
  ],
  session: { strategy: "jwt" },
  callbacks: {
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.sub ?? "";
      }
      return session;
    },
  },
  secret: process.env.NEXTAUTH_SECRET,
};
