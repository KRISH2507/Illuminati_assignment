const API_BASE = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
      ...options,
    });
  } catch {
    const hint = API_BASE
      ? `Cannot reach backend at ${API_BASE}`
      : "Cannot reach backend at http://127.0.0.1:8000. Start it: python scripts/start.py";
    throw new Error(hint);
  }

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = payload.detail;
    const message = Array.isArray(detail)
      ? detail.map((d) => d.msg || JSON.stringify(d)).join("; ")
      : detail || payload.message || `Request failed (${response.status})`;
    throw new Error(message);
  }
  return payload;
}

export function fetchHealth() {
  return request("/health");
}

export function fetchExamples() {
  return request("/examples");
}

export function askQuestion(question) {
  return request("/ask", {
    method: "POST",
    body: JSON.stringify({ question }),
  });
}
