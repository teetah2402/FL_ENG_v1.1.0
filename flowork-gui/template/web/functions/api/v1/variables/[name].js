//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\functions\api\v1\variables\[name].js total lines 61 
//#######################################################################

import { ethers } from 'ethers';

async function verify(req) {
  try {
    const addr = req.headers.get('X-User-Address');
    const sig = req.headers.get('X-Signature');
    const msg = req.headers.get('X-Signed-Message');
    if (!addr || !sig || !msg) return null;
    const recovered = ethers.verifyMessage(msg, sig);
    return (recovered.toLowerCase() === addr.toLowerCase()) ? addr.toLowerCase() : null;
  } catch (e) { return null; }
}

export async function onRequest(context) {
  const { request, env, params } = context;
  const userAddr = await verify(request);
  const varName = decodeURIComponent(params.name);

  if (!userAddr) return new Response("Unauthorized", { status: 401 });

  try {
    if (request.method === "PUT") {
      const body = await request.json();
      const { value, is_enabled, is_secret, mode } = body;

      const dbValue = typeof value === 'string' ? value : JSON.stringify(value);

      await env.DB.prepare(`
        INSERT INTO variables (addr, name, value, is_enabled, is_secret, mode, ts)
        VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7)
        ON CONFLICT(addr, name) DO UPDATE SET
          value = excluded.value,
          is_enabled = excluded.is_enabled,
          is_secret = excluded.is_secret,
          mode = excluded.mode,
          ts = excluded.ts
      `).bind(
        userAddr, varName, dbValue,
        is_enabled ? 1 : 0, is_secret ? 1 : 0, mode || 'single', Date.now()
      ).run();

      return new Response(JSON.stringify({ success: true }), { status: 200 });
    }

    if (request.method === "DELETE") {
      await env.DB.prepare("DELETE FROM variables WHERE addr = ? AND name = ?")
        .bind(userAddr, varName).run();
      return new Response(JSON.stringify({ success: true }), { status: 200 });
    }

    return new Response(null, { status: 405 });
  } catch (e) {
    return new Response(JSON.stringify({ error: e.message }), { status: 500 });
  }
}
