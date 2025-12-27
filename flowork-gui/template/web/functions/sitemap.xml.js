//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\functions\sitemap.xml.js total lines 82 
//#######################################################################

export async function onRequest(context) {
    const { env, request } = context;
    const { DB } = env;
    const now = new Date().toISOString();
    const url = new URL(request.url);
    const baseUrl = `${url.protocol}//${url.host}`;

    try {
        const articleStmt = env.DB.prepare(
            `SELECT slug, language, updated_at FROM articles
             WHERE status = 'published'
             AND visibility = 'public'
             AND (publish_at IS NULL OR publish_at <= ?)`
        ).bind(now);
        const articles = await articleStmt.all();

        const marketStmt = env.DB.prepare(
            `SELECT id, type, created_at FROM marketplace`
        );
        const marketplace = await marketStmt.all();

        let apps = [];
        try {
            const appRegistryRes = await fetch(`${baseUrl}/apps-cloud/registry.json`);
            if (appRegistryRes.ok) {
                apps = await appRegistryRes.json();
            }
        } catch (e) { }

        let xml = `<?xml version="1.0" encoding="UTF-8"?>`;
        xml += `<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">`;

        xml += `<url><loc>${baseUrl}/</loc><priority>1.0</priority></url>`;
        xml += `<url><loc>${baseUrl}/login</loc><priority>0.8</priority></url>`;
        xml += `<url><loc>${baseUrl}/register</loc><priority>0.8</priority></url>`;
        xml += `<url><loc>${baseUrl}/marketplace</loc><priority>0.9</priority></url>`;
        xml += `<url><loc>${baseUrl}/apps-center</loc><priority>1.0</priority></url>`;

        if (articles.results) {
            for (const article of articles.results) {
                const lang = article.language || 'en';
                const url = `${baseUrl}/p-${article.slug}-${lang}.html`;
                const lastMod = article.updated_at ? new Date(article.updated_at).toISOString() : now;
                xml += `<url><loc>${url}</loc><lastmod>${lastMod}</lastmod><priority>0.7</priority></url>`;
            }
        }

        if (marketplace.results) {
            for (const item of marketplace.results) {
                const marketUrl = `${baseUrl}/marketplace/item/${item.id}?type=${item.type || 'preset'}`;
                const marketLastMod = item.created_at ? new Date(item.created_at).toISOString() : now;
                xml += `<url><loc>${marketUrl}</loc><lastmod>${marketLastMod}</lastmod><priority>0.8</priority></url>`;
            }
        }

        if (apps) {
            for (const app of apps) {
                const slug = app.slug || app.id;
                const url = `${baseUrl}/app/${slug}`;
                xml += `<url><loc>${url}</loc><priority>0.9</priority></url>`;
            }
        }

        xml += `</urlset>`;

        return new Response(xml, {
            headers: {
                'Content-Type': 'application/xml',
                'Cache-Control': 'public, max-age=3600'
            }
        });

    } catch (e) {
        return new Response(e.message, { status: 500 });
    }
}
