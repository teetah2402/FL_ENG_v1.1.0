//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\functions\api\v1\ai\sora_video.js total lines 82 
//#######################################################################

export async function onRequestPost(context) {
    const { request, env } = context;
    const KIE_TOKEN = env.KIE_API_KEY;

    const VIP_LIST = [
        "0xF39733B34131c13E35733E9Af1adD78a5e768929",
        "0x9f655D3e73FF7347aeabe61E475102d9914C8403",
        "0x0F1F31783A93C94f5055E2A11AA28B2368bA982d"
    ].map(a => a.toLowerCase());

    try {
        const payload = await request.json();

        console.log("[MOTION_BRIDGE] Payload Received");

        const headerAddress = request.headers.get('X-User-Address') || "";
        const bodyAddress = payload.user_address || "";
        const userAddress = (headerAddress || bodyAddress).toLowerCase();

        if (!userAddress || !VIP_LIST.includes(userAddress)) {
            return new Response(JSON.stringify({ error: "Access Denied: Premium Subscription Required" }), {
                status: 403,
                headers: { "Content-Type": "application/json" }
            });
        }

        if (payload.action === 'check_status' && payload.taskId) {
            const statusUrl = `https://api.kie.ai/api/v1/jobs/recordInfo?taskId=${payload.taskId}`;
            const sRes = await fetch(statusUrl, {
                headers: { "Authorization": `Bearer ${KIE_TOKEN}` }
            });
            const sData = await sRes.json();
            return new Response(JSON.stringify(sData), {
                headers: { "Content-Type": "application/json" }
            });
        }

        const targetUrl = "https://api.kie.ai/api/v1/jobs/createTask";

        const apiPayload = {
            model: "sora-2-pro-text-to-video",
            input: {
                prompt: payload.prompt || "Cinematic shot",
                aspect_ratio: payload.aspect_ratio || "landscape",
                n_frames: payload.n_frames || "10",
                size: payload.size || "high",
                remove_watermark: true
            }
        };

        const res = await fetch(targetUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${KIE_TOKEN}`
            },
            body: JSON.stringify(apiPayload)
        });

        const data = await res.json();

        if (data.code !== 200) {
            return new Response(JSON.stringify({
                error: `Engine Error: ${data.msg || "Generation Failed"}`,
                details: data
            }), { status: 400 });
        }

        return new Response(JSON.stringify(data), {
            headers: { "Content-Type": "application/json" }
        });

    } catch (e) {
        return new Response(JSON.stringify({ error: `System Error: ${e.message}` }), { status: 500 });
    }
}
