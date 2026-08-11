export default function AgentTrace({ steps, colors }) {
  if (!steps.length) {
    return <p className="muted pad">Agent steps will show here after a question runs.</p>;
  }

  return (
    <div className="trace-list">
      {steps.map((step, index) => (
        <article key={`${step.agent}-${index}`} className="trace-card">
          <div className="trace-head">
            <span
              className="trace-dot"
              style={{ background: colors[step.agent] || "#64748b" }}
            />
            <div>
              <h3>{step.agent}</h3>
              <p>{step.action}</p>
            </div>
          </div>
          <pre>{step.output}</pre>
        </article>
      ))}
    </div>
  );
}
