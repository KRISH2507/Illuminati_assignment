export default function ExampleQuestions({ examples, onSelect, disabled }) {
  if (!examples.length) return null;

  return (
    <div className="examples-wrap">
      <span className="examples-label">Sample questions</span>
      <div className="examples-grid">
        {examples.map((item) => (
          <button
            key={item.id}
            type="button"
            className="example-chip"
            disabled={disabled}
            onClick={() => onSelect(item.question)}
            title={item.description}
          >
            <strong>{item.id.toUpperCase()}</strong>
            <span>{item.question}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
