/**
 * GET /api/chat-status — reports whether live kit chat is configured.
 */
module.exports = async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Cache-Control", "no-store");

  if (req.method === "OPTIONS") {
    res.status(204).end();
    return;
  }

  const hasKey = !!(
    process.env.AI_GATEWAY_API_KEY ||
    process.env.VERCEL_AI_GATEWAY_API_KEY ||
    process.env.OPENAI_API_KEY
  );

  res.status(200).json({
    mode: hasKey ? "live" : "offline",
    reason: hasKey ? "AI gateway key present" : "no AI_GATEWAY_API_KEY / OPENAI_API_KEY",
    model: process.env.AI_GATEWAY_MODEL || "openai/gpt-4o-mini",
  });
};
