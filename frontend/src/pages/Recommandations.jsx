/* ============================================================================
   pages/Recommandations.jsx — Page d'accueil
   ----------------------------------------------------------------------------
   Vide pour l'instant. Accueillera plus tard les recommandations boostées
   à l'IA, calculées à partir des films notés par l'utilisateur.
   ============================================================================ */

export default function Recommandations() {
  return (
    <div style={{ textAlign: "center", padding: "80px 20px", maxWidth: 560, margin: "0 auto" }}>
      <div style={{ fontSize: "2.4rem", marginBottom: 18 }}>✦</div>
      <h1 style={{ marginBottom: 14 }}>Recommandations</h1>
      <p className="muet" style={{ fontSize: "1.05rem", lineHeight: 1.6 }}>
        Bientôt, des films choisis pour toi en fonction de tes goûts.
        <br />
        Pour l'instant, commence par enrichir ton profil — plus tu notes de
        films, plus les recommandations seront justes.
      </p>
    </div>
  );
}
