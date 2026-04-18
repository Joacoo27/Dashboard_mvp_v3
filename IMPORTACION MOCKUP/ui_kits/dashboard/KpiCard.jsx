// KpiCard.jsx — standard metric card
function KpiCard({ title, value, delta, meta, help, danger }) {
  const showDelta = typeof delta === 'number';
  const positive = showDelta && delta >= 0;
  const color = positive ? '#2bb673' : '#ef4444';
  const arrow = positive ? '▲' : '▼';
  return (
    <div style={iwKpiStyles.card} data-iw="kpi-card">
      {help && (
        <span style={iwKpiStyles.helpDot} title={help}>i</span>
      )}
      <div style={iwKpiStyles.title}>{title}</div>
      <div style={{...iwKpiStyles.value, color: danger ? '#14233b' : '#14233b'}}>{value}</div>
      {showDelta && (
        <div style={{...iwKpiStyles.delta, color}}>{arrow} {Math.abs(delta).toFixed(1)}% vs mes anterior</div>
      )}
      {meta && <div style={iwKpiStyles.meta}>{meta}</div>}
    </div>
  );
}
const iwKpiStyles = {
  card: { background:'rgba(255,255,255,.95)', backdropFilter:'blur(10px)', padding:'14px 14px', borderRadius:14, textAlign:'center', border:'1px solid rgba(0,0,0,.05)', boxShadow:'0 8px 24px rgba(31,38,135,.05)', height:132, display:'flex', flexDirection:'column', justifyContent:'center', gap:4, position:'relative' },
  title: { color:'#64748b', fontSize:10.5, fontWeight:700, textTransform:'uppercase', letterSpacing:1, minHeight:'1.9rem', display:'flex', alignItems:'center', justifyContent:'center', lineHeight:1.2 },
  value: { fontSize:'clamp(1.5rem, 1.9vw, 2.1rem)', lineHeight:1.05, fontWeight:800, minHeight:'2.5rem', display:'flex', alignItems:'center', justifyContent:'center', whiteSpace:'nowrap', fontVariantNumeric:'tabular-nums', letterSpacing:'-0.01em' },
  delta: { fontSize:11.5, fontWeight:700, minHeight:'1rem' },
  meta: { color:'#94a3b8', fontSize:11, fontWeight:600, minHeight:'1rem' },
  helpDot: { position:'absolute', top:10, right:10, width:17, height:17, borderRadius:'50%', background:'rgba(10,18,97,.08)', border:'1px solid rgba(10,18,97,.18)', color:'#0A1261', fontSize:10, fontWeight:800, display:'inline-flex', alignItems:'center', justifyContent:'center', cursor:'help' }
};
window.KpiCard = KpiCard;
