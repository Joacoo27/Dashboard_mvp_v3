// ThemeToggle.jsx — capsule toggle, sun/moon, persists to localStorage
function ThemeToggle({ theme, onChange }) {
  const isDark = theme === 'dark';
  return (
    <button
      type="button"
      role="switch"
      aria-checked={isDark}
      aria-label="Cambiar modo claro/oscuro"
      onClick={() => onChange(isDark ? 'light' : 'dark')}
      data-iw="theme-toggle"
      data-on={isDark ? '1' : '0'}
      style={{
        position: 'relative',
        width: 68,
        height: 34,
        borderRadius: 999,
        border: isDark ? '1px solid rgba(167,194,255,.35)' : '1px solid rgba(10,18,97,.2)',
        background: isDark
          ? 'linear-gradient(180deg, #1b2350, #0d1033)'
          : 'linear-gradient(180deg, #3b82f6, #1e3a8a)',
        boxShadow: isDark
          ? '0 6px 18px rgba(0,0,0,.45), inset 0 2px 6px rgba(0,0,0,.4)'
          : '0 6px 18px rgba(30,58,138,.35), inset 0 2px 6px rgba(10,18,97,.35)',
        cursor: 'pointer',
        padding: 0,
        fontFamily: 'inherit',
        flexShrink: 0,
        overflow: 'hidden',
      }}
    >
      {/* Sun icon (left, behind) */}
      <span style={{
        position:'absolute', left: 9, top: '50%', transform:'translateY(-50%)',
        fontSize: 13, opacity: isDark ? 0.35 : 0.9, color:'#fff3cd',
        transition: 'opacity .25s ease, transform .25s ease',
        pointerEvents:'none'
      }}>☀</span>

      {/* Moon icon (right, behind) */}
      <span style={{
        position:'absolute', right: 10, top: '50%', transform:'translateY(-50%)',
        fontSize: 12, opacity: isDark ? 0.95 : 0.35, color:'#dbe2ff',
        transition: 'opacity .25s ease',
        pointerEvents:'none'
      }}>☾</span>

      {/* Knob */}
      <span style={{
        position:'absolute',
        top: 3,
        left: isDark ? 36 : 3,
        width: 28,
        height: 28,
        borderRadius: '50%',
        background: isDark
          ? 'radial-gradient(circle at 30% 30%, #eef2ff, #a7c2ff 55%, #5d7fd1 100%)'
          : 'radial-gradient(circle at 30% 30%, #ffffff, #dbe9ff 60%, #7aa8ff 100%)',
        boxShadow: '0 4px 10px rgba(0,0,0,.35), inset 0 -2px 4px rgba(0,0,0,.15), inset 0 2px 3px rgba(255,255,255,.6)',
        transition: 'left .28s cubic-bezier(.4,.15,.2,1.2), background .25s ease',
      }}/>
    </button>
  );
}
window.ThemeToggle = ThemeToggle;
