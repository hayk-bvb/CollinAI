import React, { useState } from 'react';
import { sendMessage } from '../api';
import { api } from '../api'

export const getUUID = async () => {
  const response = await api.get('/api/get_uuid');
  return response.data;
}

const sessionID = await getUUID();
console.log(sessionID)

export default function ChatWindow() {
  const [messages, setMessages] = useState([]);  // [{ from: 'user'|'bot', text }]
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMsg = { from: 'user', text: input };
    setMessages([...messages, userMsg]);
    setLoading(true);

    try {
      const { reply } = await sendMessage(input, sessionID['session_id']);
      setMessages(msgs => [...msgs, { from: 'bot', text: reply }]);
    } catch (err) {
      console.error(err);
      setMessages(msgs => [...msgs, { from: 'bot', text: 'Error: could not fetch response.' }]);
    } finally {
      setLoading(false);
      setInput('');
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: 'auto' }}>
      <div style={{ border: '1px solid #ccc', padding: 10, height: 400, overflowY: 'auto' }}>
        {messages.map((m, i) => (
          <div key={i} style={{ textAlign: m.from === 'user' ? 'right' : 'left', margin: '8px 0' }}>
            <span
              style={{
                display: 'inline-block',
                padding: '8px 12px',
                borderRadius: 16,
                background: m.from === 'user' ? '#d1e7dd' : '#e2e3e5'
              }}
            >
              {m.text}
            </span>
          </div>
        ))}
        {loading && <div>Bot is typing…</div>}
      </div>

      <div style={{ display: 'flex', marginTop: 10 }}>
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSend()}
          style={{ flexGrow: 1, padding: 8 }}
          placeholder="Type your message…"
        />
        <button onClick={handleSend} disabled={loading || !input.trim()} style={{ marginLeft: 8 }}>
          Send
        </button>
      </div>
    </div>
  );
}