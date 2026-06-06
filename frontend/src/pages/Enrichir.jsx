/* ============================================================================
   pages/Enrichir.jsx — Enrichir mon profil (un film à la fois)
   ----------------------------------------------------------------------------
   Un film en grand au centre. L'utilisateur répond « pas vu » (passe au
   suivant) ou « vu » → une étape de notation apparaît (notable ou « passer »).
   Les films viennent de TMDb (/discover) avec variété d'années (1960–2026),
   filtrables par année et nationalité. La file est préchargée pour fluidité,
   et l'enregistrement est instantané (enrichissement en tâche de fond côté API).
   ============================================================================ */

import { useEffect, useRef, useState } from "react";
import { api } from "../lib/api";
import NoteEtoiles from "../components/NoteEtoiles";

const PAYS = [
  { code: "", nom: "Tous les pays" },
  { code: "FR", nom: "France" },
  { code: "US", nom: "États-Unis" },
  { code: "GB", nom: "Royaume-Uni" },
  { code: "IT", nom: "Italie" },
  { code: "JP", nom: "Japon" },
  { code: "KR", nom: "Corée du Sud" },
  { code: "DE", nom: "Allemagne" },
  { code: "ES", nom: "Espagne" },
  { code: "IN", nom: "Inde" },
];

export default function Enrichir() {
  const [file, setFile] = useState([]);
  const [charge, setCharge] = useState(true);
  const [travail, setTravail] = useState(false);
  const [noter, setNoter] = useState(false);
  const [note, setNote] = useState(null);
  const [annee, setAnnee] = useState("");
  const [pays, setPays] = useState("");
  const pageRef = useRef(1);

  async function remplir(reset = false) {
    const params = { page: reset ? 1 : pageRef.current };
    if (annee) params.annee = annee;
    if (pays) params.pays = pays;
    const res = await api.decouvrir(params);
    pageRef.current = res.page_suivante;
    setFile((f) => (reset ? res.films : [...f, ...res.films]));
  }

  useEffect(() => {
    setCharge(true);
    pageRef.current = 1;
    setNoter(false);
    setNote(null);
    remplir(true).finally(() => setCharge(false));
  }, [annee, pays]);

  useEffect(() => {
    if (file.length > 0 && file.length <= 4) remplir(false);
  }, [file]);

  const film = file[0];

  async function enregistrer(vu, noteValeur) {
    if (!film) return;
    setTravail(true);
    try {
      await api.marquerTmdb(film.tmdb_id, vu, noteValeur, {
        titre: film.titre,
        annee: film.annee,
        affiche: film.affiche,
        note_public: film.note_public,
        resume: film.resume,
      });
      setFile((f) => f.slice(1));
      setNoter(false);
      setNote(null);
    } catch (e) {
      alert("Erreur : " + e.message);
    } finally {
      setTravail(false);
    }
  }

  const champFiltre = {
    padding: "9px 12px",
    border: "1px solid var(--bordure)",
    borderRadius: "var(--rayon-sm)",
    background: "var(--surface)",
    fontFamily: "inherit",
    fontSize: ".92rem",
  };

  return (
    <div style={{ maxWidth: 720, margin: "0 auto" }}>
      <div style={{ textAlign: "center", marginBottom: 28 }}>
        <h1 style={{ marginBottom: 6 }}>Enrichir mon profil</h1>
        <p className="muet">Vu ou pas vu ? Chaque réponse affine ton profil.</p>
      </div>

      <div style={{ display: "flex", gap: 10, justifyContent: "center", marginBottom: 34, flexWrap: "wrap" }}>
        <select style={champFiltre} value={pays} onChange={(e) => setPays(e.target.value)}>
          {PAYS.map((p) => <option key={p.code} value={p.code}>{p.nom}</option>)}
        </select>
        <input
          style={{ ...champFiltre, width: 130 }}
          type="number"
          placeholder="Année"
          value={annee}
          min="1900"
          max="2030"
          onChange={(e) => setAnnee(e.target.value)}
        />
        {(annee || pays) && (
          <button className="btn btn-fantome" onClick={() => { setAnnee(""); setPays(""); }}>
            Réinitialiser
          </button>
        )}
      </div>

      {charge ? (
        <p className="muet" style={{ textAlign: "center" }}>Chargement…</p>
      ) : !film ? (
        <p className="muet" style={{ textAlign: "center" }}>
          Plus de films à proposer avec ces filtres. Élargis-les pour continuer.
        </p>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 24 }}>
          <div
            style={{
              width: 300,
              aspectRatio: "2/3",
              borderRadius: "var(--rayon)",
              overflow: "hidden",
              background: "var(--accent-clair)",
              boxShadow: "var(--ombre)",
            }}
          >
            {film.affiche ? (
              <img src={film.affiche} alt={film.titre} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
            ) : (
              <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100%", fontFamily: "var(--font-titre)", fontSize: "3rem", color: "var(--texte-doux)" }}>?</div>
            )}
          </div>

          <div style={{ textAlign: "center", maxWidth: 480 }}>
            <h2 style={{ marginBottom: 4 }}>{film.titre}</h2>
            <p className="muet">
              {film.annee || "—"}{film.note_public ? ` · ${film.note_public.toFixed(1)}/10` : ""}
            </p>
          </div>

          {!noter ? (
            <div style={{ display: "flex", gap: 14 }}>
              <button className="btn btn-fantome" style={{ minWidth: 150, padding: "13px" }} disabled={travail} onClick={() => enregistrer(false, null)}>
                Pas vu
              </button>
              <button className="btn" style={{ minWidth: 150, padding: "13px" }} disabled={travail} onClick={() => setNoter(true)}>
                ✓ Vu
              </button>
            </div>
          ) : (
            <div style={{ textAlign: "center", display: "flex", flexDirection: "column", alignItems: "center", gap: 16 }}>
              <p style={{ fontWeight: 500 }}>Quelle note lui donnes-tu ?</p>
              <NoteEtoiles note={note} onNote={setNote} />
              <div style={{ display: "flex", gap: 12, marginTop: 4 }}>
                <button className="btn btn-fantome" disabled={travail} onClick={() => enregistrer(true, null)}>
                  Vu, sans note
                </button>
                <button className="btn" disabled={travail || note == null} onClick={() => enregistrer(true, note)}>
                  Valider la note
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
