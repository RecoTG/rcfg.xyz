
function stripPort(addr) {
  // strip port only for domain names, keep numeric IPs with port
  if (/[a-zA-Z]/.test(addr)) {
    const idx = addr.indexOf(':');
    if (idx !== -1) return addr.substring(0, idx);
  }
  return addr;
}
const SERVERS = [
  { key: 'minecraft',  label: 'Minecraft',         addr: 'mc.rcfg.xyz:25565' },
  { key: 'craftoria',  label: 'Modded Craftoria',  addr: 'mmc.rcfg.xyz:25580' },
  { key: 'cs2',        label: 'Counter-Strike 2',  addr: '135.181.19.52:27020', connectPrefix: 'connect ' },
  { key: 'arma',       label: 'Arma Reforger',     addr: '135.181.19.52:2302' }
];

async function fetchStatus(key) {
  try {
    const res = await fetch(`/api/status/${key}`);
    if (!res.ok) throw new Error();
    return await res.json();
  } catch {
    return { online: false, players: 0, max_players: 0 };
  }
}

document.addEventListener('DOMContentLoaded', async () => {
  let onlineCount = 0;
  for (const srv of SERVERS) {
    const status = await fetchStatus(srv.key);
    const btn = document.getElementById(`status-${srv.key}`).querySelector('button');
    btn.className = `btn btn-${status.online ? 'success' : 'danger'} btn-sm`;
    btn.innerText = status.online ? 'Online' : 'Offline';

    // update players
    const playersCell = document.getElementById(`players-${srv.key}`);
    playersCell.innerHTML = `
      <div class="d-flex align-items-center">
        <span class="me-2">${status.players}/${status.max_players}</span>
        <div class="progress flex-grow-1"><div class="progress-bar" style="width:${status.max_players?Math.round(status.players/status.max_players*100):0}%;"></div></div>
      </div>`;

    if (status.online) onlineCount++;

    // connect button already present, add handler
    const connectBtn = document.querySelector(`#row-${srv.key} .connect-btn`);
    connectBtn.addEventListener('click', () => {
      const value = connectBtn.getAttribute('data-ip');
      navigator.clipboard.writeText(value);
      connectBtn.innerText = 'Copied to Clipboard';
    });
  }
  document.getElementById('gs-summary').innerText = `${SERVERS.length} servers · ${onlineCount} online`;
});
