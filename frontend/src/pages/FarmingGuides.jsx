import React, { useState } from 'react';
import { BookOpen, X } from 'lucide-react';

const GUIDES = [
  {
    id: 'npk',
    title: 'Understanding Soil NPK',
    shortDesc: 'Learn the core macronutrients (Nitrogen, Phosphorus, Potassium) and how they influence leaf, root, and fruit growth.',
    content: (
      <div>
        <p><strong>Nitrogen (N):</strong> Fuel for vegetative development, stem elongation, and chlorophyll synthesis for leafy green growth.</p>
        <br />
        <p><strong>Phosphorus (P):</strong> Essential for root growth, early seedling vigor, flowering, and energy transfer (ATP).</p>
        <br />
        <p><strong>Potassium (K):</strong> Regulates water balance, stomatal conductance, disease resistance, and fruit/grain filling.</p>
      </div>
    )
  },
  {
    id: 'soils',
    title: 'Soil Types & Agricultural Management',
    shortDesc: 'Comparing sandy, clay, loamy, silty, peaty, and chalky soils and their water-nutrient retention dynamics.',
    content: (
      <div>
        <p><strong>Sandy Soil:</strong> Drains quickly, warm early, low nutrient retention. Benefits from split fertilizer applications and organic compost.</p>
        <br />
        <p><strong>Clay Soil:</strong> High nutrient and moisture holding capacity, slow drainage. Avoid working when wet to prevent soil compaction.</p>
        <br />
        <p><strong>Loamy Soil:</strong> Balanced proportion of sand, silt, and clay. Offers ideal drainage and aeration for maximum crop diversity.</p>
        <br />
        <p><strong>Silty & Peaty Soils:</strong> Fine-grained or highly organic, rich in nutrients but require careful pH and moisture monitoring.</p>
      </div>
    )
  },
  {
    id: 'rotation',
    title: 'Crop Rotation Principles',
    shortDesc: 'How alternating legumes with cereals breaks weed/pest lifecycles and restores nitrogen balance naturally.',
    content: (
      <div>
        <p><strong>Legume-Cereal Succession:</strong> Rotating pulses (chickpea, soybean, mungbean) before heavy nitrogen feeders (wheat, maize, rice) replenishes biological soil nitrogen.</p>
        <br />
        <p><strong>Pest & Disease Break:</strong> Continuous monoculture builds soil-borne pathogens. Rotating botanical families disrupts pest life cycles.</p>
        <br />
        <p><strong>Root Structure Diversification:</strong> Alternating shallow-rooted cereals with deep-taproot crops enhances overall soil structure and aeration.</p>
      </div>
    )
  },
  {
    id: 'fertilizer',
    title: 'Fertilizer Basics & Safe Application',
    shortDesc: 'Guidelines for basal dressing, top-dressing split doses, and avoiding volatilization/leaching losses.',
    content: (
      <div>
        <p><strong>Basal Application:</strong> Apply phosphorus and potassium at sowing time 3-5 cm below seed depth where young roots can reach them.</p>
        <br />
        <p><strong>Split Nitrogen Dosing:</strong> Divide urea/nitrogen into 2-3 installments during key growth stages to prevent leaching losses.</p>
        <br />
        <p><strong>Weather Timing:</strong> Avoid broadcasting fertilizer immediately before anticipated heavy downpours or during mid-day scorching sun.</p>
      </div>
    )
  },
  {
    id: 'water',
    title: 'Water & Irrigation Management',
    shortDesc: 'Matching crop water requirements with rainfall patterns and irrigation methods to prevent waterlogging and stress.',
    content: (
      <div>
        <p><strong>Critical Growth Stages:</strong> Ensure adequate soil moisture during flowering, tillering, and grain/fruit filling stages.</p>
        <br />
        <p><strong>Drainage:</strong> In heavy clay soils, ensure field drainage channels to prevent waterlogging and root asphyxiation.</p>
        <br />
        <p><strong>Drought-Tolerant Choices:</strong> In low-water regions, prioritize millets, pulses, and drought-hardy legumes over water-intensive paddy.</p>
      </div>
    )
  }
];

export default function FarmingGuides() {
  const [selectedGuide, setSelectedGuide] = useState(null);

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Farming Guides</h1>
        <p className="page-subtitle">
          Essential agronomic principles and best practices for healthy soil and sustainable yields.
        </p>
      </div>

      <div className="guides-grid">
        {GUIDES.map((guide) => (
          <div key={guide.id} className="guide-card">
            <div>
              <h3 className="guide-title">{guide.title}</h3>
              <p className="guide-desc">{guide.shortDesc}</p>
            </div>
            <button
              className="btn btn-secondary"
              onClick={() => setSelectedGuide(guide)}
            >
              <BookOpen size={16} />
              <span>Read Guide</span>
            </button>
          </div>
        ))}
      </div>

      {/* Simple Modal */}
      {selectedGuide && (
        <div className="modal-backdrop" onClick={() => setSelectedGuide(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 style={{ fontSize: '1.4rem', color: 'var(--color-primary)' }}>
                {selectedGuide.title}
              </h2>
              <button
                className="btn btn-secondary"
                style={{ padding: '0.4rem', border: 'none' }}
                onClick={() => setSelectedGuide(null)}
              >
                <X size={20} />
              </button>
            </div>
            <div className="modal-body">
              {selectedGuide.content}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
