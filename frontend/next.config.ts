import type { NextConfig } from "next";

// NEXT_PUBLIC_* is inlined at build time. Never ship a Render build that sends
// browser requests to the visitor's localhost because configuration was absent.
if (process.env.RENDER === "true") {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;
  if (!apiUrl || !apiUrl.startsWith("https://") || !apiUrl.replace(/\/$/, "").endsWith("/api/v1")) {
    throw new Error("Set NEXT_PUBLIC_API_URL to the HTTPS backend URL ending in /api/v1 before building on Render.");
  }
}

const config: NextConfig = {};
export default config;
