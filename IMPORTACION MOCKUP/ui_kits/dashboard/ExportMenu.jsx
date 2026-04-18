// ExportMenu — dropdown para descargar el Estado de Resultados en Excel o PDF
// Recreación visual: los handlers disparan console.log + toast simulado.

const iwExportStyles = {
  wrap: { position: 'relative', display: 'inline-block' },
  trigger: {
    display: 'inline-flex', alignItems: 'center', gap: 8,
    background: 'linear-gradient(180deg, #0A1261 0%, #1e3a8a 100%)',
    color: '#fff', border: 'none',
    padding: '9px 16px', borderRadius: 10,
    fontSize: 12.5, fontWeight: 700, letterSpacing: .3,
    cursor: 'pointer',
    boxShadow: '0 10px 22px rgba(10,18,97,.28), inset 0 1px 0 rgba(255,255,255,.12)',
    transition: 'transform .15s ease, box-shadow .15s ease, filter .15s ease',
    fontFamily: 'inherit',
  },
  menu: {
    position: 'absolute', top: 'calc(100% + 8px)', right: 0,
    minWidth: 240,
    background: 'var(--iw-surface-solid)',
    border: '1px solid var(--iw-border-hair)',
    borderRadius: 12,
    boxShadow: '0 24px 56px rgba(10,18,97,.22), 0 2px 6px rgba(10,18,97,.1)',
    padding: 6,
    zIndex: 20,
    animation: 'iwExportIn .16s ease-out',
  },
  header: {
    padding: '8px 12px 6px',
    fontSize: 10.5, fontWeight: 800, letterSpacing: 1, textTransform: 'uppercase',
    color: 'var(--iw-slate-500)',
  },
  item: {
    display: 'flex', alignItems: 'center', gap: 12,
    padding: '10px 12px', borderRadius: 8,
    cursor: 'pointer',
    transition: 'background .12s ease',
    background: 'transparent', border: 'none', width: '100%', textAlign: 'left',
    fontFamily: 'inherit',
  },
  icon: {
    width: 32, height: 32, borderRadius: 8,
    display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
    fontSize: 14, fontWeight: 800, flexShrink: 0, color: '#fff',
  },
  itemTitle: { fontSize: 13, fontWeight: 700, color: 'var(--iw-ink)', lineHeight: 1.2 },
  itemDesc: { fontSize: 11, color: 'var(--iw-slate-500)', marginTop: 2, lineHeight: 1.3 },
  divider: { height: 1, background: 'var(--iw-border-hair)', margin: '4px 0' },
  footer: {
    padding: '8px 12px', fontSize: 10.5, color: 'var(--iw-slate-400)',
    borderTop: '1px solid var(--iw-border-hair)', marginTop: 4,
  },
  toast: {
    position: 'fixed', bottom: 24, right: 24,
    background: '#14233b', color: '#fff',
    padding: '12px 18px', borderRadius: 10,
    fontSize: 13, fontWeight: 600,
    boxShadow: '0 20px 40px rgba(0,0,0,.35), 0 0 0 1px rgba(255,255,255,.06)',
    display: 'flex', alignItems: 'center', gap: 10,
    zIndex: 100,
    animation: 'iwToastIn .2s ease-out',
  },
};

function ExportMenu() {
  const [open, setOpen] = React.useState(false);
  const [toast, setToast] = React.useState(null);
  const ref = React.useRef(null);

  React.useEffect(() => {
    if (!open) return;
    const onDoc = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    const onEsc = (e) => { if (e.key === 'Escape') setOpen(false); };
    document.addEventListener('mousedown', onDoc);
    document.addEventListener('keydown', onEsc);
    return () => { document.removeEventListener('mousedown', onDoc); document.removeEventListener('keydown', onEsc); };
  }, [open]);

  const handleExport = (kind) => {
    setOpen(false);
    const label = kind === 'xlsx' ? 'Excel (.xlsx)' : 'PDF';
    setToast({ kind, label });
    setTimeout(() => setToast(null), 2600);
  };

  return (
    <div style={iwExportStyles.wrap} ref={ref}>
      <button
        style={iwExportStyles.trigger}
        onClick={() => setOpen(o => !o)}
        onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-1px)'; e.currentTarget.style.filter = 'brightness(1.08)'; }}
        onMouseLeave={e => { e.currentTarget.style.transform = ''; e.currentTarget.style.filter = ''; }}
        aria-haspopup="menu" aria-expanded={open}
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 3v12"/><path d="m7 10 5 5 5-5"/><path d="M5 21h14"/>
        </svg>
        Descargar EE.RR
        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" style={{opacity:.85, transform: open ? 'rotate(180deg)' : 'none', transition:'transform .15s ease'}}>
          <path d="m6 9 6 6 6-6"/>
        </svg>
      </button>

      {open && (
        <div style={iwExportStyles.menu} role="menu">
          <div style={iwExportStyles.header}>Exportar Estado de Resultados</div>

          <button
            style={iwExportStyles.item}
            onMouseEnter={e => e.currentTarget.style.background = 'var(--iw-bg-subtle)'}
            onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
            onClick={() => handleExport('xlsx')}
            role="menuitem"
          >
            <span style={{...iwExportStyles.icon, background:'linear-gradient(135deg, #1d6f42, #2bb673)'}}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="m8 8 8 8"/><path d="m16 8-8 8"/></svg>
            </span>
            <span style={{flex:1}}>
              <div style={iwExportStyles.itemTitle}>Excel (.xlsx)</div>
              <div style={iwExportStyles.itemDesc}>Tabla editable con fórmulas de variación y cumplimiento.</div>
            </span>
          </button>

          <button
            style={iwExportStyles.item}
            onMouseEnter={e => e.currentTarget.style.background = 'var(--iw-bg-subtle)'}
            onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
            onClick={() => handleExport('pdf')}
            role="menuitem"
          >
            <span style={{...iwExportStyles.icon, background:'linear-gradient(135deg, #b91c1c, #ef4444)'}}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M9 13h6"/><path d="M9 17h4"/></svg>
            </span>
            <span style={{flex:1}}>
              <div style={iwExportStyles.itemTitle}>PDF</div>
              <div style={iwExportStyles.itemDesc}>Informe con membrete, listo para imprimir o compartir.</div>
            </span>
          </button>

          <div style={iwExportStyles.footer}>Corte Mar-2026 · CLP millones · YTD</div>
        </div>
      )}

      {toast && (
        <div style={iwExportStyles.toast} role="status">
          <span style={{
            width: 22, height: 22, borderRadius: '50%',
            background: toast.kind === 'xlsx' ? '#2bb673' : '#ef4444',
            display:'inline-flex', alignItems:'center', justifyContent:'center',
            fontSize: 12, fontWeight: 900,
          }}>✓</span>
          Descargando EE.RR · {toast.label}…
        </div>
      )}
    </div>
  );
}

// Keyframes (inject once)
if (typeof document !== 'undefined' && !document.getElementById('iw-export-keyframes')) {
  const st = document.createElement('style');
  st.id = 'iw-export-keyframes';
  st.textContent = `
    @keyframes iwExportIn { from { opacity:0; transform: translateY(-6px) scale(.98); } to { opacity:1; transform: translateY(0) scale(1); } }
    @keyframes iwToastIn  { from { opacity:0; transform: translateY(10px); } to { opacity:1; transform: translateY(0); } }
  `;
  document.head.appendChild(st);
}

window.ExportMenu = ExportMenu;
