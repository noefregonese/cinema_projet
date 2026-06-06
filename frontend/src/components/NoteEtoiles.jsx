/* ============================================================================
   components/NoteEtoiles.jsx — Affiche/édite une note sur 10
   ----------------------------------------------------------------------------
   5 étoiles, chacune valant 2 points, demi-étoiles gérées au survol.
   Si `onNote` est fourni, les étoiles deviennent cliquables.
   ============================================================================ */

import { useState } from "react";

function Etoile({ remplissage }) {
  // remplissage : 0 (vide), 0.5 (moitié), 1 (pleine)
  const id = Math.random().toString(36).slice(2);
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" style={{ display: "block" }}>
      <defs>
        <linearGradient id={id}>
          <stop offset={`${remplissage * 100}%`} stopColor="var(--etoile)" />
          <stop offset={`${remplissage * 100}%`} stopColor="var(--bordure)" />
        </linearGradient>
      </defs>
      <path
        fill={`url(#${id})`}
        d="M12 2l2.9 6.3 6.9.6-5.2 4.6 1.6 6.8L12 17.3 5.8 20.9l1.6-6.8L2.2 8.9l6.9-.6z"
      />
    </svg>
  );
}

export default function NoteEtoiles({ note, onNote }) {
  const [survol, setSurvol] = useState(null);
  const valeur = survol != null ? survol : note ?? 0;

  return (
    <div style={{ display: "flex", gap: 3, alignItems: "center" }}>
      {[0, 1, 2, 3, 4].map((i) => {
        const base = i * 2;
        const remplissage = Math.max(0, Math.min(1, (valeur - base) / 2));
        return (
          <span
            key={i}
            style={{ cursor: onNote ? "pointer" : "default", position: "relative" }}
            onMouseLeave={() => setSurvol(null)}
          >
            {/* moitié gauche = base+1, moitié droite = base+2 */}
            {onNote && (
              <>
                <span
                  style={{ position: "absolute", inset: 0, width: "50%", zIndex: 2 }}
                  onMouseEnter={() => setSurvol(base + 1)}
                  onClick={() => onNote(base + 1)}
                />
                <span
                  style={{ position: "absolute", inset: 0, left: "50%", width: "50%", zIndex: 2 }}
                  onMouseEnter={() => setSurvol(base + 2)}
                  onClick={() => onNote(base + 2)}
                />
              </>
            )}
            <Etoile remplissage={remplissage} />
          </span>
        );
      })}
      {note != null && (
        <span className="muet" style={{ marginLeft: 6, fontSize: ".9rem" }}>
          {note}/10
        </span>
      )}
    </div>
  );
}
