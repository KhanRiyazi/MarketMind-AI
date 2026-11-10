/* Chart.js helpers. One chart per canvas id; the old one is destroyed before redraw. */
const Charts = {
  _live: {},
  line(canvasId, labels, datasets) {
    this._live[canvasId]?.destroy();
    const css = getComputedStyle(document.documentElement);
    const grid = css.getPropertyValue("--line").trim(), text = css.getPropertyValue("--muted").trim();
    const palette = [css.getPropertyValue("--teal").trim(), css.getPropertyValue("--amber").trim(),
                     css.getPropertyValue("--muted").trim(), css.getPropertyValue("--loss").trim()];
    this._live[canvasId] = new Chart(document.getElementById(canvasId), {
      type: "line",
      data: { labels, datasets: datasets.map((d, i) => ({
        borderColor: palette[i % palette.length], backgroundColor: "transparent", borderWidth: i === 0 ? 2 : 1.5,
        pointRadius: 0, tension: 0.15, spanGaps: true, borderDash: d.dash || [], ...d })) },
      options: { responsive: true, maintainAspectRatio: false, interaction: { mode: "index", intersect: false },
        plugins: { legend: { labels: { color: text, boxWidth: 12 } } },
        scales: { x: { ticks: { color: text, maxTicksLimit: 8 }, grid: { display: false } },
                  y: { ticks: { color: text }, grid: { color: grid } } } },
    });
  },
};
