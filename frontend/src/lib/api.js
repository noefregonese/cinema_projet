/* ============================================================================
   lib/api.js — Client HTTP vers le backend
   ----------------------------------------------------------------------------
   Centralise tous les appels à l'API. Avantages :
   - une seule URL de base à changer (dev / prod),
   - le token JWT est injecté automatiquement dans chaque requête,
   - la gestion d'erreur est uniforme.
   ============================================================================ */

// URL du backend. En local, on tape sur localhost:8000 par défaut.
// En production (Vercel), on définit VITE_API_URL vers l'URL Render.
const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Le token est gardé en mémoire ET dans localStorage (pour survivre au refresh).
let token = localStorage.getItem("token") || null;

export function setToken(nouveau) {
  token = nouveau;
  if (nouveau) localStorage.setItem("token", nouveau);
  else localStorage.removeItem("token");
}

export function getToken() {
  return token;
}

// Requête générique. `options` accepte { method, body, form }.
async function requete(chemin, options = {}) {
  const headers = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;

  let corps;
  if (options.form) {
    // login : format application/x-www-form-urlencoded (standard OAuth2)
    corps = new URLSearchParams(options.form).toString();
    headers["Content-Type"] = "application/x-www-form-urlencoded";
  } else if (options.body !== undefined) {
    corps = JSON.stringify(options.body);
    headers["Content-Type"] = "application/json";
  }

  const r = await fetch(`${BASE}${chemin}`, {
    method: options.method || "GET",
    headers,
    body: corps,
  });

  if (r.status === 204) return null; // pas de contenu (delete)

  const data = await r.json().catch(() => null);
  if (!r.ok) {
    const msg = data?.detail || `Erreur ${r.status}`;
    throw new Error(typeof msg === "string" ? msg : "Erreur serveur");
  }
  return data;
}

/* ---- Endpoints regroupés par thème ---- */

export const api = {
  // Authentification
  register: (email, mot_de_passe, pseudo) =>
    requete("/auth/register", { method: "POST", body: { email, mot_de_passe, pseudo } }),
  login: (email, mot_de_passe) =>
    requete("/auth/login", { method: "POST", form: { username: email, password: mot_de_passe } }),
  moi: () => requete("/auth/me"),

  // Catalogue
  films: (params = {}) => {
    const q = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== "" && v != null)
    ).toString();
    return requete(`/films${q ? "?" + q : ""}`);
  },
  film: (id) => requete(`/films/${id}`),

  // Mes films
  mesFilms: (vu, tri) => {
    const q = new URLSearchParams();
    if (vu !== undefined) q.set("vu", vu);
    if (tri) q.set("tri", tri);
    const s = q.toString();
    return requete(`/me/films${s ? "?" + s : ""}`);
  },
  mesStats: () => requete("/me/stats"),
  majStatut: (filmId, statut) =>
    requete(`/me/films/${filmId}`, { method: "PUT", body: statut }),
  retirerFilm: (filmId) => requete(`/me/films/${filmId}`, { method: "DELETE" }),

  // Import TMDb
  rechercheTmdb: (q) => requete(`/import/recherche?q=${encodeURIComponent(q)}`),
  importerFilm: (tmdbId) => requete(`/import/film/${tmdbId}`, { method: "POST" }),
  decouvrir: (params = {}) => {
    const q = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== "" && v != null)
    ).toString();
    return requete(`/import/decouvrir${q ? "?" + q : ""}`);
  },
  marquerTmdb: (tmdbId, vu, note, infos = {}) => {
    const q = new URLSearchParams({ vu });
    if (note != null) q.set("note", note);
    for (const [cle, val] of Object.entries(infos)) {
      if (val != null && val !== "") q.set(cle, val);
    }
    return requete(`/import/statut/${tmdbId}?${q.toString()}`, { method: "POST" });
  },
};
