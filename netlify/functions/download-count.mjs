// netlify/functions/download-count.mjs
//
// NOTE: this must keep the .mjs extension, not .js -- it uses modern
// ES module syntax (import / export default), and without a
// package.json declaring "type": "module" anywhere in the project,
// a plain .js file is treated as CommonJS by default, which makes
// import/export a syntax error and the function fails to build
// entirely (confirmed: this exact bug happened once already -- the
// endpoint fell through to the site's normal 404 page since Netlify
// never successfully registered a working function at that route).
//
// Live download counter for the Data page, backed by Netlify Blobs
// (Netlify's built-in key-value store -- no external account needed,
// runs entirely within Netlify's own infrastructure).
//
// This is deliberately separate from Google Analytics: GA4 already
// tracks .csv/.xlsx downloads automatically and .dta/.bib downloads
// with a little extra code (see data.qmd), which is the right tool
// for rich analytics/reporting. This function exists only to power
// the live-updating number actually displayed on the page -- GA4
// data isn't queryable from a static site at page-load time without
// much heavier infrastructure (a Google Cloud service account, and
// even then the number wouldn't be live, just as-of-last-build).
//
// GET  /.netlify/functions/download-count           -> current counts for all tracked files
// POST /.netlify/functions/download-count {file: x}  -> increments file x, returns new count

import { getStore } from "@netlify/blobs";

// Whitelist of files this counter tracks -- prevents the endpoint
// being used to write arbitrary keys into the store.
const TRACKED_FILES = [
  "index_2025.csv",
  "index_2025.xlsx",
  "index_2025.dta",
  "missing_data_2025.xlsx",
  "lallpi.bib",
];

const CORS_HEADERS = {
  "Content-Type": "application/json",
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};

export default async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: CORS_HEADERS });
  }

  const store = getStore("download-counts");

  if (req.method === "GET") {
    const counts = {};
    for (const file of TRACKED_FILES) {
      const value = await store.get(file);
      counts[file] = value ? parseInt(value, 10) : 0;
    }
    return new Response(JSON.stringify(counts), { headers: CORS_HEADERS });
  }

  if (req.method === "POST") {
    let body;
    try {
      body = await req.json();
    } catch {
      return new Response(JSON.stringify({ error: "Invalid JSON body" }), {
        status: 400,
        headers: CORS_HEADERS,
      });
    }

    const file = body.file;
    if (!TRACKED_FILES.includes(file)) {
      return new Response(JSON.stringify({ error: "Unknown file" }), {
        status: 400,
        headers: CORS_HEADERS,
      });
    }

    const current = await store.get(file);
    const newCount = (current ? parseInt(current, 10) : 0) + 1;
    await store.set(file, String(newCount));

    return new Response(JSON.stringify({ file, count: newCount }), {
      headers: CORS_HEADERS,
    });
  }

  return new Response("Method not allowed", { status: 405, headers: CORS_HEADERS });
};
