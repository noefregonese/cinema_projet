/* ============================================================================
   pages/Catalogue.jsx — Le catalogue de films
   ----------------------------------------------------------------------------
   Charge les films, fusionne avec le statut perso de l'utilisateur, permet
   la recherche et les actions (marquer vu, noter) directement sur les cartes.
   ============================================================================ */

import { useEffect, useState } from "react";
import { api } from "../lib/api";
import FilmCard from "../components/FilmCard";

export default function Catalogue() {
  const [films, setFilms] = useState([]);
  const [statuts, setStatuts] = useState({}); // { filmId: {vu, note, urgence} }
  const [recherche, setRecherche] = useState("");
  const [charge, setCharge] = useState(true);

  async function charger() {
    setCharge(true);
    const [listeFilms, mesFilms] = await Promise.all([
      api.films({ recherche }),
      api.mesFilms(),
    ]);
    const map = {};
    for (const item of mesFilms) map[item.film.id] = item.statut;
    setFilms(listeFilms);
    setStatuts(map);
    setCharge(false);
  }

  useEffect(() => { charger(); }, []);

  // Recherche avec petit délai (anti-rebond)
  useEffect(() => {
    const t = setTimeout(() => { charger(); }, 350);
    return () => clearTimeout(t);
  }, [recherche]);

  function statutDe(filmId) {
    return statuts[filmId] || { vu: false, note: null, urgence: 0 };
  }

  async function majStatut(filmId, modif) {
    const nouveau = await api.majStatut(filmId, modif);
    setStatuts((s) => ({ ...s, [filmId]: nouveau }));
  }

  return (
    <div>
      <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between", flexWrap: "wrap", gap: 16, marginBottom: 32 }}>
        <div>
          <h1>Catalogue</h1>
          <p className="muet">Parcours, note et coche les films que tu as vus.</p>
        </div>
        <input
          className="champ"
          style={{ maxWidth: 280 }}
          placeholder="Rechercher un titre…"
          value={recherche}
          onChange={(e) => setRecherche(e.target.value)}
        />
      </div>

      {charge ? (
        <p className="muet">Chargement…</p>
      ) : films.length === 0 ? (
        <p className="muet">Aucun film. Va dans « Importer » pour en ajouter depuis TMDb.</p>
      ) : (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(190px, 1fr))",
            gap: 22,
          }}
        >
          {films.map((film) => {
            const st = statutDe(film.id);
            return (
              <FilmCard
                key={film.id}
                film={film}
                statut={st}
                onVu={(vu) => majStatut(film.id, { vu })}
                onNote={(note) => majStatut(film.id, { note, vu: true })}
              />
            );
          })}
        </div>
      )}
    </div>
  );
}
