/* ============================================================================
   pages/Filmotheque.jsx — Ma filmothèque
   ----------------------------------------------------------------------------
   1. Écran de choix : « films que j'ai vus » ou « films que je n'ai pas vus ».
   2a. Vus      → tableau de bord : statistiques, graphiques, coups de cœur,
                  puis liste triable.
   2b. Pas vus  → liste triée par note du public.
   3. Tout en bas : un bouton « + » vers une page « Bientôt ! ».
   ============================================================================ */

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import FilmCard from "../components/FilmCard";
import BarChart from "../components/BarChart";
import NoteEtoiles from "../components/NoteEtoiles";

export default function Filmotheque() {
  const [vue, setVue] = useState(null); // null | "vus" | "nonvus"

  if (vue === null) return <Choix onChoix={setVue} />;
  if (vue === "vus") return <Vus onRetour={() => setVue(null)} />;
  return <NonVus onRetour={() => setVue(null)} />;
}

/* ---------- Écran de choix ---------- */
function Choix({ onChoix }) {
  const carte = (cle, titre, desc) => (
    <button
      onClick={() => onChoix(cle)}
      style={{
        flex: 1, minWidth: 220, padding: "40px 28px", textAlign: "left",
        background: "var(--surface)", border: "1px solid var(--bordure)",
        borderRadius: "var(--rayon)", cursor: "pointer", boxShadow: "var(--ombre)",
        transition: "transform .12s ease",
      }}
      onMouseEnter={(e) => (e.currentTarget.style.transform = "translateY(-3px)")}
      onMouseLeave={(e) => (e.currentTarget.style.transform = "none")}
    >
      <h2 style={{ marginBottom: 8 }}>{titre}</h2>
      <p className="muet">{desc}</p>
    </button>
  );

  return (
    <div style={{ maxWidth: 760, margin: "0 auto" }}>
      <div style={{ textAlign: "center", marginBottom: 40 }}>
        <h1 style={{ marginBottom: 6 }}>Ma filmothèque</h1>
        <p className="muet">Que veux-tu explorer ?</p>
      </div>
      <div style={{ display: "flex", gap: 20, flexWrap: "wrap" }}>
        {carte("vus", "Les films que j'ai vus", "Tes statistiques, tes goûts, tes coups de cœur.")}
        {carte("nonvus", "Les films que je n'ai pas vus", "Ta liste à voir, triée par popularité.")}
      </div>
    </div>
  );
}

/* ---------- Bouton retour + clicker bas de page (réutilisés) ---------- */
function Retour({ onRetour }) {
  return (
    <button className="btn btn-fantome" onClick={onRetour} style={{ marginBottom: 24 }}>
      ← Retour
    </button>
  );
}

function ClickerPlus() {
  const nav = useNavigate();
  return (
    <div style={{ textAlign: "center", marginTop: 60 }}>
      <button
        onClick={() => nav("/bientot")}
        style={{
          width: 54, height: 54, borderRadius: "50%",
          border: "1px dashed var(--bordure)", background: "var(--surface)",
          fontSize: "1.6rem", color: "var(--texte-doux)", cursor: "pointer",
        }}
        title="Bientôt"
      >
        +
      </button>
    </div>
  );
}

