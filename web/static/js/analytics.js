async function loadMetrics() {
  const res = await fetch('/api/metrics');
  return await res.json();
}

function renderCharts(data) {
  const labels = Object.keys(data.by_agent || {});
  const counts = Object.values(data.by_agent || {});

  new Chart(document.getElementById('runsChart'), {
    type: 'bar',
    data: { labels, datasets: [{ label: 'Agent Çalıştırma Sayısı', data: counts, backgroundColor: '#2e8b57' }] }
  });

  new Chart(document.getElementById('tokensChart'), {
    type: 'doughnut',
    data: { labels: ['Toplam Token'], datasets: [{ label: 'Tokens', data: [data.total_tokens || 0], backgroundColor: ['#ff8fab'] }] }
  });

  new Chart(document.getElementById('latencyChart'), {
    type: 'line',
    data: {
      labels: ['Avg Latency'],
      datasets: [{ label: 'Saniye', data: [data.avg_latency || 0], borderColor: '#4f46e5', tension: 0.3 }]
    }
  });
}

loadMetrics().then(renderCharts);
