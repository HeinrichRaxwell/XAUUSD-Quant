import React, { useEffect, useRef, useState } from 'react';
import { createChart, CandlestickSeries, LineSeries, LineStyle } from 'lightweight-charts';

export default function InteractiveQuantChart({ chartData: propChartData, isAnalyzing, onRefreshChart }) {
  const chartContainerRef = useRef(null);
  const overlayCanvasRef = useRef(null);
  const chartInstanceRef = useRef(null);

  const [internalChartData, setInternalChartData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch chart data internally if not provided by prop
  useEffect(() => {
    if (propChartData) {
      setInternalChartData(propChartData);
      setIsLoading(false);
      return;
    }

    const fetchChartData = () => {
      fetch('http://localhost:8000/api/chart_data')
        .then((res) => res.json())
        .then((data) => {
          if (data && !data.error) {
            setInternalChartData(data);
          }
        })
        .catch((err) => console.error('Error fetching chart data:', err))
        .finally(() => setIsLoading(false));
    };

    fetchChartData();
    const interval = setInterval(fetchChartData, 4000);
    return () => clearInterval(interval);
  }, [propChartData]);

  const activeData = propChartData || internalChartData;

  // Helper: Sanitize time objects
  const sanitize = (data) => {
    if (!Array.isArray(data)) return [];
    return data
      .map((item) => {
        if (!item || item.time === undefined || item.time === null) return null;
        let ts = item.time;
        if (typeof ts === 'string') {
          ts = Math.floor(new Date(ts).getTime() / 1000);
        } else if (typeof ts === 'number' && ts > 2e11) {
          ts = Math.floor(ts / 1000);
        }
        return { ...item, time: ts };
      })
      .filter((item) => item !== null && !isNaN(item.time))
      .sort((a, b) => a.time - b.time);
  };

  // Helper: Line segment interpolation for smooth Lightweight Charts rendering
  const interpolateLineSeries = (p1, p2, candles) => {
    if (!p1 || !p2 || !candles || candles.length === 0) return [];
    const t1 = p1.time;
    const t2 = p2.time;
    const v1 = p1.price;
    const v2 = p2.price;

    const inRange = candles.filter((c) => c.time >= t1 && c.time <= t2);
    if (inRange.length < 2) {
      return [
        { time: t1, value: v1 },
        { time: t2, value: v2 },
      ];
    }

    const minT = inRange[0].time;
    const maxT = inRange[inRange.length - 1].time;
    const dt = maxT - minT || 1;

    return inRange.map((c) => {
      const alpha = (c.time - minT) / dt;
      const interpVal = v1 + alpha * (v2 - v1);
      return { time: c.time, value: interpVal };
    });
  };

  // Draw Demand/Supply Zone Shaded Box & XABCD Vertex Badges on Overlay Canvas
  const updateOverlayCanvas = (chart, candleSeries, levels, direction, candles) => {
    const canvas = overlayCanvasRef.current;
    const container = chartContainerRef.current;
    if (!canvas || !container || !chart || !candleSeries || !levels || !candles || candles.length === 0) return;

    const width = (canvas.width = container.clientWidth || 800);
    const height = (canvas.height = container.clientHeight || 500);
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.clearRect(0, 0, width, height);

    const timeScale = chart.timeScale();
    const firstTs = candles[0].time;
    const lastRealTs = candles[Math.max(0, candles.length - 5)].time;

    const coordFirst = timeScale.timeToCoordinate(firstTs);
    const coordLast = timeScale.timeToCoordinate(lastRealTs);

    const xStart = coordFirst !== null && !isNaN(coordFirst) ? Math.max(0, coordFirst) : 0;
    const xLast = coordLast !== null && !isNaN(coordLast) ? coordLast : width * 0.7;

    // Demand / Supply Zone Box
    if (levels.zone_top && levels.zone_bottom) {
      const yTop = candleSeries.priceToCoordinate(levels.zone_top);
      const yBot = candleSeries.priceToCoordinate(levels.zone_bottom);

      if (yTop !== null && yBot !== null && !isNaN(yTop) && !isNaN(yBot)) {
        const boxY = Math.min(yTop, yBot);
        const boxH = Math.max(Math.abs(yBot - yTop), 22);
        const zoneColor = direction === 'BUY' ? 'rgba(30, 58, 138, 0.35)' : 'rgba(127, 29, 29, 0.35)';

        ctx.fillStyle = zoneColor;
        ctx.fillRect(xStart, boxY, xLast - xStart, boxH);

        ctx.fillStyle = direction === 'BUY' ? '#94a3b8' : '#f87171';
        ctx.font = 'bold 11px "Plus Jakarta Sans", sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(
          `${levels.zone_label} ($${levels.zone_bottom.toFixed(2)} - $${levels.zone_top.toFixed(2)})`,
          (xStart + xLast) / 2,
          boxY + boxH / 2 + 4
        );
      }
    }

    // ── Shaded Harmonic Wings (Triangles X-A-B and B-C-D) + Vertex Badges ─────
    if (activeData && activeData.xabcd_points && activeData.xabcd_points.length === 5) {
      const pts = activeData.xabcd_points;
      const pCoords = pts.map((p) => ({
        x: timeScale.timeToCoordinate(p.time),
        y: candleSeries.priceToCoordinate(p.price),
        label: p.label
      }));

      if (pCoords.every((c) => c.x !== null && c.y !== null && !isNaN(c.x) && !isNaN(c.y))) {
        // Wing 1: Triangle X - A - B
        ctx.beginPath();
        ctx.moveTo(pCoords[0].x, pCoords[0].y);
        ctx.lineTo(pCoords[1].x, pCoords[1].y);
        ctx.lineTo(pCoords[2].x, pCoords[2].y);
        ctx.closePath();
        ctx.fillStyle = 'rgba(245, 158, 11, 0.16)';
        ctx.fill();
        ctx.strokeStyle = '#f59e0b';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // Wing 2: Triangle B - C - D
        ctx.beginPath();
        ctx.moveTo(pCoords[2].x, pCoords[2].y);
        ctx.lineTo(pCoords[3].x, pCoords[3].y);
        ctx.lineTo(pCoords[4].x, pCoords[4].y);
        ctx.closePath();
        ctx.fillStyle = 'rgba(245, 158, 11, 0.16)';
        ctx.fill();
        ctx.strokeStyle = '#f59e0b';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // Draw High-Visibility Harmonic Point Badges (X, A, B, C, D)
        const labels = ['X', 'A', 'B', 'C', 'D'];
        pCoords.forEach((pt, idx) => {
          ctx.beginPath();
          ctx.arc(pt.x, pt.y, 11, 0, 2 * Math.PI);
          ctx.fillStyle = '#161d19';
          ctx.fill();
          ctx.strokeStyle = '#f59e0b';
          ctx.lineWidth = 2;
          ctx.stroke();

          ctx.fillStyle = '#ffffff';
          ctx.font = 'bold 11px "JetBrains Mono", monospace';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(labels[idx], pt.x, pt.y);
        });

        // Draw Fibonacci Ratio Labels on Leg Midpoints (Matching Harmonic Patterns.png)
        const fibRatios = [
          { p1: pCoords[0], p2: pCoords[2], text: '0.618' }, // X - B
          { p1: pCoords[1], p2: pCoords[3], text: '0.886' }, // A - C
          { p1: pCoords[2], p2: pCoords[4], text: '1.618' }, // B - D
          { p1: pCoords[0], p2: pCoords[4], text: '0.786' }, // X - D
        ];

        fibRatios.forEach((ratio) => {
          const midX = (ratio.p1.x + ratio.p2.x) / 2;
          const midY = (ratio.p1.y + ratio.p2.y) / 2;

          ctx.fillStyle = 'rgba(22, 29, 25, 0.85)';
          ctx.fillRect(midX - 16, midY - 8, 32, 16);
          ctx.strokeStyle = 'rgba(56, 189, 248, 0.4)';
          ctx.lineWidth = 1;
          ctx.strokeRect(midX - 16, midY - 8, 32, 16);

          ctx.fillStyle = '#38bdf8';
          ctx.font = 'bold 9px "JetBrains Mono", monospace';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(ratio.text, midX, midY);
        });
      }
    }
  };

  useEffect(() => {
    if (!chartContainerRef.current || !activeData) return;

    chartContainerRef.current.innerHTML = '';

    try {
      const containerWidth = chartContainerRef.current.clientWidth || 800;

      const chart = createChart(chartContainerRef.current, {
        width: containerWidth,
        height: 500,
        layout: {
          background: { color: '#0d111c' },
          textColor: '#94a3b8',
          fontFamily: "'Plus Jakarta Sans', sans-serif",
        },
        grid: {
          vertLines: { color: 'rgba(30, 41, 59, 0.35)' },
          horzLines: { color: 'rgba(30, 41, 59, 0.35)' },
        },
        crosshair: {
          mode: 0,
          vertLine: { color: 'rgba(251, 191, 36, 0.40)', width: 1, style: LineStyle.Dashed },
          horzLine: { color: 'rgba(251, 191, 36, 0.40)', width: 1, style: LineStyle.Dashed },
        },
        rightPriceScale: {
          borderColor: 'rgba(51, 65, 85, 0.6)',
          scaleMargins: { top: 0.12, bottom: 0.12 },
          autoScale: true,
          alignLabels: true,
        },
        timeScale: {
          borderColor: 'rgba(51, 65, 85, 0.6)',
          timeVisible: true,
          secondsVisible: false,
          rightOffset: 15,
          minBarSpacing: 6,
          maxBarSpacing: 25,
        },
      });

      chartInstanceRef.current = chart;

      // ── 1. Candlestick Series (OHLC) ──────────────────────────────────────
      const candleSeries = chart.addSeries(CandlestickSeries, {
        upColor: '#26a69a',
        downColor: '#ef5350',
        borderVisible: false,
        wickUpColor: '#26a69a',
        wickDownColor: '#ef5350',
      });

      const cleanCandles = sanitize(activeData.candles);
      if (cleanCandles.length > 0) {
        candleSeries.setData(cleanCandles);
      }

      const levels = activeData.levels || {};
      const direction = activeData.direction || 'BUY';

      // ── 2. XABCD Harmonic Line Series (Solid Amber Line) ──────────────────
      try {
        const cleanXabcd = sanitize(activeData.xabcd_points);
        if (cleanXabcd.length > 1) {
          let interpolatedXabcd = [];
          for (let i = 0; i < cleanXabcd.length - 1; i++) {
            const seg = interpolateLineSeries(cleanXabcd[i], cleanXabcd[i + 1], cleanCandles);
            interpolatedXabcd = interpolatedXabcd.concat(seg);
          }
          const sanitizedXabcd = sanitize(interpolatedXabcd);

          if (sanitizedXabcd.length > 0) {
            const xabcdSeries = chart.addSeries(LineSeries, {
              color: '#f59e0b',
              lineWidth: 2,
              lineStyle: LineStyle.Solid,
              crosshairMarkerVisible: false,
              lastValueVisible: false,
              priceLineVisible: false,
            });
            xabcdSeries.setData(sanitizedXabcd);
          }
        }
      } catch (errXabcd) {
        console.error('Error drawing XABCD series:', errXabcd);
      }

      // ── 3. Diagonal Fibonacci Lines (X-C, A-D) ───────────────────────────
      try {
        const fibLines = activeData.fib_lines || [];
        fibLines.forEach((fib) => {
          if (!fib.points || fib.points.length < 2) return;
          const interpFib = interpolateLineSeries(fib.points[0], fib.points[1], cleanCandles);
          const cleanInterpFib = sanitize(interpFib);
          if (cleanInterpFib.length < 2) return;

          const fibSeries = chart.addSeries(LineSeries, {
            color: fib.color || '#38bdf8',
            lineWidth: 1.5,
            lineStyle: LineStyle.Dashed,
            crosshairMarkerVisible: false,
            lastValueVisible: false,
            priceLineVisible: false,
          });
          fibSeries.setData(cleanInterpFib);
        });
      } catch (errFib) {
        console.error('Error drawing Fib series:', errFib);
      }

      // ── 4. Extended Monte Carlo P50 Curve (Cyan Blue Dashed Line) ─────────
      try {
        const cleanMc = sanitize(activeData.monte_carlo_line);
        if (cleanMc.length > 1) {
          const mcData = cleanMc.map((p) => ({ time: p.time, value: p.price }));

          const mcSeries = chart.addSeries(LineSeries, {
            color: '#38bdf8',
            lineWidth: 3,
            lineStyle: LineStyle.Dashed,
            crosshairMarkerVisible: true,
            lastValueVisible: true,
            priceLineVisible: false,
            title: 'Monte P50',
          });
          mcSeries.setData(mcData);
        }
      } catch (errMc) {
        console.error('Error drawing Monte Carlo series:', errMc);
      }

      // ── 5. Right Price Scale Badges (Grouped & Non-Overlapping) ─────────
      try {
        const rawBadges = [
          { price: levels.prz_tp3, title: 'PRZ TP3', color: '#dc2626' },
          { price: levels.tp, title: 'TP', color: '#10b981' },
          { price: levels.monte_target, title: 'Monte', color: '#eab308' },
          { price: levels.prz_tp2, title: 'PRZ TP2', color: '#ef4444' },
          { price: levels.prz_tp1, title: 'PRZ TP1', color: '#dc2626' },
          { price: levels.entry, title: 'Entry', color: '#f59e0b' },
          { price: levels.prz_sl, title: 'PRZ SL', color: '#b91c1c' },
          { price: levels.sl, title: 'SL', color: '#ef4444' },
        ].filter((b) => typeof b.price === 'number' && !isNaN(b.price));

        // Group badges sharing exact or near price values to prevent text overlap
        const grouped = [];
        rawBadges.forEach((b) => {
          const existing = grouped.find((g) => Math.abs(g.price - b.price) < 0.2);
          if (existing) {
            if (!existing.titles.includes(b.title)) {
              existing.titles.push(b.title);
            }
          } else {
            grouped.push({ price: b.price, titles: [b.title], color: b.color });
          }
        });

        grouped.forEach((g) => {
          candleSeries.createPriceLine({
            price: g.price,
            color: g.color,
            lineWidth: 1.5,
            lineStyle: LineStyle.Dashed,
            axisLabelVisible: true,
            title: g.titles.join(' / '),
          });
        });
      } catch (errBadges) {
        console.error('Error creating price lines:', errBadges);
      }

      // ── 6. Initial Viewport Zoom (Last 60 Bars to End of Chart) ─────────
      if (cleanCandles.length > 0) {
        const totalBars = cleanCandles.length;
        chart.timeScale().setVisibleLogicalRange({
          from: Math.max(0, totalBars - 60),
          to: totalBars + 5,
        });
      }

      // ── 7. Draw Overlay Canvas on TimeScale Changes & Window Resize ───────
      const syncOverlay = () => updateOverlayCanvas(chart, candleSeries, levels, direction, cleanCandles);

      chart.timeScale().subscribeVisibleLogicalRangeChange(syncOverlay);

      syncOverlay();
      requestAnimationFrame(syncOverlay);
      setTimeout(syncOverlay, 150);

      const handleResize = () => {
        if (chartContainerRef.current && chart) {
          chart.applyOptions({ width: chartContainerRef.current.clientWidth });
          syncOverlay();
        }
      };
      window.addEventListener('resize', handleResize);

      return () => {
        window.removeEventListener('resize', handleResize);
        chart.remove();
      };
    } catch (errChart) {
      console.error('Error initializing Lightweight Chart:', errChart);
    }
  }, [activeData]);

  return (
    <div style={{ position: 'relative', width: '100%', height: '500px', background: '#0d111c', borderRadius: '6px', overflow: 'hidden' }}>
      {isLoading && !activeData && (
        <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#4edea3', zIndex: 10, background: '#0d111c', fontSize: '0.85rem' }}>
          ⚡ RENDERING QUANT REAL-TIME CANVAS...
        </div>
      )}
      <div ref={chartContainerRef} style={{ width: '100%', height: '100%' }} />
      <canvas
        ref={overlayCanvasRef}
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          pointerEvents: 'none',
          zIndex: 5,
        }}
      />
    </div>
  );
}
