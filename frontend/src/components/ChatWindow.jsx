import React, { useEffect, useMemo, useRef, useState } from 'react';
import { sendMessage } from '../api';
import { api } from '../api'; // assuming you already have this

export default function ChatWindow() {
  const [messages, setMessages] = useState([]); // [{ from: 'user'|'bot', text, ts }]
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [session, setSession] = useState(null); // { session_id: '...' }
  const listRef = useRef(null);
  const typingRef = useRef(null);

  // Fetch session id once (fixes the top-level await issue)
  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const { data } = await api.get('/api/get_uuid');
        if (mounted) setSession(data);
      } catch (e) {
        console.error('Failed to fetch session id', e);
      }
    })();
    return () => { mounted = false; };
  }, []);

  // Auto scroll to bottom on new messages
  useEffect(() => {
    if (!listRef.current) return;
    listRef.current.scrollTo({
      top: listRef.current.scrollHeight,
      behavior: 'smooth',
    });
  }, [messages, loading]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || !session?.session_id || loading) return;

    const userMsg = { from: 'user', text, ts: Date.now() };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);
    setInput('');

    try {
      const response = await sendMessage(text, session.session_id);
      const botText =
        (response && (response.ai_answer || response.ai_message || response.reply?.ai_answer)) ||
        'Hmm… I could not parse a response.';
      setMessages((prev) => [...prev, { from: 'bot', text: botText, ts: Date.now() }]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        { from: 'bot', text: 'Error: could not fetch response.', ts: Date.now() },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const onKeyDown = (e) => {
    // Enter to send, Shift+Enter for newline
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const disabled = useMemo(
    () => loading || !session?.session_id || !input.trim(),
    [loading, session, input]
  );

  return (
    <div style={styles.card}>
      {/* Chat header */}
      <div style={styles.cardHeader}>
        <div style={styles.headerLeft}>
          <div style={styles.avatarBot}>🤖</div>
          <div>
            <div style={styles.headerTitle}>Collin</div>
            <div style={styles.headerSub}>
              {session?.session_id ? `Session: ${session.session_id.slice(0, 8)}…` : 'Connecting…'}
            </div>
          </div>
        </div>
        <div style={styles.headerRight}>
          <StatusPill ok={!!session?.session_id} />
        </div>
      </div>

      {/* Messages */}
      <div style={styles.listWrap} ref={listRef}>
        {messages.length === 0 && !loading && (
          <EmptyState />
        )}

        {messages.map((m, i) => (
          <MessageBubble key={i} from={m.from} text={m.text} ts={m.ts} />
        ))}

        {loading && (
          <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginTop: 8 }} ref={typingRef}>
            <div style={styles.avatarBotSm}>🤖</div>
            <TypingDots />
          </div>
        )}
      </div>

      {/* Input */}
      <div style={styles.inputBar}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKeyDown}
          rows={1}
          placeholder={session?.session_id ? 'Type your message…' : 'Setting up session…'}
          style={styles.textarea}
        />
        <button
          onClick={handleSend}
          disabled={disabled}
          style={{ ...styles.sendBtn, ...(disabled ? styles.sendBtnDisabled : {}) }}
          title={!session?.session_id ? 'Waiting for session…' : 'Send'}
        >
          {loading ? <Spinner /> : 'Send'}
        </button>
      </div>
    </div>
  );
}

/** Subcomponents **/

