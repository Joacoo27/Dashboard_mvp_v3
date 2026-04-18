// ChartPanel.jsx — section title + pulsing info capsule + Plotly-style container
function ChartPanel({ title, description, children }) {
  const [open, setOpen] = React.useState(false);
  return (
    <div style={iwChartStyles.wrap}>
      <div style={iwChartStyles.titleRow}>
        <div style={iwChartStyles.title} data-iw="chart-title">{title}</div>
        <div style={iwChartStyles.capWrap}>
          <button onClick={() => setOpen(o => !o)} style={iwChartStyles.capBtn} data-iw="chart-info">i</button>
          {open && (
            <div style={iwChartStyles.popover} data-iw="chart-popover">
              <button onClick={() => setOpen(false)} style={iwChartStyles.popClose}>×</button>
              <div style={iwChartStyles.popTitle} data-iw="pop-title">📊 {title}</div>
              <div style={iwChartStyles.popText} data-iw="pop-text">{description}</div>
            </div>
          )}
        </div>
      </div>
      <div style={iwChartStyles.container} data-iw="chart-container">{children}</div>
    </div>
  );
}

// Simple faux-plotly visuals (area + bars + line)
function TrendMiniChart({ bars, line, labels }) {
  const max = Math.max(...bars, ...line, 1);
  const w = 560, h = 220, pad = 28;
  const bw = (w - pad * 2) / bars.length;
  return (
    <svg viewBox={`0 0 ${w} ${h}`} style={{width:'100%', height:220, display:'block'}}>
      {[0.25, 0.5, 0.75, 1].map(f => (
        <line key={f} x1={pad} x2={w-pad} y1={h-pad-(h-pad*2)*f} y2={h-pad-(h-pad*2)*f} stroke="#e2e8f0" strokeDasharray="2 3"/>
      ))}
      {bars.map((v, i) => {
        const bh = (v/max) * (h-pad*2);
        return <rect key={i} x={pad + i*bw + 4} y={h-pad-bh} width={bw-8} height={bh} rx="3" fill="#3b82f6" opacity="0.85"/>;
      })}
      <polyline fill="none" stroke="#ef4444" strokeWidth="2.5" strokeDasharray="5 4"
        points={line.map((v,i) => `${pad + i*bw + bw/2},${h-pad-(v/max)*(h-pad*2)}`).join(' ')}/>
      {line.map((v,i) => (
        <circle key={i} cx={pad + i*bw + bw/2} cy={h-pad-(v/max)*(h-pad*2)} r="3" fill="#ef4444"/>
      ))}
      {labels && labels.map((l,i) => (
        <text key={i} x={pad + i*bw + bw/2} y={h-8} textAnchor="middle" fontSize="10" fill="#64748b" fontWeight="700">{l}</text>
      ))}
      <g transform="translate(28, 10)">
        <rect x="0" y="0" width="14" height="10" fill="#3b82f6" rx="2"/>
        <text x="20" y="9" fontSize="10.5" fill="#14233b" fontWeight="700">Ingreso Real</text>
        <line x1="120" y1="5" x2="140" y2="5" stroke="#ef4444" strokeWidth="2.5" strokeDasharray="4 3"/>
        <text x="146" y="9" fontSize="10.5" fill="#14233b" fontWeight="700">Presupuesto</text>
      </g>
    </svg>
  );
}

const iwChartStyles = {
  wrap: { marginTop:10 },
  titleRow: { display:'flex', alignItems:'center', gap:10, marginBottom:8, position:'relative' },
  title: { color:'#111827', fontSize:17, fontWeight:800, letterSpacing:'-0.01em' },
  capWrap: { position:'relative' },
  capBtn: { background:'#0A1261', border:'2px solid rgba(255,255,255,.3)', color:'#fff', width:24, height:24, borderRadius:'50%', cursor:'pointer', fontSize:12, fontWeight:900, boxShadow:'0 4px 12px rgba(10,18,97,.3)', animation:'iwPulseBlue 2s infinite' },
  popover: { position:'absolute', top:36, left:0, width:300, background:'rgba(255,255,255,.98)', border:'1px solid rgba(10,18,97,.15)', borderRadius:20, padding:'16px 18px', boxShadow:'0 20px 50px rgba(10,18,97,.2)', zIndex:10 },
  popClose: { position:'absolute', top:8, right:10, background:'none', border:'none', color:'#94a3b8', fontSize:18, cursor:'pointer', fontWeight:700 },
  popTitle: { color:'#0A1261', fontSize:14, fontWeight:800, marginBottom:6 },
  popText: { color:'#475569', fontSize:12.5, lineHeight:1.5, fontWeight:500 },
  container: { background:'rgba(255,255,255,.98)', border:'1px solid rgba(30,58,138,.08)', borderRadius:16, boxShadow:'0 12px 30px rgba(20,35,59,.06)', padding:'12px 14px 6px' }
};
window.ChartPanel = ChartPanel;
window.TrendMiniChart = TrendMiniChart;

