/**
 * Harmonic Pattern & Monte Carlo Quant Chart Drawer
 * Pure native coordinates { time, price } renderer for TradingView / Lightweight Charts.
 * Zero pixel math. Zero decorative lines. 100% mathematical precision.
 */

// 1. validateFibRatios(): Checks if ratio matches target range within configurable tolerance (3-5%)
export function validateFibRatios(patternName, ratios, tolerance = 0.05) {
  const specs = {
    Gartley:   { ab_xa: [0.618, 0.618], bc_ab: [0.382, 0.886], cd_bc: [1.272, 1.618], ad_xa: [0.786, 0.786] },
    Bat:       { ab_xa: [0.382, 0.500], bc_ab: [0.382, 0.886], cd_bc: [1.618, 2.618], ad_xa: [0.886, 0.886] },
    Butterfly: { ab_xa: [0.786, 0.786], bc_ab: [0.382, 0.886], cd_bc: [1.618, 2.618], ad_xa: [1.272, 1.618] },
    Crab:      { ab_xa: [0.382, 0.618], bc_ab: [0.382, 0.886], cd_bc: [2.618, 3.618], ad_xa: [1.618, 1.618] },
    "Deep Crab": { ab_xa: [0.886, 0.886], bc_ab: [0.382, 0.886], cd_bc: [2.000, 3.618], ad_xa: [1.618, 1.618] },
  };

  const spec = specs[patternName] || specs["Deep Crab"];
  for (const k in spec) {
    const val = ratios[k];
    if (val === undefined) continue;
    const minT = spec[k][0] * (1.0 - tolerance);
    const maxT = spec[k][1] * (1.0 + tolerance);
    if (val < minT || val > maxT) return false;
  }
  return true;
}

// 2. drawPattern(): Renders X-A-B-C-D pattern and diagonal Fibonacci lines natively
export function drawPattern(chart, xabcdPoints, fibLines, LineStyle) {
  if (!chart || !xabcdPoints || xabcdPoints.length !== 5) return [];

  const createdSeries = [];

  // Helper for line series with contiguous interpolation
  const addSeries = (data, color, lineStyle = LineStyle.Solid, lineWidth = 2) => {
    try {
      const series = chart.addLineSeries({
        color,
        lineWidth,
        lineStyle,
        priceLineVisible: false,
        lastValueVisible: false,
        crosshairMarkerVisible: false,
      });
      series.setData(data);
      createdSeries.push(series);
    } catch (e) {
      console.warn("Series render skip:", e);
    }
  };

  // Connect X-A, A-B, B-C, C-D
  for (let i = 0; i < 4; i++) {
    addSeries(
      [
        { time: xabcdPoints[i].time, price: xabcdPoints[i].price },
        { time: xabcdPoints[i + 1].time, price: xabcdPoints[i + 1].price },
      ],
      "#f59e0b",
      LineStyle.Solid,
      2
    );
  }

  // Draw Fibonacci Diagonal Lines (X-C, A-D, X-D)
  if (fibLines && Array.isArray(fibLines)) {
    fibLines.forEach((fib) => {
      if (fib.points && fib.points.length === 2) {
        addSeries(
          [
            { time: fib.points[0].time, price: fib.points[0].price },
            { time: fib.points[1].time, price: fib.points[1].price },
          ],
          fib.color || "#38bdf8",
          LineStyle.Dashed,
          1
        );
      }
    });
  }

  return createdSeries;
}

// 3. drawMonteCarloProjection(): Renders Monte Carlo P50 median curve into future bars
export function drawMonteCarloProjection(chart, monteCarloLine, LineStyle) {
  if (!chart || !monteCarloLine || monteCarloLine.length < 2) return null;

  try {
    const mcSeries = chart.addLineSeries({
      color: "#eab308",
      lineWidth: 3,
      lineStyle: LineStyle.Dashed,
      priceLineVisible: true,
      lastValueVisible: true,
      title: "Monte P50",
    });
    mcSeries.setData(monteCarloLine);
    return mcSeries;
  } catch (e) {
    console.warn("Monte Carlo render skip:", e);
    return null;
  }
}
