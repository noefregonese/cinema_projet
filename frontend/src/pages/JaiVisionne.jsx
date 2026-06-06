/* ============================================================================
   pages/JaiVisionne.jsx — Ajouter un film qu'on vient de voir
   ----------------------------------------------------------------------------
   L'utilisateur cherche un film précis (TMDb), le sélectionne, met une note,
   et l'enregistre comme vu dans sa base — en un seul geste.
   ============================================================================ */

import { useState } from "react";
import { api } from "../lib/api";
import NoteEtoiles from "../components/NoteEtoiles";

export default function JaiVisionne() {
  const [q, setQ] = useState("");
  const [resultats, setResultats] = useState([]);
  const [selection, setSelection] = useState(null);
  const [note, setNote] = useState(null);
  const [charge, setCharge] = useState(false);
  const [enregistre, setEnregistre] = useState(false);
  const [erreur, setErreur] = useState("");

  async function chercher(e) {
    e.preventDefault();
    if (!q.trim()) return;
    setErreur(""); setCharge(true); setSelection(null); setEnregistre(false);
    try {
      setResultats(await api.rechercheTmdb(q));
    } catch (err) {
      setErreur(err.message);
    } finally {
      setCharge(false);
    }
  }

  async function enregistrer() {
    if (!selection) return;
    setErreur("");
    try {
      await api.marquerTmdb(selection.tmdb_id, true, note, {
        titre: selection.titre,
        annee: selection.annee,
        affiche: selection.affiche,
        note_public: selection.note_public,
      });
      setEnregistre(true);
    } catch (err) {
      setErreur(err.message);
    }
  }

  function recommencer() {
    setQ(""); setResultats([]); setSelection(null); setNote(null); setEnregistre(false);
  }

  // Écran de confirmation
  if (enregistre) {
    return (
      <div style={{ maxWidth: 480, margin: "60px auto", textAlign: "center" }}>
        <div style={{ fontSize: "2.4rem", marginBottom: 16, color: "var(--etoile)" }}>✓</div>
        <h1 style={{ marginBottom: 10 }}>Ajouté !</h1>
        <p className="muet" style={{ marginBottom: 28 }}>
          « {selection.titre} » est enregistré comme vu
          {note != null ? ` et noté ${note}/10` : ""}.
        </p>
        <button className="btn" onClick={recommencer}>Ajouter un autre film</button>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 560, margin: "0 auto" }}>
      <div style={{ textAlign: "center", marginBottom: 28 }}>
        <h1 style={{ marginBottom: 6 }}>J'ai visionné</h1>
        <p className="muet">Cherche le film que tu viens de voir et note-le.</p>
      </div>

      <form onSubmit={chercher} style={{ display: "flex", gap: 10, marginBottom: 24 }}>
        <input className="champ" placeholder="Titre du film…" value={q} onChange={(e) => setQ(e.target.value)} />
        <button className="btn" disabled={charge}>{charge ? "..." : "Chercher"}</button>
      </form>

      {erreur && <p className="erreur" style={{ marginBottom: 16 }}>{erreur}</p>}

      {/* Si un film est sélectionné : note + validation */}
      {selection ? (
        <div style={{ background: "var(--surface)", border: "1px solid var(--bordure)", borderRadius: "var(--rayon)", padding: 24, textAlign: "center" }}>
          <div style={{ width: 120, aspectRatio: "2/3", margin: "0 auto 16px", borderRadius: 8, overflow: "hidden", background: "var(--accent-clair)" }}>
            {selection.affiche && <img src={selection.affiche} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />}
          </div>
          <h2 style={{ marginBottom: 2 }}>{selection.titre}</h2>
          <p className="muet" style={{ marginBottom: 20 }}>{selection.annee || "—"}</p>

          <p style={{ marginBottom: 10, fontWeight: 500 }}>Ta note (optionnelle)</p>
          <div style={{ display: "flex", justifyContent: "center", marginBottom: 24 }}>
            <NoteEtoiles note={note} onNote={setNote} />
          </div>

          <div style={{ display: "flex", gap: 10, justifyContent: "center" }}>
            <button className="btn btn-fantome" onClick={() => setSelection(null)}>Retour</button>
            <button className="btn" onClick={enregistrer}>Enregistrer comme vu</button>
          </div>
        </div>
      ) : (
        // Sinon : liste des résultats
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {resultats.map((r) => (
            <button
              key={r.tmdb_id}
              onClick={() => { setSelection(r); setNote(null); }}
              style={{
                display: "flex", alignItems: "center", gap: 14, padding: 12, textAlign: "left",
                background: "var(--surface)", border: "1px solid var(--bordure)",
                borderRadius: "var(--rayon-sm)", cursor: "pointer",
              }}
            >
              <div style={{ width: 44, height: 66, flexShrink: 0, background: "var(--accent-clair)", borderRadius: 6, overflow: "hidden" }}>
                {r.affiche && <img src={r.affiche} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />}
              </div>
              <div>
                <div style={{ fontWeight: 600 }}>{r.titre}</div>
                <div className="muet" style={{ fontSize: ".88rem" }}>{r.annee || "—"}</div>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
