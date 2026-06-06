/* ============================================================================
   components/BarChart.jsx — Petit graphique en barres horizontales (CSS pur)
   ----------------------------------------------------------------------------
   Affiche une liste { label, valeur } sous forme de barres proportionnelles.
   Aucune librairie : juste des div dont la largeur dépend de la valeur max.
   ============================================================================ */

export default function BarChart({ data, couleur = "var(--accent)" }) {
  if (!data || data.length === 0) {
    return <p className="muet" style={{ fontSize: ".9rem" }}>Pas encore de données.</p>;
  }
  const max = Math.max(...data.map((d) => d.valeur));

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
      {data.map((d) => (
        <div key={d.label} style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <span style={{ width: 110, flexShrink: 0, fontSize: ".88rem", textAlign: "right" }}>
            {d.label}
          </span>
          <div style={{ flex: 1, background: "var(--accent-clair)", borderRadius: 6, overflow: "hidden", height: 22 }}>
            <div
              style={{
                width: `${max ? (d.valeur / max) * 100 : 0}%`,
                background: couleur,
                height: "100%",
                borderRadius: 6,
                transition: "width .4s ease",
                minWidth: d.valeur > 0 ? 3 : 0,
              }}
            />
          </div>
          <span className="muet" style={{ width: 28, fontSize: ".85rem" }}>{d.valeur}</span>
        </div>
      ))}
    </div>
  );
}