// Dual-axis chart — blue bars (stock) + red line (coverage months)
function StockCoverageChart({ stock, cobertura, labels }) {
  const w = 680, h = 260, padL = 44, padR = 44, padT = 28, padB = 34;
  const maxStock = Math.max(...stock) * 1.1;
  const maxCob = Math.max(...cobertura) * 1.15;
  const innerW = w - padL - padR;
  const innerH = h - padT - padB;
  const bw = innerW / stock.length;
  const x = (i) => padL + i * bw + bw/2;
  const yStock = (v) => padT + innerH - (v/maxStock) * innerH;
  const yCob = (v) => padT + innerH - (v/maxCob) * innerH;
  const fmtK = (v) => v >= 1000 ? (v/1000).toFixed(0) + 'K' : v;

  return (
    <svg viewBox={`0 0 ${w} ${h}`} style={{width:'100%', height:260, display:'block'}}>
      {[0, 0.25, 0.5, 0.75, 1].map(f => (
        <line key={f} x1={padL} x2={w-padR} y1={padT + innerH*(1-f)} y2={padT + innerH*(1-f)} stroke="#e2e8f0" strokeDasharray="2 3"/>
      ))}
      {[0, 0.25, 0.5, 0.75, 1].map(f => (
        <text key={'ls'+f} x={padL-6} y={padT + innerH*(1-f) + 3} textAnchor="end" fontSize="9.5" fill="#64748b" fontWeight="700">{fmtK(Math.round(maxStock*f))}</text>
      ))}
      {[0, 0.25, 0.5, 0.75, 1].map(f => (
        <text key={'rs'+f} x={w-padR+6} y={padT + innerH*(1-f) + 3} textAnchor="start" fontSize="9.5" fill="#ef4444" fontWeight="700">{(maxCob*f).toFixed(1)}</text>
      ))}
      <text x={10} y={padT-6} fontSize="10" fontWeight="800" fill="#0A1261">Unid.</text>
      <text x={w-padR+6} y={padT-6} fontSize="10" fontWeight="800" fill="#ef4444">Meses</text>

      {stock.map((v,i) => {
        const bh = padT + innerH - yStock(v);
        return (
          <g key={i}>
            <rect x={x(i) - bw*0.36} y={yStock(v)} width={bw*0.72} height={bh} rx="4" fill="#3b82f6" opacity="0.88"/>
            <text x={x(i)} y={yStock(v)-5} textAnchor="middle" fontSize="9.5" fontWeight="800" fill="#0A1261">{fmtK(v)}</text>
          </g>
        );
      })}

      <polyline fill="none" stroke="#ef4444" strokeWidth="2.5"
        points={cobertura.map((v,i) => `${x(i)},${yCob(v)}`).join(' ')}/>
      {cobertura.map((v,i) => (
        <g key={i}>
          <circle cx={x(i)} cy={yCob(v)} r="3.5" fill="#ef4444" stroke="#fff" strokeWidth="1.5"/>
          <text x={x(i)} y={yCob(v)-8} textAnchor="middle" fontSize="9.5" fontWeight="800" fill="#ef4444">{v.toFixed(1)}</text>
        </g>
      ))}

      {labels.map((l,i) => (
        <text key={i} x={x(i)} y={h-10} textAnchor="middle" fontSize="9.5" fill="#64748b" fontWeight="700">{l}</text>
      ))}

      <g transform={`translate(${padL}, 6)`}>
        <rect x="0" y="0" width="12" height="10" fill="#3b82f6" rx="2"/>
        <text x="17" y="9" fontSize="10.5" fill="#14233b" fontWeight="700">Stock (Unid.)</text>
        <line x1="110" y1="5" x2="128" y2="5" stroke="#ef4444" strokeWidth="2.5"/>
        <circle cx="119" cy="5" r="3" fill="#ef4444"/>
        <text x="134" y="9" fontSize="10.5" fill="#14233b" fontWeight="700">Meses de Inv.</text>
      </g>
    </svg>
  );
}
window.StockCoverageChart = StockCoverageChart;
