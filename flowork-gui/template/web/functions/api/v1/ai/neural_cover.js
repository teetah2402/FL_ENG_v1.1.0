//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\functions\api\v1\ai\neural_cover.js total lines 115 
//#######################################################################

export async function onRequestPost(context) {
    const { request, env } = context;
    const KIE_TOKEN = env.KIE_API_KEY;

    const VIP_LIST = [
        "0xF39733B34131c13E35733E9Af1adD78a5e768929",
        "0x9f655D3e73FF7347aeabe61E475102d9914C8403",
        "0x0F1F31783A93C94f5055E2A11AA28B2368bA982d"
    ].map(a => a.toLowerCase());

    const MODEL_LIMITS = {
        'V5': { style: 1000, title: 100, prompt: 5000 },
        'V4_5PLUS': { style: 1000, title: 100, prompt: 5000 },
        'V4_5': { style: 1000, title: 100, prompt: 5000 },
        'V45ALL': { style: 1000, title: 80, prompt: 5000 },
        'V4': { style: 200, title: 80, prompt: 3000 }
    };

    try {
        const payload = await request.json();

        console.log("[COVER_BRIDGE] Payload:", JSON.stringify(payload));

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
            const statusUrl = `https://api.kie.ai/api/v1/generate/record-info?taskId=${payload.taskId}`;
            const sRes = await fetch(statusUrl, {
                headers: { "Authorization": `Bearer ${KIE_TOKEN}` }
            });
            const sData = await sRes.json();

            console.log(`[COVER_BRIDGE] Poll Result ${payload.taskId}:`, JSON.stringify(sData));

            return new Response(JSON.stringify(sData), {
                headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
            });
        }


        const selectedModel = payload.model || "V4";
        const limits = MODEL_LIMITS[selectedModel];
        if (limits) {
            const titleLen = (payload.title || "").length;
            const styleLen = (payload.style || "").length;
            const promptLen = (payload.prompt || "").length;

            if (titleLen > limits.title) throw new Error(`Title too long for ${selectedModel}. Max: ${limits.title}`);
            if (styleLen > limits.style) throw new Error(`Style too long for ${selectedModel}. Max: ${limits.style}`);
            if (promptLen > limits.prompt) throw new Error(`Lyrics/Prompt too long for ${selectedModel}. Max: ${limits.prompt}`);
        }

        const targetUrl = "https://api.kie.ai/api/v1/generate/upload-cover";
        const userTag = `Neural_Cover_${userAddress.substring(0, 6)}`;

        const backbonePayload = {
            uploadUrl: payload.uploadUrl,
            prompt: payload.prompt || "Cover",
            customMode: payload.customMode ?? true,
            instrumental: payload.instrumental ?? false,
            model: selectedModel,
            callBackUrl: "https://flowork.cloud/api/v1/ai/music-callback",
            title: payload.title || "Neural Cover",
            vocalGender: payload.vocalGender || "m",
            styleWeight: payload.styleWeight || 0.65,
            weirdnessConstraint: payload.weirdnessConstraint || 0.65,
            audioWeight: payload.audioWeight || 0.65,
            negativeTags: payload.negativeTags || "",
            author: userTag
        };

        if (payload.style) backbonePayload.style = payload.style;

        const res = await fetch(targetUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${KIE_TOKEN}`
            },
            body: JSON.stringify(backbonePayload)
        });

        const data = await res.json();

        console.log("[COVER_BRIDGE] Task Created:", JSON.stringify(data));

        if (!res.ok) {
            return new Response(JSON.stringify({
                error: `Backend Error: ${data.msg || data.error || res.statusText}`
            }), { status: res.status });
        }

        return new Response(JSON.stringify(data), {
            headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
        });

    } catch (e) {
        return new Response(JSON.stringify({ error: `Bridge Error: ${e.message}` }), { status: 500 });
    }
}
