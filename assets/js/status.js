const SERVERS = ["minecraft","cs2","arma"];
async function updateStatus(name) {
  const el = document.getElementById(`status-${name}`);
  try {
    const res = await fetch(`/api/status/${name}`);
    const jsn = await res.json();
    el.innerHTML = jsn.online
      ? `<span class="badge bg-success">Online</span> ${jsn.players||0}/${jsn.max_players||0}`
      : `<span class="badge bg-danger">Offline</span>`;
  } catch {
    el.textContent = 'Error';
  }
}
function refreshAll() { SERVERS.forEach(updateStatus); }
refreshAll(); setInterval(refreshAll,30000);
