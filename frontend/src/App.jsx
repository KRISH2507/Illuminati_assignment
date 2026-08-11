import { useEffect, useRef, useState } from "react";
import { askQuestion, fetchHealth } from "./api.js";
import AgentTrace from "./components/AgentTrace.jsx";
import DataPreview from "./components/DataPreview.jsx";

const AGENT_COLORS = {
  Orchestrator: "#f97316",
  "Query Planner": "#8b5cf6",
  "Data Analyst": "#0ea5e9",
  "Insight Writer": "#10b981",
};

const STARTER_PROMPTS = [
  "How is overall sales performance trending?",
  "Which channels are driving the most revenue?",
  "Where should we focus to improve store performance?",
];

export default function App() {
  const debugMode = new URLSearchParams(window.location.search).get("debug") === "1";

  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [online, setOnline] = useState(true);
  const [messages, setMessages] = useState([]);
  const [activeResult, setActiveResult] = useState(null);
  const chatEndRef = useRef(null);

  useEffect(() => {
    fetchHealth()
      .then(() => setOnline(true))
      .catch(() => setOnline(false));
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function handleAsk(inputQuestion) {
    const trimmed = (inputQuestion || question).trim();
    if (!trimmed || loading) return;

    setError("");
    setLoading(true);
    setQuestion("");
    setMessages((prev) => [...prev, { role: "user", content: trimmed }]);

    try {
      const result = await askQuestion(trimmed);
      setMessages((prev) => [...prev, { role: "assistant", content: result.answer }]);
      setActiveResult(result);
      setOnline(true);
    } catch (err) {
      const message = err.message || "Something went wrong.";
      setError(message);
      setMessages((prev) => [...prev, { role: "assistant", content: message, isError: true }]);
      if (message.toLowerCase().includes("backend")) setOnline(false);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">QB</div>
          <div>
            <h1>QuickBite Analytics</h1>
            <p>AI-powered business insights for your restaurant network</p>
          </div>
        </div>
        {!online && (
          <span className="offline-badge">Connection issue — check backend is running</span>
        )}
      </header>

      <main className={`layout ${debugMode ? "layout-debug" : "layout-single"}`}>
        <section className="chat-column">
          <div className="panel chat-panel">
            <div className="panel-header">
              <h2>Ask QuickBite</h2>
              <span className="muted">Get instant answers from your sales data</span>
            </div>

            <div className="chat-feed">
              {messages.length === 0 && !loading && (
                <div className="empty-state">
                  <h3>What would you like to know?</h3>
                  <p>
                    Ask about revenue, stores, channels, products, or trends —
                    in everyday language.
                  </p>
                  <div className="starter-prompts">
                    {STARTER_PROMPTS.map((prompt) => (
                      <button
                        key={prompt}
                        type="button"
                        className="starter-chip"
                        disabled={loading}
                        onClick={() => handleAsk(prompt)}
                      >
                        {prompt}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {messages.map((msg, index) => (
                <div key={index} className={`bubble ${msg.role} ${msg.isError ? "error" : ""}`}>
                  <span className="bubble-label">
                    {msg.role === "user" ? "You" : "QuickBite Insight"}
                  </span>
                  <p>{msg.content}</p>
                </div>
              ))}

              {loading && (
                <div className="bubble assistant loading-bubble">
                  <span className="bubble-label">Analyzing</span>
                  <div className="loading-row">
                    <span className="spinner" />
                    Crunching your latest sales data…
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            <form
              className="composer"
              onSubmit={(event) => {
                event.preventDefault();
                handleAsk(question);
              }}
            >
              <input
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                placeholder="Ask a business question…"
                disabled={loading}
              />
              <button type="submit" disabled={loading || !question.trim()}>
                Ask
              </button>
            </form>
            {error && <p className="form-error">{error}</p>}
          </div>
        </section>

        {debugMode && (
          <aside className="insights-column">
            <div className="panel">
              <div className="panel-header">
                <h2>Agent Trace</h2>
                <span className="muted">Debug mode — add ?debug=1 to URL</span>
              </div>
              <AgentTrace steps={activeResult?.steps || []} colors={AGENT_COLORS} />
            </div>

            <div className="panel">
              <div className="panel-header">
                <h2>SQL & Data</h2>
                <span className="muted">For evaluator / developer review</span>
              </div>
              {activeResult?.sql ? (
                <pre className="sql-block">{activeResult.sql}</pre>
              ) : (
                <p className="muted pad">Run a question to see SQL output.</p>
              )}
              <DataPreview rows={activeResult?.data || []} />
            </div>
          </aside>
        )}
      </main>
    </div>
  );
}
