//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\functions\api\v1\ai\music.js total lines 111 
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
            return new Response(JSON.stringify(sData), {
                headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
            });
        }

        const isVideo = payload.type === 'video';

        if (!isVideo) {
            const selectedModel = payload.model || "V5";
            const limits = MODEL_LIMITS[selectedModel] || MODEL_LIMITS['V5'];

            const pLen = (payload.prompt || "").length;
            const tLen = (payload.title || "").length;
            const sLen = (payload.style || "").length;

            if (pLen > limits.prompt) throw new Error(`Prompt too long for ${selectedModel} (Max: ${limits.prompt})`);
            if (tLen > limits.title) throw new Error(`Title too long for ${selectedModel} (Max: ${limits.title})`);
            if (sLen > limits.style) throw new Error(`Style too long for ${selectedModel} (Max: ${limits.style})`);
        }

        const targetUrl = isVideo ? "https://api.kie.ai/api/v1/mp4/generate" : "https://api.kie.ai/api/v1/generate";

        const backbonePayload = isVideo ? {
            taskId: payload.taskId,
            audioId: payload.audioId,
            callBackUrl: "https://flowork.cloud/api/v1/ai/music-callback",
            author: "Neural Producer",
            domainName: "flowork.cloud"
        } : {
            prompt: payload.prompt,
            customMode: payload.customMode || false,
            instrumental: payload.instrumental || false,
            model: payload.model || "V5",
            style: payload.style || "Classical",
            title: payload.title || "Neural Sequence",
            negativeTags: payload.negativeTags || "",
            vocalGender: payload.vocalGender || "m", // [ADDED] Male/Female selection
            styleWeight: payload.styleWeight || 0.65,
            weirdnessConstraint: payload.weirdnessConstraint || 0.65,
            audioWeight: payload.audioWeight || 0.65,
            callBackUrl: "https://flowork.cloud/api/v1/ai/music-callback"
        };

        const res = await fetch(targetUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${KIE_TOKEN}`
            },
            body: JSON.stringify(backbonePayload)
        });

        const data = await res.json();

        if (!res.ok) {
            return new Response(JSON.stringify({
                error: `Backend Error: ${data.msg || data.error || res.statusText}`
            }), { status: res.status });
        }

        return new Response(JSON.stringify(data), {
            headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
        });

    } catch (e) {
        return new Response(JSON.stringify({ error: `Fatal Bridge Error: ${e.message}` }), { status: 500 });
    }
}
