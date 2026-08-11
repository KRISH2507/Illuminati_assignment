export default function DataPreview({ rows }) {
  if (!rows.length) {
    return <p className="muted pad">Result rows will render here as a table.</p>;
  }

  const columns = Object.keys(rows[0]).slice(0, 8);
  const preview = rows.slice(0, 12);

  return (
    <div className="table-wrap">
      <div className="table-meta">{rows.length} row(s) returned · showing up to 12</div>
      <table>
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col}>{col}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {preview.map((row, index) => (
            <tr key={index}>
              {columns.map((col) => (
                <td key={col}>{formatCell(row[col])}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function formatCell(value) {
  if (value === null || value === undefined) return "—";
  if (Array.isArray(value)) return value.join("; ");
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}
