// TopNav.jsx — horizontal button row, primary / secondary
function TopNav({ tabs, active, onChange, moduleLabel, moduleIcon }) {
  return (
    <nav style={iwTopNavStyles.wrap}>
      {moduleLabel && (
        <div style={iwTopNavStyles.moduleBadge}>
          {moduleIcon && <span style={{fontSize:14}}>{moduleIcon}</span>}
          <span style={{fontSize:10,fontWeight:800,letterSpacing:1.5,color:'rgba(255,255,255,.7)',textTransform:'uppercase'}}>Sección</span>
          <span style={{fontSize:13,fontWeight:900,color:'#fff',letterSpacing:'-.01em'}}>{moduleLabel}</span>
        </div>
      )}
      {tabs.map(t => {
        const isActive = t === active;
        return (
          <button key={t} onClick={() => onChange(t)} data-iw="tab-btn" data-on={isActive ? "1" : "0"}
            style={{...iwTopNavStyles.btn, ...(isActive ? iwTopNavStyles.active : iwTopNavStyles.inactive)}}>
            {t}
          </button>
        );
      })}
    </nav>
  );
}
const iwTopNavStyles = {
  wrap: { display:'flex', gap:8, flexWrap:'wrap', marginBottom:14, alignItems:'center' },
  moduleBadge: { display:'inline-flex', alignItems:'center', gap:7, padding:'7px 11px', borderRadius:12, background:'linear-gradient(135deg, #0A1261, #1e3a8a)', border:'1px solid rgba(96,165,250,.35)', boxShadow:'0 12px 24px rgba(10,18,97,.2)', marginRight:2 },
  btn: { fontFamily:'inherit', borderRadius:12, height:40, padding:'0 16px', fontWeight:800, fontSize:13, cursor:'pointer', lineHeight:1.2 },
  active: { background:'#0A1261', color:'#fff', border:'1px solid rgba(10,18,97,.95)', boxShadow:'0 16px 34px rgba(10,18,97,.22)' },
  inactive: { background:'rgba(255,255,255,.98)', color:'#111827', border:'1px solid rgba(20,35,59,.14)', boxShadow:'0 12px 28px rgba(20,35,59,.06)' }
};
window.TopNav = TopNav;
