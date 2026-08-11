/**
 * POST /api/chat — Vercel AI Gateway when AI_GATEWAY_API_KEY (or OPENAI_API_KEY) is set.
 * Returns 503 with mode:offline otherwise so the client can fall back.
 */
const SYSTEM = `You are the Site Services VC Kit assistant for a static documentation suite.

Help with: catchment rules (25 mi OR ~60 min @ 40 mph; near Staffed → Local; far+<1.2tpd→Remote; far+≥1.2→Staffed), VC pipeline (template → vc_mapper.py → Cost_Model_Load → /cost-model), browser /sandbox bridge, /sandbox/map, scenario strip, proposal export pack, delivery KPIs (FTFR≥85%, avoidable dispatch ~14%, util 75–85%, failed-visit +34–44%), kit file inventory under /assets/vc-kit/.

Hard rules:
- Never invent customer names, PII, ticket volumes, or headcount.
- Use only Reference Deal A / Reference Deal B as labeled examples.
- Cost_Model_Load is a bridge, not a priced proposal.
- Browser sandbox ≠ full python -m engine run (say the gap when relevant).
- Be concise and practical.`;

module.exports = async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    res.status(204).end();
    return;
  }
  if (req.method !== "POST") {
    res.status(405).json({ error: "Method not allowed" });
    return;
  }

  const key =
    process.env.AI_GATEWAY_API_KEY ||
    process.env.VERCEL_AI_GATEWAY_API_KEY ||
    process.env.OPENAI_API_KEY;

  if (!key) {
    res.status(503).json({
      mode: "offline",
      error: "No AI_GATEWAY_API_KEY / OPENAI_API_KEY configured",
    });
    return;
  }

  let body = req.body;
  if (typeof body === "string") {
    try {
      body = JSON.parse(body);
    } catch (_) {
      body = {};
    }
  }
  const message = (body && body.message) || "";
  const history = Array.isArray(body && body.history) ? body.history.slice(-8) : [];
  if (!String(message).trim()) {
    res.status(400).json({ error: "message required" });
    return;
  }

  const messages = [
    { role: "system", content: SYSTEM },
    ...history.map((h) => ({
      role: h.role === "assistant" ? "assistant" : "user",
      content: String(h.content || "").slice(0, 4000),
    })),
    { role: "user", content: String(message).slice(0, 4000) },
  ];

  const model = process.env.AI_GATEWAY_MODEL || "openai/gpt-4o-mini";
  const endpoints = [
    "https://ai-gateway.vercel.sh/v1/chat/completions",
    "https://api.openai.com/v1/chat/completions",
  ];

  let lastErr = "";
  for (const url of endpoints) {
    try {
      const r = await fetch(url, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${key}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: url.includes("openai.com") ? model.replace(/^openai\//, "") : model,
          messages,
          temperature: 0.3,
          max_tokens: 900,
        }),
      });
      const text = await r.text();
      if (!r.ok) {
        lastErr = `HTTP ${r.status} ${text.slice(0, 200)}`;
        continue;
      }
      let data;
      try {
        data = JSON.parse(text);
      } catch (_) {
        lastErr = "invalid JSON from provider";
        continue;
      }
      const reply =
        data.choices &&
        data.choices[0] &&
        data.choices[0].message &&
        data.choices[0].message.content;
      if (!reply) {
        lastErr = "empty completion";
        continue;
      }
      res.status(200).json({ mode: "live", text: reply, model });
      return;
    } catch (e) {
      lastErr = e.message || String(e);
    }
  }

  console.error("chat provider failed", lastErr);
  res.status(502).json({ mode: "offline", error: lastErr || "provider failed" });
};
