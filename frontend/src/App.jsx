import React from 'react';
import ChatWindow from './components/ChatWindow';

export default function App() {
  return (
    <div style={styles.appBg}>
      <div style={styles.headerWrap}>
        <h1 style={styles.title}>
          <span style={styles.logoDot} /> CollinAI Bot
        </h1>
      </div>
      <div style={styles.container}>
        <ChatWindow />
      </div>
    </div>
  );
}

const styles = {
  appBg: {
    minHeight: '100vh',
    background:
      'radial-gradient(1200px 600px at 20% -10%, #e8f3ff 0%, transparent 60%), radial-gradient(800px 400px at 100% 0%, #ffe9f2 0%, transparent 55%), linear-gradient(180deg, #f7f9fc, #ffffff)',
    padding: '40px 16px',
  },
  headerWrap: {
    textAlign: 'center',
    marginBottom: 16,
  },
  title: {
    margin: 0,
    fontSize: 28,
    fontWeight: 800,
    letterSpacing: 0.2,
    color: '#0f172a',
  },
  logoDot: {
    display: 'inline-block',
    width: 10,
    height: 10,
    background:
      'linear-gradient(135deg, #6366f1 0%, #22d3ee 100%)',
    borderRadius: '999px',
    marginRight: 10,
    verticalAlign: 'middle',
    boxShadow: '0 0 0 3px rgba(99,102,241,0.15)',
  },
  subtitle: {
    marginTop: 8,
    color: '#475569',
  },
  container: {
    maxWidth: 860,
    margin: '0 auto',
  },
};