// Chatbot modal logic with accessibility, animations, API integration, and persistence
(function () {
  const openBtn = document.getElementById('cb-open-button');
  const dialog = document.getElementById('cb-dialog');
  const overlay = document.getElementById('cb-overlay');
  const closeBtn = document.getElementById('cb-close');
  const clearBtn = document.getElementById('cb-clear');
  const messagesEl = document.getElementById('cb-messages');
  const typingEl = document.getElementById('cb-typing');
  const formEl = document.getElementById('cb-form');
  const inputEl = document.getElementById('cb-input');

  const STORAGE_KEY = 'cb-history-v1';
  const FOCUSABLE_SELECTORS = 'a[href], area[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), button:not([disabled]), [tabindex]:not([tabindex="-1"])';
  let lastFocused = null;

  function restoreHistory() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return;
      const items = JSON.parse(raw);
      items.forEach(item => addMessage(item.text, item.user));
    } catch (e) {
      // ignore storage errors
    }
  }

  function persistMessage(text, user) {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      const items = raw ? JSON.parse(raw) : [];
      items.push({ text, user });
      localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
    } catch (e) {
      // ignore storage errors
    }
  }

  function clearHistory() {
    try { localStorage.removeItem(STORAGE_KEY); } catch (e) {}
    const nodes = messagesEl.querySelectorAll('.message');
    nodes.forEach((n, i) => { if (i > 0) n.remove(); });
    clearTyping();
  }

  function clearTyping() { typingEl.classList.remove('active'); typingEl.setAttribute('aria-hidden', 'true'); }
  function showTyping() { typingEl.classList.add('active'); typingEl.setAttribute('aria-hidden', 'false'); }

  function addMessage(text, isUser) {
    const msg = document.createElement('div');
    msg.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    msg.innerHTML = text;
    messagesEl.insertBefore(msg, typingEl);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function focusTrap(event) {
    if (!dialog.classList.contains('active')) return;
    if (event.key !== 'Tab') return;
    const focusables = dialog.querySelectorAll(FOCUSABLE_SELECTORS);
    if (!focusables.length) return;
    const first = focusables[0];
    const last = focusables[focusables.length - 1];
    const active = document.activeElement;
    if (event.shiftKey && active === first) { last.focus(); event.preventDefault(); }
    else if (!event.shiftKey && active === last) { first.focus(); event.preventDefault(); }
  }

  function openDialog() {
    lastFocused = document.activeElement;
    overlay.hidden = false;
    dialog.hidden = false;
    // force reflow to enable transition
    void dialog.offsetHeight;
    dialog.classList.add('active');
    dialog.focus();
    setTimeout(() => inputEl.focus(), 150);
    document.addEventListener('keydown', onKeyDown);
    document.addEventListener('keydown', focusTrap);
  }

  function closeDialog() {
    dialog.classList.remove('active');
    overlay.hidden = true;
    setTimeout(() => { dialog.hidden = true; }, 200);
    document.removeEventListener('keydown', onKeyDown);
    document.removeEventListener('keydown', focusTrap);
    if (lastFocused) lastFocused.focus();
  }

  function onKeyDown(e) {
    if (e.key === 'Escape') closeDialog();
  }

  async function sendToAPI(userText) {
    const payload = {
      messages: [
        { role: 'system', content: 'أنت مساعد افتراضي لموقع حجز القاعات. أجب باختصار وبالعربية.' },
        { role: 'user', content: userText }
      ]
    };
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || `HTTP ${res.status}`);
      }
      const data = await res.json();
      return data.text || 'تعذر الحصول على رد الآن.';
    } catch (err) {
      return `حدث خطأ: ${err.message}. حاول مرة أخرى لاحقًا.`;
    }
  }

  formEl.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = inputEl.value.trim();
    if (!text) return;
    addMessage(text, true);
    persistMessage(text, true);
    inputEl.value = '';
    showTyping();
    const reply = await sendToAPI(text);
    clearTyping();
    addMessage(reply, false);
    persistMessage(reply, false);
  });

  openBtn.addEventListener('click', openDialog);
  closeBtn.addEventListener('click', closeDialog);
  overlay.addEventListener('click', closeDialog);
  if (clearBtn) clearBtn.addEventListener('click', clearHistory);

  restoreHistory();
})();