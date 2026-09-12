import React from 'react';
import { AlertCircle, CheckCircle2, Database, Cpu, Leaf } from 'lucide-react';

export default function About() {
  return (
    <div style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div className="page-header">
        <h1 className="page-title">About CropMitra</h1>
        <p className="page-subtitle">
          Data-driven, explainable agricultural decision support designed for real farmers.
        </p>
      </div>

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.4rem', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Leaf size={22} color="var(--color-primary)" />
          <span>What is CropMitra?</span>
        </h2>
        <p style={{ marginBottom: '1rem', color: 'var(--color-text-main)' }}>
          CropMitra is an open agricultural decision-support web application. It simplifies field decision-making by matching a farmer's water availability, soil type, and previous crop with the most suitable crop and an optimal fertilizer schedule.
        </p>
        <p style={{ color: 'var(--color-text-muted)' }}>
          Instead of complex dashboards or black-box predictions, CropMitra focuses on a straightforward, transparent workflow: <strong>Simple Input → ML Recommendation → Clear Result → Fertilizer Guidance</strong>.
        </p>
      </div>

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.4rem', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Cpu size={22} color="var(--color-primary)" />
          <span>How It Works</span>
        </h2>
        <ul style={{ paddingLeft: '1.25rem', color: 'var(--color-text-main)', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <li>
            <strong>Agronomic Feature Synthesis:</strong> Your field inputs are mapped to validated soil characteristics (pH, nutrient absorption capacity) and moisture availability.
          </li>
          <li>
            <strong>Random Forest ML Model:</strong> A high-accuracy multi-class Random Forest model assesses suitability across 22 major crop classes.
          </li>
          <li>
            <strong>Crop Rotation Rule Layer:</strong> An agronomic rule engine applies rotation bonuses (e.g. legume nitrogen fixation) or flags monoculture risks before finalizing rankings.
          </li>
          <li>
            <strong>Fertilizer Plan & Application Guidance:</strong> Generates balanced N-P-K nutrient dosage and split-application schedules backed by agricultural standards.
          </li>
        </ul>
      </div>

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.4rem', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Database size={22} color="var(--color-primary)" />
          <span>Data Sources</span>
        </h2>
        <p style={{ color: 'var(--color-text-muted)', marginBottom: '0.5rem' }}>
          CropMitra is trained and calibrated against curated agricultural datasets containing verified field soil observations, climate parameters (temperature, rainfall, humidity, pH), and standard fertilizer nutrient matrices.
        </p>
      </div>

      {/* Important Limitation Disclaimer */}
      <div className="disclaimer-box" style={{ padding: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 700, marginBottom: '0.35rem', fontSize: '1rem' }}>
          <AlertCircle size={20} />
          <span>Important Limitation & Advisory</span>
        </div>
        <p style={{ color: '#92400e', fontSize: '0.95rem' }}>
          CropMitra is a decision-support tool and should not replace advice from qualified agricultural professionals or local agricultural authorities.
        </p>
      </div>
    </div>
  );
}
