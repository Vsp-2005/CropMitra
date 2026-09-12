import React, { useState } from 'react';
import { Sprout, Menu, X, Sun, Moon } from 'lucide-react';

export default function Navbar({ activePage, setActivePage, theme, toggleTheme }) {
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleNavigate = (page) => {
    setActivePage(page);
    setMobileOpen(false);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <nav className="navbar">
      <div className="app-container nav-inner">
        {/* Brand Logo */}
        <div className="brand-logo" onClick={() => handleNavigate('home')}>
          <div className="brand-icon">
            <Sprout size={20} />
          </div>
          <span>CropMitra</span>
        </div>

        {/* Desktop Navigation Links & Theme Toggle */}
        <ul className="nav-links">
          <li>
            <span
              className={`nav-link ${activePage === 'home' ? 'active' : ''}`}
              onClick={() => handleNavigate('home')}
            >
              Home
            </span>
          </li>
          <li>
            <span
              className={`nav-link ${activePage === 'advisor' ? 'active' : ''}`}
              onClick={() => handleNavigate('advisor')}
            >
              Crop Advisor
            </span>
          </li>
          <li>
            <span
              className={`nav-link ${activePage === 'guides' ? 'active' : ''}`}
              onClick={() => handleNavigate('guides')}
            >
              Farming Guides
            </span>
          </li>
          <li>
            <span
              className={`nav-link ${activePage === 'about' ? 'active' : ''}`}
              onClick={() => handleNavigate('about')}
            >
              About
            </span>
          </li>
          <li style={{ display: 'flex', alignItems: 'center' }}>
            <button
              className="theme-toggle-btn"
              onClick={toggleTheme}
              aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
              title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
            >
              {theme === 'dark' ? <Sun size={19} /> : <Moon size={19} />}
            </button>
          </li>
        </ul>

        {/* Mobile Hamburger Button */}
        <div className="mobile-controls">
          <button
            className="mobile-menu-btn"
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label="Toggle menu"
          >
            {mobileOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      <div className={`mobile-nav ${mobileOpen ? 'open' : ''}`}>
        <ul className="mobile-nav-links">
          <li>
            <span
              className={`mobile-nav-link ${activePage === 'home' ? 'active' : ''}`}
              onClick={() => handleNavigate('home')}
            >
              Home
            </span>
          </li>
          <li>
            <span
              className={`mobile-nav-link ${activePage === 'advisor' ? 'active' : ''}`}
              onClick={() => handleNavigate('advisor')}
            >
              Crop Advisor
            </span>
          </li>
          <li>
            <span
              className={`mobile-nav-link ${activePage === 'guides' ? 'active' : ''}`}
              onClick={() => handleNavigate('guides')}
            >
              Farming Guides
            </span>
          </li>
          <li>
            <span
              className={`mobile-nav-link ${activePage === 'about' ? 'active' : ''}`}
              onClick={() => handleNavigate('about')}
            >
              About
            </span>
          </li>
          <li style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.65rem 0.5rem', borderTop: '1px solid var(--color-border)', marginTop: '0.5rem' }}>
            <span style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-text-muted)' }}>
              Theme ({theme === 'dark' ? 'Dark' : 'Light'})
            </span>
            <button
              className="theme-toggle-btn"
              onClick={toggleTheme}
              aria-label="Toggle theme"
            >
              {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
            </button>
          </li>
        </ul>
      </div>
    </nav>
  );
}
