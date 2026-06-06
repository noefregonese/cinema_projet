/* ============================================================================
   pages/Import.jsx — Importer des films depuis TMDb
   ----------------------------------------------------------------------------
   Cherche sur TMDb, affiche les résultats, et permet d'importer un film
   dans le catalogue en un clic.
   ============================================================================ */

import { useState } from "react";
import { api } from "../lib/api";

export default function Import() {
  const [q, setQ] = useState("");
  const [resultats, setResultats] = useState([]);
  const [charge, setCharge] = useState(false);
  const [importes, setImportes] = useState({}); // tmdbId -> "encours" | "ok" | "erreur"
  const [erreur, setErreur] = useState("");

  async function chercher(e) {
    e.preventDefault();
    if (!q.trim()) return;
    setErreur("");
    setCharge(true);
    try {
      setResultats(await api.rechercheTmdb(q));
    } catch (err) {
      setErreur(err.message);
    } finally {
      setCharge(false);
    }
  }

  async function importer(tmdbId) {
    setImportes((s) => ({ ...s, [tmdbId]: "encours" }));
    try {
      await api.importerFilm(tmdbId);
      setImportes((s) => ({ ...s, [tmdbId]: "ok" }));
    } catch {
      setImportes((s) => ({ ...s, [tmdbId]: "erreur" }));
    }
  }

  return (
    <div>
      <h1 style={{ marginBottom: 6 }}>Importer</h1>
      <p className="muet" style={{ marginBottom: 24 }}>
        Cherche un film sur TMDb et ajoute-le à ton catalogue.
      </p>

      <form onSubmit={chercher} style={{ display: "flex", gap: 10, marginBottom: 28, maxWidth: 480 }}>
        <input
          className="champ"
          placeholder="Titre du film…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <button className="btn" disabled={charge}>
          {charge ? "..." : "Chercher"}
        </button>
      </form>

      {erreur && <p className="erreur" style={{ marginBottom: 20 }}>{erreur}</p>}

      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {resultats.map((r) => {
          const etat = importes[r.tmdb_id];
          return (
            <div
              key={r.tmdb_id}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 16,
                padding: 12,
                background: "var(--surface)",
                border: "1px solid var(--bordure)",
                borderRadius: "var(--rayon-sm)",
              }}
            >
              <div style={{ width: 46, height: 69, flexShrink: 0, background: "var(--accent-clair)", borderRadius: 6, overflow: "hidden" }}>
                {r.affiche && <img src={r.affiche} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600 }}>{r.titre}</div>
                <div className="muet" style={{ fontSize: ".88rem" }}>
                  {r.annee || "—"}{r.note_public ? ` · ${r.note_public.toFixed(1)}` : ""}
                </div>
              </div>
              <button
                className={etat === "ok" ? "btn btn-fantome" : "btn"}
                disabled={etat === "encours" || etat === "ok"}
                onClick={() => importer(r.tmdb_id)}
              >
                {etat === "encours" ? "Import…" : etat === "ok" ? "✓ Importé" : etat === "erreur" ? "Réessayer" : "Importer"}
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
