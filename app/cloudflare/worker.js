/**
 * Cloudflare Workers Edge Webhook Ingestion & Telemetry Dispatcher
 * Developer Workflow OS - Universal Event Engine Edge Ingress
 */

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const method = request.method.toUpperCase();

    // Health check endpoint probe
    if (url.pathname === "/api/v1/health") {
      return new Response(
        JSON.stringify({ status: "healthy", service: "Cloudflare SDLC Event Worker" }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      );
    }

    // Ingestion endpoint: POST /api/v1/ingest/<category>/<provider>
    if (url.pathname.startsWith("/api/v1/ingest") && method === "POST") {
      try {
        const bodyText = await request.text();
        const payload = bodyText ? JSON.parse(bodyText) : {};

        // Extract path parameters: /api/v1/ingest/<category>/<provider>
        const pathParts = url.pathname.split("/").filter(Boolean);
        const category = pathParts.length >= 4 ? pathParts[2] : "code";
        const provider = pathParts.length >= 4 ? pathParts[3] : "generic";

        // Cryptographic HMAC-SHA256 verification if secret is configured
        if (env.WEBHOOK_HMAC_SECRET) {
          const sigHeader = request.headers.get("x-sdlc-signature") || request.headers.get("x-hub-signature-256");
          if (!sigHeader || !(await verifyHMAC(bodyText, sigHeader, env.WEBHOOK_HMAC_SECRET))) {
            return new Response(
              JSON.stringify({ error: "Invalid or missing HMAC signature" }),
              { status: 401, headers: { "Content-Type": "application/json" } }
            );
          }
        }

        // Generate canonical event metadata
        const eventId = `evt_${Date.now().toString(36)}_${Math.random().toString(36).substring(2, 7)}`;
        const timestamp = new Date().toISOString();
        const repository = payload.repository?.full_name || payload.repository?.name || payload.project?.path_with_namespace || payload.project_name || "unknown";
        const branch = payload.ref?.replace("refs/heads/", "") || payload.branch || null;
        const actorName = payload.sender?.login || payload.user_name || payload.actor || "system";
        const eventType = inferEventType(category, provider, payload);
        const scoreDelta = computeScoreDelta(eventType);
        const riskLevel = computeRiskLevel(scoreDelta);

        // D1 SQL Persistence
        if (env.DB) {
          await env.DB.prepare(
            `INSERT OR REPLACE INTO sdlc_events (
              id, timestamp, source, category, event_type, repository, branch, environment, actor_name, payload_json, score_delta, risk_level, message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
          ).bind(
            eventId,
            timestamp,
            provider,
            category,
            eventType,
            repository,
            branch,
            env.ENVIRONMENT || "production",
            actorName,
            JSON.stringify(payload),
            scoreDelta,
            riskLevel,
            `Ingested ${eventType} event from ${provider}`
          ).run();
        }

        return new Response(
          JSON.stringify({
            status: "accepted",
            event_id: eventId,
            event_type: eventType,
            provider: provider,
            category: category,
            repository: repository
          }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        );

      } catch (err) {
        return new Response(
          JSON.stringify({ error: "Webhook processing error", details: err.message }),
          { status: 500, headers: { "Content-Type": "application/json" } }
        );
      }
    }

    // Default response or dashboard asset fallback
    if (env.ASSETS) {
      return env.ASSETS.fetch(request);
    }

    return new Response(
      JSON.stringify({ service: "Developer Workflow OS Edge Worker", status: "active" }),
      { status: 200, headers: { "Content-Type": "application/json" } }
    );
  }
};

/**
 * Verify HMAC-SHA256 payload signature
 */
async function verifyHMAC(payload, signature, secret) {
  try {
    const cleanSig = signature.replace(/^sha256=/, "");
    const encoder = new TextEncoder();
    const key = await crypto.subtle.importKey(
      "raw",
      encoder.encode(secret),
      { name: "HMAC", hash: "SHA-256" },
      false,
      ["verify"]
    );

    const sigBuf = hexToBytes(cleanSig);
    return await crypto.subtle.verify(
      "HMAC",
      key,
      sigBuf,
      encoder.encode(payload)
    );
  } catch (e) {
    return false;
  }
}

function hexToBytes(hex) {
  const bytes = new Uint8Array(Math.ceil(hex.length / 2));
  for (let i = 0; i < bytes.length; i++) {
    bytes[i] = parseInt(hex.substr(i * 2, 2), 16);
  }
  return bytes;
}

function inferEventType(category, provider, payload) {
  if (category === "code" || provider === "github" || provider === "gitlab") {
    if (payload.action === "opened" || payload.object_attributes?.state === "opened") return "pr_opened";
    if (payload.action === "closed" && payload.pull_request?.merged) return "pr_merged";
    if (payload.ref || payload.commits) return "commit_pushed";
  }
  if (category === "build" || provider === "jenkins" || provider === "circleci") {
    if (payload.status === "SUCCESS" || payload.result === "SUCCESS") return "build_passed";
    if (payload.status === "FAILURE" || payload.result === "FAILURE") return "build_failed";
    return "build_started";
  }
  if (category === "ticket" || provider === "jira" || provider === "linear") {
    if (payload.issue_event_type === "issue_created" || payload.action === "create") return "issue_created";
    if (payload.issue?.fields?.status?.name?.toLowerCase().includes("block") || payload.label === "release-blocker") return "issue_blocked";
    return "issue_updated";
  }
  return "generic_signal";
}

function computeScoreDelta(eventType) {
  switch (eventType) {
    case "build_failed": return -10.0;
    case "issue_blocked": return -15.0;
    case "pr_merged": return 5.0;
    case "build_passed": return 2.0;
    default: return 0.0;
  }
}

function computeRiskLevel(scoreDelta) {
  if (scoreDelta <= -15.0) return "CRITICAL";
  if (scoreDelta < 0.0) return "HIGH";
  if (scoreDelta > 0.0) return "LOW";
  return "MEDIUM";
}
