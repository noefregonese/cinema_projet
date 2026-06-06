/* ============================================================================
   components/FilmCard.jsx — Carte d'un film
   ----------------------------------------------------------------------------
   Affiche l'affiche, le titre, l'année. Optionnellement, des actions
   (marquer vu, noter) si `statut` et les callbacks sont fournis.
   ============================================================================ */

import NoteEtoiles from "./NoteEtoiles";

export default function FilmCard({ film, statut, onVu, onNote }) {
  return (
    <div
      style={{
        background: "var(--surface)",
        border: "1px solid var(--bordure)",
        borderRadius: "var(--rayon)",
        overflow: "hidden",
        boxShadow: "var(--ombre)",
        display: "flex",
        flexDirection: "column",
      }}
    >
      {/* Affiche */}
      <div
        style={{
          aspectRatio: "2/3",
          background: "var(--accent-clair)",
          position: "relative",
        }}
      >
        {film.affiche ? (
          <img
            src={film.affiche}
            alt={film.titre_francais || film.titre_original}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        ) : (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              height: "100%",
              color: "var(--texte-doux)",
              fontFamily: "var(--font-titre)",
              fontSize: "2rem",
            }}
          >
            ?
          </div>
        )}
        {film.note_public != null && (
          <span
            style={{
              position: "absolute",
              top: 10,
              right: 10,
              background: "rgba(26,26,24,.82)",
              color: "#fff",
              padding: "3px 9px",
              borderRadius: 999,
              fontSize: ".82rem",
              fontWeight: 600,
            }}
          >
            {film.note_public.toFixed(1)}
          </span>
        )}
      </div>

      {/* Infos */}
      <div style={{ padding: "14px 16px 16px", display: "flex", flexDirection: "column", gap: 10, flex: 1 }}>
        <div>
          <h3 style={{ fontSize: "1.05rem", lineHeight: 1.2 }}>
            {film.titre_francais || film.titre_original}
          </h3>
          <span className="muet" style={{ fontSize: ".88rem" }}>{film.annee || "—"}</span>
        </div>

        {statut && (
          <div style={{ marginTop: "auto", display: "flex", flexDirection: "column", gap: 8 }}>
            <NoteEtoiles note={statut.note} onNote={onNote} />
            <button
              className={statut.vu ? "btn btn-fantome" : "btn"}
              style={{ width: "100%", padding: "8px" }}
              onClick={() => onVu(!statut.vu)}
            >
              {statut.vu ? "✓ Vu" : "Marquer comme vu"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
