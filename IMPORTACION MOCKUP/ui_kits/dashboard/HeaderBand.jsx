// HeaderBand.jsx
function HeaderBand({ title, description }) {
  return (
    <>
      <div style={iwBandStyles.band} data-iw="header-band">{title}</div>
      {description && <p style={iwBandStyles.desc} data-iw="header-desc">{description}</p>}
    </>
  );
}
const iwBandStyles = {
  band: { background:'#0A1261', color:'#fff', padding:'14px 22px', borderRadius:10, fontSize:'clamp(1.15rem, 1.5vw, 1.5rem)', fontWeight:800, minHeight:52, display:'flex', alignItems:'center', boxShadow:'0 8px 22px rgba(20,35,59,.14)', marginBottom:10, letterSpacing:'-0.01em' },
  desc: { color:'#64748b', marginTop:-2, marginBottom:14, fontSize:12.5, fontWeight:600 }
};
window.HeaderBand = HeaderBand;
