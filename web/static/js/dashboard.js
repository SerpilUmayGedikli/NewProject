const DEFAULT_AGENTS = [
  { id: 'claude', name: 'Claude', role: 'Analyst' },
  { id: 'chatgpt', name: 'ChatGPT', role: 'Generalist' },
  { id: 'gemini', name: 'Gemini', role: 'Researcher' }
];

const agentColumn = document.getElementById('agentColumn');
const statusBox = document.getElementById('statusBox');
const startBtn = document.getElementById('startBtn');
const newChatBtn = document.getElementById('newChatBtn');
const chatStack = document.getElementById('chatStack');

function renderAgents(statusMap = {}) {
  agentColumn.innerHTML = '';
  DEFAULT_AGENTS.forEach((a) => {
    const s = statusMap[a.id]?.status || 'idle';
    const out = statusMap[a.id]?.last_output || '-';
    const el = document.createElement('div');
    el.className = 'agent';
    el.innerHTML = `<strong>${a.name}</strong> · ${a.role}<br/>Durum: <b>${s}</b><br/>Son çıktı: ${out}`;
    agentColumn.appendChild(el);
  });
}

async function chatAction(chatId, endpoint) {
  await fetch(endpoint, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ chat_id: chatId })
  });
  await refreshChats();
}

function renderChats(chats = []) {
  chatStack.innerHTML = '';
  chats.forEach((chat) => {
    const card = document.createElement('div');
    card.className = 'chat-card';
    const messages = (chat.messages || []).map((m) => {
      const cls = m.sender === 'user' ? 'msg-user' : 'msg-agent';
      return `<div class="msg ${cls}"><b>${m.sender}:</b> ${m.text}</div>`;
    }).join('');

    card.innerHTML = `
      <div class="chat-head">
        <span>${chat.title} (${chat.agent_id})</span>
        <span>Durum: ${chat.status} · Token: ${chat.tokens_total || 0}</span>
      </div>
      <div class="chat-messages">${messages || '<i>Mesaj yok</i>'}</div>
      <div class="chat-controls">
        <button data-pause="${chat.chat_id}">Duraklat</button>
        <button data-resume="${chat.chat_id}">Devam Et</button>
        <button data-delete="${chat.chat_id}" class="danger">Sil</button>
      </div>
      <div class="chat-actions">
        <input placeholder="Bu sohbet için mesaj yaz" data-chat-input="${chat.chat_id}" />
        <button data-send-chat="${chat.chat_id}">Gönder</button>
      </div>
    `;
    chatStack.appendChild(card);
  });

  document.querySelectorAll('[data-send-chat]').forEach((btn) => {
    btn.onclick = async () => {
      const chatId = btn.getAttribute('data-send-chat');
      const input = document.querySelector(`[data-chat-input="${chatId}"]`);
      const message = input.value.trim();
      if (!message) return;
      const res = await fetch('/api/chats/message', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ chat_id: chatId, message })
      });
      if (!res.ok) alert('Sohbet duraklatılmış olabilir.');
      input.value = '';
      await refreshChats();
    };
  });

  document.querySelectorAll('[data-pause]').forEach((btn) => {
    btn.onclick = () => chatAction(btn.getAttribute('data-pause'), '/api/chats/pause');
  });
  document.querySelectorAll('[data-resume]').forEach((btn) => {
    btn.onclick = () => chatAction(btn.getAttribute('data-resume'), '/api/chats/resume');
  });
  document.querySelectorAll('[data-delete]').forEach((btn) => {
    btn.onclick = () => chatAction(btn.getAttribute('data-delete'), '/api/chats/delete');
  });
}

async function refreshStatus() {
  const res = await fetch('/api/agents/status');
  const data = await res.json();
  renderAgents(data);
  statusBox.textContent = JSON.stringify(data, null, 2);
}

async function refreshChats() {
  const res = await fetch('/api/chats');
  const data = await res.json();
  renderChats(data);
}

startBtn.addEventListener('click', async () => {
  const prompt = document.getElementById('prompt').value;
  await fetch('/api/agents/start', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ prompt, agents: DEFAULT_AGENTS })
  });
  await refreshStatus();
});

newChatBtn.addEventListener('click', async () => {
  const agent_id = document.getElementById('agentSelect').value;
  const title = document.getElementById('chatTitle').value || `${agent_id} sohbeti`;
  await fetch('/api/chats/start', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ agent_id, title })
  });
  document.getElementById('chatTitle').value = '';
  await refreshChats();
});

renderAgents();
refreshChats();
setInterval(refreshStatus, 1500);
setInterval(refreshChats, 1500);
