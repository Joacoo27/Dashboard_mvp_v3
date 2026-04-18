// Sidebar.jsx — navy fill, logo slot, filters
function Sidebar({ familias, onFamiliaToggle, selected, collapsed, onToggle, modulo, onModuloChange }) {
  return (
    <aside style={iwSidebarStyles.sidebar} data-collapsed={collapsed}>
      <div style={iwSidebarStyles.inner}>
        <button onClick={onToggle} style={iwSidebarStyles.collapse} aria-label="Toggle sidebar" data-iw="collapse">‹</button>
        <div style={iwSidebarStyles.logoSlot}>
          <img src="../../assets/logo_mark.svg" width="36" height="36" alt="" style={{display:'block'}}/>
          <div>
            <div style={{fontWeight:900,letterSpacing:'-0.02em',fontSize:17,color:'#fff',lineHeight:1}}>Interwins</div>
            <div style={{fontSize:10,color:'rgba(255,255,255,.6)',fontWeight:700,letterSpacing:1,marginTop:3}}>PANEL EJECUTIVO</div>
          </div>
        </div>

        <div style={iwSidebarStyles.divider}/>
        <div style={iwSidebarStyles.sectionLabel}>🧭 Sección</div>
        <div style={iwSidebarStyles.moduleWrap}>
          {[
            {id:'financiera', label:'Financiera', icon:'💰'},
            {id:'operacional', label:'Operacional', icon:'📦'},
          ].map(m => (
            <button key={m.id} onClick={() => onModuloChange(m.id)} data-iw="module-btn" data-on={modulo === m.id ? "1" : "0"}
              style={{...iwSidebarStyles.moduleBtn, ...(modulo === m.id ? iwSidebarStyles.moduleBtnOn : {})}}>
              <span style={{fontSize:14}}>{m.icon}</span>
              <span>{m.label}</span>
              {modulo === m.id && <span style={iwSidebarStyles.moduleDot}/>}
            </button>
          ))}
        </div>

        <div style={iwSidebarStyles.divider}/>
        <div style={iwSidebarStyles.sectionLabel}>🔄 Datos en Caché</div>
        <button style={iwSidebarStyles.lightBtn} data-iw="light-btn">Actualizar desde BD</button>

        <div style={iwSidebarStyles.divider}/>
        <div style={iwSidebarStyles.sectionLabel}>🎯 Filtros Globales</div>
        <div style={{...iwSidebarStyles.labelSm}}>Familia</div>
        <div style={iwSidebarStyles.chipWrap}>
          {familias.map(f => (
            <button key={f} onClick={() => onFamiliaToggle(f)} data-iw="chip"
              style={{...iwSidebarStyles.chip, ...(selected.includes(f) ? iwSidebarStyles.chipOn : {})}}>
              {f}
            </button>
          ))}
        </div>

        <div style={{...iwSidebarStyles.labelSm, marginTop: 14}}>Proveedor</div>
        <div style={iwSidebarStyles.selectField} data-iw="select-field">Todos ▾</div>

        <div style={{...iwSidebarStyles.labelSm, marginTop: 10}}>Tiering</div>
        <div style={iwSidebarStyles.selectField} data-iw="select-field">A · B · C ▾</div>

        <div style={iwSidebarStyles.divider}/>
        <div style={iwSidebarStyles.sectionLabel}>⚙️ Configuración Logística</div>
        <div style={{...iwSidebarStyles.labelSm, display:'flex',alignItems:'center',gap:6}}>
          Política de Inventario (Meses)
          <span style={iwSidebarStyles.helpDot} title="Umbral de meses para clasificar exceso">i</span>
        </div>
        <div style={iwSidebarStyles.slider}>
          <div style={iwSidebarStyles.sliderTrack}/>
          <div style={iwSidebarStyles.sliderThumb} data-iw="slider-thumb">3</div>
        </div>
      </div>
    </aside>
  );
}

