// FlipCard.jsx — 3D flip, front = KPI, back = explanation
function FlipCard({ title, value, delta, meta, explanation }) {
  const [flipped, setFlipped] = React.useState(false);
  const showDelta = typeof delta === 'number';
  const positive = showDelta && delta >= 0;
  return (
    <div style={iwFlipStyles.wrap} onClick={() => setFlipped(f => !f)} data-iw="flip-card">
      <div style={{...iwFlipStyles.inner, transform: flipped ? 'rotateY(180deg)' : 'rotateY(0)'}}>
        <div style={{...iwFlipStyles.face, ...iwFlipStyles.front}} className="flip-front">
          <div style={iwFlipStyles.title} className="flip-title">{title}</div>
          <div style={iwFlipStyles.value} className="flip-value">{value}</div>
          {showDelta && (
            <div style={{...iwFlipStyles.delta, color: positive ? '#2bb673' : '#ef4444'}} className="flip-delta">
              {positive ? '▲' : '▼'} {Math.abs(delta).toFixed(1)}% vs referencia
            </div>
          )}
          {meta && <div style={iwFlipStyles.meta} className="flip-meta">{meta}</div>}
          <div style={iwFlipStyles.hint} data-iw="flip-hint" className="flip-hint">↻ Haz clic para ver explicación</div>
        </div>
        <div style={{...iwFlipStyles.face, ...iwFlipStyles.back}} className="flip-back">
          <div style={iwFlipStyles.backTitle}>{title}</div>
          <div style={iwFlipStyles.backDesc}>{explanation}</div>
          <div style={{...iwFlipStyles.hint, color:'rgba(255,255,255,.6)', marginTop:10}}>Haz clic para volver</div>
        </div>
      </div>
    </div>
  );
}
const iwFlipStyles = {
  wrap: { perspective:1200, height:132, cursor:'pointer' },
  inner: { position:'relative', width:'100%', height:'100%', transition:'transform .6s cubic-bezier(.4,.2,.2,1)', transformStyle:'preserve-3d' },
  face: { position:'absolute', inset:0, backfaceVisibility:'hidden', WebkitBackfaceVisibility:'hidden', borderRadius:14, padding:'12px 14px', boxShadow:'0 8px 24px rgba(31,38,135,.05)', border:'1px solid rgba(0,0,0,.05)', display:'flex', flexDirection:'column', justifyContent:'center', textAlign:'center', gap:3, boxSizing:'border-box' },
  front: { background:'rgba(255,255,255,.95)', backdropFilter:'blur(10px)' },
  back: { background:'#0A1261', color:'#fff', transform:'rotateY(180deg)' },
  title: { color:'#64748b', fontSize:10.5, fontWeight:700, textTransform:'uppercase', letterSpacing:1 },
  value: { color:'#14233b', fontSize:'clamp(1.5rem, 1.9vw, 2.1rem)', fontWeight:800, fontVariantNumeric:'tabular-nums', letterSpacing:'-0.01em', lineHeight:1.05 },
  delta: { fontSize:11.5, fontWeight:700 },
  meta: { color:'#94a3b8', fontSize:11, fontWeight:600 },
  hint: { color:'#94a3b8', fontSize:9.5, fontWeight:600, marginTop:3 },
  backTitle: { color:'#60a5fa', fontSize:11.5, fontWeight:700, textTransform:'uppercase', letterSpacing:1, marginBottom:4 },
  backDesc: { color:'rgba(255,255,255,.92)', fontSize:11.5, lineHeight:1.4, fontWeight:500, padding:'0 4px' }
};
window.FlipCard = FlipCard;
