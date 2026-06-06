/* ============================================================================
   pages/MesFilms.jsx — La liste personnelle de l'utilisateur
   ----------------------------------------------------------------------------
   Affiche les films que l'utilisateur a notés ou marqués, avec un filtre
   « tous / vus / à voir ».
   ============================================================================ */

import { useEffect, useState } from "react";
import { api } from "../lib/api";
import FilmCard from "../components/FilmCard";

export default function MesFilms() {
  const [items, setItems] = useState([]);
  const [filtre, setFiltre] = useState("tous"); // tous | vus | avoir
  const [charge, setCharge] = useState(true);

  async function charger() {
    setCharge(true);
    const vu = filtre === "vus" ? true : filtre === "avoir" ? false : undefined;
    setItems(await api.mesFilms(vu));
    setCharge(false);
  }

  useEffect(() => { charger(); }, [filtre]);

  async function majStatut(filmId, modif) {
    await api.majStatut(filmId, modif);
    charger();
  }

  const onglet = (val, label) => (
    <button
      onClick={() => setFiltre(val)}
      className={filtre === val ? "btn" : "btn btn-fantome"}
      style={{ padding: "8px 16px" }}
    >
      {label}
    </button>
  );

  return (
    <div>
      <h1 style={{ marginBottom: 6 }}>Mes films</h1>
      <p className="muet" style={{ marginBottom: 24 }}>Ta cinémathèque personnelle.</p>

      <div style={{ display: "flex", gap: 10, marginBottom: 32 }}>
        {onglet("tous", "Tous")}
        {onglet("vus", "Vus")}
        {onglet("avoir", "À voir")}
      </div>

      {charge ? (
        <p className="muet">Chargement…</p>
      ) : items.length === 0 ? (
        <p className="muet">Rien ici pour l'instant. Note ou coche des films dans le catalogue.</p>
      ) : (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(190px, 1fr))",
            gap: 22,
          }}
        >
          {items.map(({ film, statut }) => (
            <FilmCard
              key={film.id}
              film={film}
              statut={statut}
              onVu={(vu) => majStatut(film.id, { vu })}
              onNote={(note) => majStatut(film.id, { note, vu: true })}
            />
          ))}
        </div>
      )}
    </div>
  );
}
