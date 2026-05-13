// ── PRICE CHART ──
function renderPriceBars(prices, months) {
  const container = document.getElementById('price-bars');
  if (!container || !prices) return;
  const max = Math.max(...prices);
  container.innerHTML = '';
  prices.forEach((p, i) => {
    const pct = Math.round((p / max) * 150);
    const isPred = i === prices.length - 1;
    const wrap = document.createElement('div');
    wrap.className = 'bar-wrap';
    wrap.innerHTML = `
      <div style="font-size:0.6rem;color:var(--text-muted);height:16px;display:flex;align-items:center;">₹${p}</div>
      <div class="bar" style="height:${pct}px;background:${isPred ? 'var(--green-400)' : 'var(--green-100)'};"></div>
      <div class="bar-label">${months ? months[i] || '' : ''}</div>`;
    container.appendChild(wrap);
  });
}

// ── UPLOAD ZONE LABEL ──
document.addEventListener('DOMContentLoaded', function () {
  const fileInput = document.getElementById('disease-image');
  const uploadZone = document.getElementById('upload-zone');
  if (fileInput && uploadZone) {
    fileInput.addEventListener('change', function () {
      if (this.files && this.files[0]) {
        uploadZone.querySelector('p').innerHTML =
          `<strong>${this.files[0].name}</strong> selected — ready to analyze`;
      }
    });
  }

  // ── CHATBOT ──
  const chatInput = document.getElementById('chat-input');
  if (chatInput) {
    chatInput.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') sendChat();
    });
    // scroll to bottom on load
    const msgs = document.getElementById('chat-messages');
    if (msgs) msgs.scrollTop = msgs.scrollHeight;
  }

  // ── RENDER PRICE CHART IF DATA EXISTS ──
  const chartEl = document.getElementById('price-bars');
  if (chartEl && window.PRICE_DATA) {
    renderPriceBars(window.PRICE_DATA.prices, window.PRICE_DATA.months);
  }
});

// ── CHATBOT CLIENT SIDE ──
function appendMsg(text, role) {
  const container = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.className = `msg ${role}`;
  const isBot = role === 'bot';
  div.innerHTML = `
    <div class="msg-avatar ${isBot ? 'bot' : 'user-av'}">${isBot ? 'KM' : 'You'}</div>
    <div class="msg-bubble">${text}</div>`;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return div;
}

function sendChat() {
  const input = document.getElementById('chat-input');
  const msg = input.value.trim();
  if (!msg) return;
  input.value = '';
  appendMsg(msg, 'user');

  const typing = appendMsg('<div class="typing"><span></span><span></span><span></span></div>', 'bot');

  fetch('/chatbot/ask/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken'),
    },
    body: JSON.stringify({ message: msg }),
  })
    .then(r => r.json())
    .then(data => {
      typing.querySelector('.msg-bubble').textContent = data.reply || 'Sorry, I could not process that.';
      document.getElementById('chat-messages').scrollTop = 9999;
    })
    .catch(() => {
      typing.querySelector('.msg-bubble').textContent = 'Connection error. Please try again.';
    });
}

function sendChip(text) {
  document.getElementById('chat-input').value = text;
  sendChat();
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    document.cookie.split(';').forEach(cookie => {
      const c = cookie.trim();
      if (c.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(c.slice(name.length + 1));
      }
    });
  }
  return cookieValue;
}