const API_BASE = import.meta.env.VITE_API_URL || "";

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
    throw new Error(
      "Cannot reach backend at port 8000. Start it first: python scripts/start.py"
    );
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
