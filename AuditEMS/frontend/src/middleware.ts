export { auth as middleware } from "@/auth";

// Apply middleware to all routes except api, _next/static, _next/image, and favicon.ico
export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
