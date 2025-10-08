import React from "react";

export default function SignalCard({ data }) {
  const rows = Object.entries(data).map(([k, v]) => (
    <div key={k} style={{ display: "flex", justifyContent: "space-between", padding: "6px 0", borderBottom: "1px solid #1f2937" }}>
      <div style={{ opacity: 0.8 }}>{k}</div>
      <div style={{ fontWeight: 600 }}>{String(v)}</div>
    </div>
  ));

  return (
    <div style={{ background: "#111827", borderRadius: 12, padding: 16, maxWidth: 600 }}>
      <h2 style={{ marginTop: 0, marginBottom: 12 }}>Signal</h2>
      {rows}
    </div>
  );
}
