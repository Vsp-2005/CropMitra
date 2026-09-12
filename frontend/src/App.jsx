import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Home from './pages/Home';
import CropAdvisor from './pages/CropAdvisor';
import FarmingGuides from './pages/FarmingGuides';
import About from './pages/About';

export default function App() {
  const [activePage, setActivePage] = useState('home');
  
  // Theme state: 'light' | 'dark'
  const [theme, setTheme] = useState(() => {
    const saved = localStorage.getItem('cropmitra_theme');
    if (saved === 'light' || saved === 'dark') {
      return saved;
    }
    // Fallback to system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    return 'light';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('cropmitra_theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => (prev === 'dark' ? 'light' : 'dark'));
  };

  return (
    <div className="app-layout">
      <Navbar 
        activePage={activePage} 
        setActivePage={setActivePage}
        theme={theme}
        toggleTheme={toggleTheme}
      />

      <main className="main-content">
        <div className="app-container">
          {activePage === 'home' && (
            <Home 
              onGetStarted={() => setActivePage('advisor')} 
              onLearnMore={() => setActivePage('about')} 
            />
          )}

          {activePage === 'advisor' && (
            <CropAdvisor />
          )}

          {activePage === 'guides' && (
            <FarmingGuides />
          )}

          {activePage === 'about' && (
            <About />
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}