const iwSidebarStyles = {
  sidebar: { background:'#0A1261', color:'#fff', minHeight:'100vh', width:248, flexShrink:0, borderRight:'1px solid rgba(255,255,255,.08)', transition:'width .2s ease', position:'relative' },
  inner: { padding:'14px 14px', display:'flex', flexDirection:'column', gap:3 },
  collapse: { position:'absolute', top:14, right:-12, width:24, height:24, borderRadius:'50%', background:'#fff', color:'#0A1261', border:'1px solid rgba(10,18,97,.2)', boxShadow:'0 4px 12px rgba(20,35,59,.15)', cursor:'pointer', fontSize:14, fontWeight:900, display:'flex', alignItems:'center', justifyContent:'center', zIndex:2 },
  logoSlot: { display:'flex', gap:10, alignItems:'center', padding:'2px 2px 10px' },
  divider: { height:1, background:'rgba(255,255,255,.12)', margin:'8px 0' },
  sectionLabel: { fontSize:12.5, fontWeight:800, letterSpacing:'.01em', marginBottom:7, color:'#fff' },
  labelSm: { fontSize:11.5, fontWeight:700, color:'rgba(255,255,255,.85)', marginBottom:5 },
  chipWrap: { display:'flex', flexWrap:'wrap', gap:6 },
  chip: { background:'rgba(255,255,255,.12)', color:'#fff', border:'1px solid rgba(255,255,255,.15)', borderRadius:999, padding:'5px 10px', fontSize:11.5, fontWeight:700, cursor:'pointer', fontFamily:'inherit' },
  chipOn: { background:'rgba(59,130,246,.35)', borderColor:'rgba(59,130,246,.55)', boxShadow:'0 4px 12px rgba(0,0,0,.2)' },
  selectField: { background:'linear-gradient(180deg, rgba(255,255,255,.96), rgba(247,250,255,.96))', color:'#14233b', borderRadius:12, padding:'8px 11px', fontSize:12, fontWeight:600, boxShadow:'0 10px 24px rgba(20,35,59,.05)', border:'1px solid rgba(30,58,138,.12)' },
  lightBtn: { background:'linear-gradient(180deg, rgba(255,255,255,.96), rgba(245,249,255,.96))', color:'#14233b', fontWeight:700, border:'1px solid rgba(30,58,138,.12)', borderRadius:12, padding:'8px 12px', fontSize:12.5, cursor:'pointer', boxShadow:'0 10px 24px rgba(20,35,59,.05)', fontFamily:'inherit' },
  helpDot: { width:17, height:17, borderRadius:'50%', background:'rgba(255,255,255,.15)', border:'1px solid rgba(255,255,255,.3)', color:'#fff', fontSize:10, fontWeight:900, display:'inline-flex', alignItems:'center', justifyContent:'center', cursor:'help' },
  slider: { position:'relative', height:22, margin:'4px 6px' },
  sliderTrack: { position:'absolute', left:0, right:0, top:'50%', height:6, borderRadius:999, background:'linear-gradient(90deg, rgba(59,130,246,.45), rgba(30,58,138,.22))', transform:'translateY(-50%)' },
  sliderThumb: { position:'absolute', left:'22%', top:0, width:24, height:22, borderRadius:12, background:'linear-gradient(135deg, #14233b, #1e3a8a)', color:'#fff', fontSize:12, fontWeight:800, display:'flex', alignItems:'center', justifyContent:'center', boxShadow:'0 10px 22px rgba(30,58,138,.18)' },
  moduleWrap: { display:'flex', flexDirection:'column', gap:6 },
  moduleBtn: { position:'relative', display:'flex', alignItems:'center', gap:9, padding:'8px 11px', borderRadius:11, background:'rgba(255,255,255,.06)', color:'rgba(255,255,255,.78)', border:'1px solid rgba(255,255,255,.08)', fontSize:12.5, fontWeight:700, cursor:'pointer', fontFamily:'inherit', textAlign:'left' },
  moduleBtnOn: { background:'linear-gradient(180deg, rgba(59,130,246,.35), rgba(30,58,138,.45))', color:'#fff', border:'1px solid rgba(96,165,250,.5)', boxShadow:'0 6px 16px rgba(0,0,0,.22)' },
  moduleDot: { position:'absolute', right:12, top:'50%', transform:'translateY(-50%)', width:7, height:7, borderRadius:'50%', background:'#60a5fa', boxShadow:'0 0 0 3px rgba(96,165,250,.25)' }
};
window.Sidebar = Sidebar;
