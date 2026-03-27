const logsBox = document.getElementById('logsBox');

async function loadLogs() {
  const res = await fetch('/api/logs');
  const data = await res.json();
  logsBox.textContent = JSON.stringify(data.slice(-50), null, 2);
}

loadLogs();
setInterval(loadLogs, 2000);