/* ---------- Vue « films vus » : tableau de bord ---------- */
function Vus({ onRetour }) {
  const [stats, setStats] = useState(null);
  const [films, setFilms] = useState([]);
  const [tri, setTri] = useState("note");
  const [charge, setCharge] = useState(true);

  useEffect(() => {
    Promise.all([api.mesStats(), api.mesFilms(true, tri)]).then(([s, f]) => {
      setStats(s);
      setFilms(f);
      setCharge(false);
    });
  }, []);

  useEffect(() => {
    api.mesFilms(true, tri).then(setFilms);
  }, [tri]);

  if (charge) return <div><Retour onRetour={onRetour} /><p className="muet">Chargement…</p></div>;

  if (stats.total_vus === 0) {
    return (
      <div>
        <Retour onRetour={onRetour} />
        <p className="muet">Tu n'as encore marqué aucun film comme vu. Va dans « Enrichir mon profil » pour commencer.</p>
        <ClickerPlus />
      </div>
    );
  }

  const carteStat = (valeur, label) => (
    <div style={{ flex: 1, minWidth: 130, background: "var(--surface)", border: "1px solid var(--bordure)", borderRadius: "var(--rayon)", padding: "20px 22px" }}>
      <div style={{ fontFamily: "var(--font-titre)", fontSize: "2rem", fontWeight: 600 }}>{valeur}</div>
      <div className="muet" style={{ fontSize: ".88rem" }}>{label}</div>
    </div>
  );

  const bloc = (titre, contenu) => (
    <div style={{ background: "var(--surface)", border: "1px solid var(--bordure)", borderRadius: "var(--rayon)", padding: 24 }}>
      <h2 style={{ fontSize: "1.15rem", marginBottom: 18 }}>{titre}</h2>
      {contenu}
    </div>
  );

  return (
    <div>
      <Retour onRetour={onRetour} />
      <h1 style={{ marginBottom: 4 }}>Les films que j'ai vus</h1>
      <p className="muet" style={{ marginBottom: 28 }}>Un aperçu de tes goûts cinéma.</p>

      {/* Chiffres clés */}
      <div style={{ display: "flex", gap: 16, flexWrap: "wrap", marginBottom: 20 }}>
        {carteStat(stats.total_vus, "films vus")}
        {carteStat(stats.note_moyenne ?? "—", "note moyenne")}
        {carteStat(stats.nb_notes, "films notés")}
        {carteStat(stats.decennies.length ? `${stats.decennies.sort((a,b)=>b.nb-a.nb)[0].decennie}s` : "—", "décennie favorite")}
      </div>

      {/* Graphiques */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: 16, marginBottom: 20 }}>
        {bloc("Genres favoris", (
          <BarChart data={stats.genres.map((g) => ({ label: g.nom, valeur: g.nb }))} />
        ))}
        {bloc("Pays les plus vus", (
          <BarChart data={stats.pays.map((p) => ({ label: p.nom, valeur: p.nb }))} couleur="var(--etoile)" />
        ))}
        {bloc("Par décennie", (
          <BarChart data={stats.decennies.map((d) => ({ label: `${d.decennie}s`, valeur: d.nb }))} />
        ))}
        {bloc("Distribution de tes notes", (
          <BarChart data={stats.distribution_notes.map((d) => ({ label: `${d.note}/10`, valeur: d.nb }))} couleur="var(--etoile)" />
        ))}
      </div>

      {/* Coups de cœur */}
      {stats.coups_de_coeur.length > 0 && (
        <div style={{ marginBottom: 36 }}>
          <h2 style={{ fontSize: "1.15rem", marginBottom: 16 }}>Tes coups de cœur</h2>
          <div style={{ display: "flex", gap: 16, overflowX: "auto", paddingBottom: 8 }}>
            {stats.coups_de_coeur.map((f) => (
              <div key={f.id} style={{ width: 130, flexShrink: 0 }}>
                <div style={{ aspectRatio: "2/3", borderRadius: 10, overflow: "hidden", background: "var(--accent-clair)", marginBottom: 8 }}>
                  {f.affiche && <img src={f.affiche} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />}
                </div>
                <div style={{ fontSize: ".85rem", fontWeight: 600, lineHeight: 1.2 }}>{f.titre}</div>
                <div className="muet" style={{ fontSize: ".8rem" }}>{f.note}/10</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Liste complète triable */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 18, flexWrap: "wrap", gap: 12 }}>
        <h2 style={{ fontSize: "1.15rem" }}>Tous mes films vus</h2>
        <select
          value={tri}
          onChange={(e) => setTri(e.target.value)}
          style={{ padding: "8px 12px", border: "1px solid var(--bordure)", borderRadius: "var(--rayon-sm)", background: "var(--surface)", fontFamily: "inherit" }}
        >
          <option value="note">Trier par ma note</option>
          <option value="annee">Trier par année</option>
          <option value="recent">Plus récemment ajoutés</option>
        </select>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: 20 }}>
        {films.map(({ film, statut }) => (
          <FilmCard key={film.id} film={film} statut={statut} onVu={() => {}} onNote={() => {}} />
        ))}
      </div>

      <ClickerPlus />
    </div>
  );
}

/* ---------- Vue « films pas vus » : liste par note publique ---------- */
function NonVus({ onRetour }) {
  const [films, setFilms] = useState([]);
  const [charge, setCharge] = useState(true);

  useEffect(() => {
    api.mesFilms(false, "note_public").then((f) => { setFilms(f); setCharge(false); });
  }, []);

  return (
    <div>
      <Retour onRetour={onRetour} />
      <h1 style={{ marginBottom: 4 }}>Les films que je n'ai pas vus</h1>
      <p className="muet" style={{ marginBottom: 28 }}>Triés par note du public.</p>

      {charge ? (
        <p className="muet">Chargement…</p>
      ) : films.length === 0 ? (
        <p className="muet">Aucun film en attente. Marque des films « pas vu » dans « Enrichir mon profil ».</p>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: 20 }}>
          {films.map(({ film, statut }) => (
            <FilmCard key={film.id} film={film} statut={statut} onVu={() => {}} onNote={() => {}} />
          ))}
        </div>
      )}

      <ClickerPlus />
    </div>
  );
}
