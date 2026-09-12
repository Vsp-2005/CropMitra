import React from 'react';

export default function Footer() {
  return (
    <footer className="footer no-print">
      <div className="app-container">
        <p style={{ fontWeight: 600, color: 'var(--color-primary)', marginBottom: '0.35rem' }}>
          CropMitra — Agricultural Decision-Support System
        </p>
        <p style={{ fontSize: '0.85rem' }}>
          Empowering farmers with data-driven crop recommendations & balanced fertilizer planning.
        </p>
      </div>
    </footer>
  );
}
