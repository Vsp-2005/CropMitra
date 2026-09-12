import React from 'react';
import { ArrowRight, BookOpen, Sparkles, MapPin, Cpu, FlaskConical } from 'lucide-react';

export default function Home({ onGetStarted, onLearnMore }) {
  return (
    <div className="hero-section">
      <div className="hero-tag">
        <Sparkles size={16} />
        <span>Field-tested agricultural intelligence</span>
      </div>

      <h1 className="hero-title">
        Better crop decisions, better farming.
      </h1>

      <p className="hero-desc">
        CropMitra helps you choose suitable crops based on your field conditions and location.
      </p>

      <div className="hero-cta-group">
        <button className="btn btn-primary btn-lg" onClick={onGetStarted}>
          <span>Get Recommendation</span>
          <ArrowRight size={18} />
        </button>
        <button className="btn btn-secondary btn-lg" onClick={onLearnMore}>
          <BookOpen size={18} />
          <span>Learn More</span>
        </button>
      </div>

      {/* 3-Step Visual Flow with Subtle Agricultural Accents */}
      <div className="hero-visual">
        <div className="visual-step step-green">
          <div className="step-num">
            <MapPin size={15} />
            <span>Step 1</span>
          </div>
          <div className="step-title">Location & Field Info</div>
          <p className="step-desc">
            Select your Indian state & district along with water, soil, and previous crop.
          </p>
        </div>

        <div className="visual-step step-amber-green">
          <div className="step-num">
            <Cpu size={15} />
            <span>Step 2</span>
          </div>
          <div className="step-title">ML & Rotation Scoring</div>
          <p className="step-desc">
            Random Forest model evaluates soil compatibility cross-verified with regional data.
          </p>
        </div>

        <div className="visual-step step-green">
          <div className="step-num">
            <FlaskConical size={15} />
            <span>Step 3</span>
          </div>
          <div className="step-title">Clear Plan & Fertilizer</div>
          <p className="step-desc">
            Explore ranked recommendations, suitability ratings, and tailored N-P-K nutrient dosage.
          </p>
        </div>
      </div>
    </div>
  );
}