function MessageBubble({ from, text, ts }) {
  const isUser = from === 'user';
  return (
    <div
      style={{
        display: 'flex',
        gap: 10,
        margin: '10px 0',
        flexDirection: isUser ? 'row-reverse' : 'row',
        alignItems: 'flex-end',
      }}
    >
      <div style={isUser ? styles.avatarUser : styles.avatarBotSm}>
        {isUser ? '🧑' : '🤖'}
      </div>
      <div style={{ maxWidth: '80%' }}>
        <div
          style={{
            ...styles.bubble,
            ...(isUser ? styles.bubbleUser : styles.bubbleBot),
          }}
        >
          {text}
        </div>
        <div style={styles.timestamp}>
          {new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div style={styles.empty}>
      <div style={styles.emptyIcon}>💬</div>
      <div style={styles.emptyTitle}>Start the conversation</div>
      <div style={styles.emptySub}>
        Ask anything—press <kbd style={styles.kbd}>Enter</kbd> to send,
        <span style={{ margin: '0 6px' }} />
        <kbd style={styles.kbd}>Shift</kbd> + <kbd style={styles.kbd}>Enter</kbd> for a new line.
      </div>
    </div>
  );
}

function TypingDots() {
  return (
    <div style={styles.typing}>
      <span style={{ ...styles.dot, animationDelay: '0ms' }} />
      <span style={{ ...styles.dot, animationDelay: '150ms' }} />
      <span style={{ ...styles.dot, animationDelay: '300ms' }} />
    </div>
  );
}

function Spinner() {
  return <span style={styles.spinner} />;
}

function StatusPill({ ok }) {
  return (
    <div style={{ ...styles.statusPill, background: ok ? '#e7f9ef' : '#fff5f5', color: ok ? '#0a8a4a' : '#b42318' }}>
      <span style={{ ...styles.statusDot, background: ok ? '#12b76a' : '#f04438' }} />
      {ok ? 'Connected' : 'Offline'}
    </div>
  );
}

/** Styles **/

const styles = {
  card: {
    background: '#ffffff',
    borderRadius: 16,
    boxShadow:
      '0 10px 30px rgba(2,6,23,0.08), inset 0 0 0 1px rgba(15,23,42,0.06)',
    overflow: 'hidden',
  },
  cardHeader: {
    padding: '14px 16px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    background:
      'linear-gradient(180deg, rgba(99,102,241,0.08), rgba(99,102,241,0.0))',
    borderBottom: '1px solid rgba(15,23,42,0.06)',
  },
  headerLeft: { display: 'flex', gap: 12, alignItems: 'center' },
  headerTitle: { fontWeight: 700, color: '#0f172a' },
  headerSub: { fontSize: 12, color: '#64748b' },
  headerRight: {},
  avatarBot: {
    width: 36,
    height: 36,
    borderRadius: 12,
    display: 'grid',
    placeItems: 'center',
    background:
      'linear-gradient(135deg, #eef2ff, #cffafe)',
    border: '1px solid rgba(15,23,42,0.06)',
  },
  avatarBotSm: {
    width: 28,
    height: 28,
    borderRadius: 10,
    display: 'grid',
    placeItems: 'center',
    background: '#eef2ff',
    border: '1px solid rgba(15,23,42,0.06)',
    fontSize: 16,
  },
  avatarUser: {
    width: 28,
    height: 28,
    borderRadius: 10,
    display: 'grid',
    placeItems: 'center',
    background: '#ecfeff',
    border: '1px solid rgba(15,23,42,0.06)',
    fontSize: 16,
  },
  listWrap: {
    height: 480,
    overflowY: 'auto',
    padding: '16px 16px',
    background:
      'linear-gradient(180deg, #fafafc, #ffffff)',
  },
  bubble: {
    padding: '10px 12px',
    borderRadius: 14,
    border: '1px solid rgba(15,23,42,0.06)',
    lineHeight: 1.45,
    whiteSpace: 'pre-wrap',
    wordBreak: 'break-word',
    boxShadow: '0 1px 0 rgba(2,6,23,0.03)',
    fontSize: 15,
  },
  bubbleUser: {
    background:
      'linear-gradient(180deg, #ecfeff, #ffffff)',
  },
  bubbleBot: {
    background:
      'linear-gradient(180deg, #eef2ff, #ffffff)',
  },
  timestamp: {
    fontSize: 11,
    color: '#94a3b8',
    marginTop: 6,
    textAlign: 'left',
  },
  inputBar: {
    display: 'flex',
    gap: 8,
    padding: 12,
    borderTop: '1px solid rgba(15,23,42,0.06)',
    background: 'rgba(248,250,252,0.7)',
    backdropFilter: 'saturate(180%) blur(6px)',
  },
  textarea: {
    flex: 1,
    resize: 'none',
    padding: '12px 14px',
    borderRadius: 12,
    border: '1px solid rgba(15,23,42,0.08)',
    outline: 'none',
    fontFamily: 'inherit',
    fontSize: 15,
    lineHeight: 1.4,
    background: '#ffffff',
    boxShadow: '0 1px 0 rgba(2,6,23,0.03) inset',
  },
  sendBtn: {
    padding: '0 16px',
    minWidth: 92,
    borderRadius: 12,
    border: '1px solid rgba(15,23,42,0.08)',
    background:
      'linear-gradient(135deg, #6366f1, #22d3ee)',
    color: '#fff',
    fontWeight: 700,
    fontSize: 14,
    cursor: 'pointer',
    boxShadow: '0 6px 16px rgba(34,211,238,0.25)',
    transition: 'transform 120ms ease, filter 120ms ease',
  },
  sendBtnDisabled: {
    filter: 'grayscale(0.4) brightness(0.9)',
    cursor: 'not-allowed',
  },
  typing: {
    display: 'inline-flex',
    gap: 6,
    alignItems: 'center',
    padding: '8px 10px',
    borderRadius: 12,
    border: '1px dashed rgba(15,23,42,0.1)',
  },
  dot: {
    width: 6,
    height: 6,
    borderRadius: 999,
    background: '#475569',
    display: 'inline-block',
    animation: 'typing 1s infinite ease-in-out',
  },
  spinner: {
    width: 16,
    height: 16,
    border: '2px solid rgba(255,255,255,0.6)',
    borderTopColor: '#ffffff',
    borderRadius: '50%',
    display: 'inline-block',
    animation: 'spin 0.8s linear infinite',
  },
  empty: {
    textAlign: 'center',
    color: '#475569',
    marginTop: 48,
  },
  emptyIcon: {
    fontSize: 28,
    marginBottom: 8,
  },
  emptyTitle: { fontWeight: 700, color: '#0f172a' },
  emptySub: { marginTop: 6, fontSize: 14 },
  kbd: {
    background: '#f1f5f9',
    border: '1px solid #e2e8f0',
    borderRadius: 6,
    padding: '2px 6px',
    fontFamily: 'ui-monospace, SFMono-Regular, Menlo, monospace',
    fontSize: 12,
  },
  suggestList: {
    margin: '14px auto 0',
    padding: 0,
    listStyle: 'none',
    maxWidth: 520,
    display: 'grid',
    gap: 6,
  },
  suggest: {
    background: '#f8fafc',
    border: '1px solid rgba(15,23,42,0.06)',
    padding: '8px 10px',
    borderRadius: 8,
    fontSize: 14,
  },
  statusPill: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 6,
    borderRadius: 999,
    padding: '6px 10px',
    fontSize: 12,
    fontWeight: 600,
    border: '1px solid rgba(15,23,42,0.06)',
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 999,
    display: 'inline-block',
    boxShadow: '0 0 0 3px rgba(16,185,129,0.10)',
  },
};

/* Keyframe styles injected once via a style tag */
const styleTagId = '__chatwindow_keyframes__';
if (typeof document !== 'undefined' && !document.getElementById(styleTagId)) {
  const style = document.createElement('style');
  style.id = styleTagId;
  style.textContent = `
@keyframes typing {
  0%, 80%, 100% { transform: translateY(0); opacity: .4; }
  40% { transform: translateY(-3px); opacity: 1; }
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
`;
  document.head.appendChild(style);
}