import React, { useState, useEffect, useMemo } from 'react';
import { 
  Sprout, 
  Droplets, 
  Layers, 
  RotateCcw, 
  Printer, 
  ArrowRight, 
  ArrowLeft, 
  CheckCircle2, 
  AlertCircle,
  FlaskConical,
  Bookmark,
  Calendar,
  Sparkles,
  MapPin,
  Info,
  Check,
  ShieldCheck
} from 'lucide-react';
import { api } from '../services/api';

const WATER_OPTIONS = [
  { id: 'low', label: 'Low', desc: 'Arid / Rain-fed dry' },
  { id: 'medium', label: 'Medium', desc: 'Moderate / Standard canal' },
  { id: 'high', label: 'High', desc: 'High rainfall / Wetland' }
];

const SOIL_OPTIONS = [
  { id: 'sandy', label: 'Sandy' },
  { id: 'clay', label: 'Clay' },
  { id: 'loamy', label: 'Loamy' },
  { id: 'silty', label: 'Silty' },
  { id: 'peaty', label: 'Peaty' },
  { id: 'chalky', label: 'Chalky' }
];

export default function CropAdvisor() {
  // Navigation states: 'form' | 'loading' | 'crop_result' | 'fert_result'
  const [viewState, setViewState] = useState('form');
  
  // Location States - NO PRESELECTED VALUES (empty initially)
  const [statesList, setStatesList] = useState([]);
  const [districtsList, setDistrictsList] = useState([]);
  const [selectedState, setSelectedState] = useState('');
  const [selectedDistrict, setSelectedDistrict] = useState('');

  // Regional crops for selected location
  const [regionalCrops, setRegionalCrops] = useState([]);
  const [loadingRegionalCrops, setLoadingRegionalCrops] = useState(false);

  // Field Condition States - NO PRESELECTED VALUES (empty initially)
  const [waterAvailability, setWaterAvailability] = useState('');
  const [soilType, setSoilType] = useState('');
  const [previousCrop, setPreviousCrop] = useState('');
  const [cropList, setCropList] = useState([]);

  // Validation & Error States
  const [fieldErrors, setFieldErrors] = useState({});
  const [errorMsg, setErrorMsg] = useState(null);

  // Result data
  const [locationMeta, setLocationMeta] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [selectedCropIndex, setSelectedCropIndex] = useState(0);
  const [fertResult, setFertResult] = useState(null);
  const [saveStatus, setSaveStatus] = useState(null); // null | 'saved' | 'error'

  // Load States list on mount (do not select anything automatically)
  useEffect(() => {
    async function loadStates() {
      try {
        const states = await api.getStates();
        setStatesList(states);
      } catch (err) {
        console.error('Error fetching states:', err);
      }
    }
    loadStates();
  }, []);

  // Load Districts whenever selectedState changes
  useEffect(() => {
    async function loadDistricts() {
      if (!selectedState) {
        setDistrictsList([]);
        setSelectedDistrict('');
        setRegionalCrops([]);
        return;
      }
      try {
        const districts = await api.getDistricts(selectedState);
        setDistrictsList(districts);
        setSelectedDistrict(''); // reset district selection when state changes
        setRegionalCrops([]);
      } catch (err) {
        console.error('Error fetching districts:', err);
      }
    }
    loadDistricts();
  }, [selectedState]);

  // Load generic crop options for previous crop selector (do not select anything automatically)
  useEffect(() => {
    async function loadCrops() {
      try {
        const crops = await api.getCrops();
        setCropList(crops);
      } catch (err) {
        console.error('Error fetching crops:', err);
      }
    }
    loadCrops();
  }, []);

  // Compute other crops dynamically: All Available Crops - Regional Crops = Other Crops
  const otherCrops = useMemo(() => {
    const regionalLower = new Set(regionalCrops.map(c => c.toLowerCase().trim()));
    return cropList.filter(c => !regionalLower.has(c.toLowerCase().trim()));
  }, [cropList, regionalCrops]);

  const isCommonCropSelected = (cropName) => {
    return previousCrop && previousCrop.toLowerCase().trim() === cropName.toLowerCase().trim();
  };

  const isOtherCropSelected = useMemo(() => {
    if (!previousCrop) return false;
    const isRegional = regionalCrops.some(c => c.toLowerCase().trim() === previousCrop.toLowerCase().trim());
    return !isRegional;
  }, [previousCrop, regionalCrops]);

  const handleStateChange = (e) => {
    const val = e.target.value;
    setSelectedState(val);
    setSelectedDistrict('');
    setDistrictsList([]);
    setRegionalCrops([]);
    setPreviousCrop('');
    if (fieldErrors.state) {
      setFieldErrors(prev => ({ ...prev, state: '' }));
    }
    if (fieldErrors.district) {
      setFieldErrors(prev => ({ ...prev, district: '' }));
    }
    if (fieldErrors.previousCrop) {
      setFieldErrors(prev => ({ ...prev, previousCrop: '' }));
    }
    if (errorMsg) setErrorMsg(null);
  };

  const handleDistrictChange = async (e) => {
    const val = e.target.value;
    setSelectedDistrict(val);
    setPreviousCrop('');
    setRegionalCrops([]);
    if (fieldErrors.district) {
      setFieldErrors(prev => ({ ...prev, district: '' }));
    }
    if (fieldErrors.previousCrop) {
      setFieldErrors(prev => ({ ...prev, previousCrop: '' }));
    }
    if (errorMsg) setErrorMsg(null);

    if (val && selectedState) {
      setLoadingRegionalCrops(true);
      try {
        const crops = await api.getLocationCrops(selectedState, val);
        setRegionalCrops(crops || []);
      } catch (err) {
        console.error('Error fetching regional crops:', err);
        setRegionalCrops([]);
      } finally {
        setLoadingRegionalCrops(false);
      }
    }
  };

  const handleWaterSelect = (val) => {
    setWaterAvailability(val);
    if (fieldErrors.water) {
      setFieldErrors(prev => ({ ...prev, water: '' }));
    }
    if (errorMsg) setErrorMsg(null);
  };

  const handleSoilSelect = (val) => {
    setSoilType(val);
    if (fieldErrors.soil) {
      setFieldErrors(prev => ({ ...prev, soil: '' }));
    }
    if (errorMsg) setErrorMsg(null);
  };

  const handleSelectRegionalCrop = (crop) => {
    setPreviousCrop(crop);
    if (fieldErrors.previousCrop) {
      setFieldErrors(prev => ({ ...prev, previousCrop: '' }));
    }
    if (errorMsg) setErrorMsg(null);
  };

  const handleSelectOtherCrop = (e) => {
    const val = e.target.value;
    setPreviousCrop(val);
    if (fieldErrors.previousCrop) {
      setFieldErrors(prev => ({ ...prev, previousCrop: '' }));
    }
    if (errorMsg) setErrorMsg(null);
  };

  const handleReset = () => {
    setSelectedState('');
    setSelectedDistrict('');
    setDistrictsList([]);
    setRegionalCrops([]);
    setWaterAvailability('');
    setSoilType('');
    setPreviousCrop('');
    setFieldErrors({});
    setErrorMsg(null);
    setLocationMeta(null);
    setRecommendations([]);
    setSelectedCropIndex(0);
    setFertResult(null);
    setSaveStatus(null);
    setViewState('form');
  };

  const handleSubmitForm = async (e) => {
    if (e) e.preventDefault();
    
    // Strict client-side validation
    const errors = {};
    if (!selectedState) {
      errors.state = "Please select your state.";
    }
    if (!selectedDistrict) {
      errors.district = "Please select your district.";
    }
    if (!waterAvailability) {
      errors.water = "Please select water availability.";
    }
    if (!soilType) {
      errors.soil = "Please select soil type.";
    }
    if (!previousCrop) {
      errors.previousCrop = "Please select your previous crop.";
    }

    if (Object.keys(errors).length > 0) {
      setFieldErrors(errors);
      setErrorMsg("Please complete all field information before getting a recommendation.");
      return;
    }

    setFieldErrors({});
    setErrorMsg(null);
    setViewState('loading');

    try {
      const response = await api.getCropRecommendation({
        state: selectedState,
        district: selectedDistrict,
        water_availability: waterAvailability,
        soil_type: soilType,
        previous_crop: previousCrop
      });

      if (response && response.recommendations && response.recommendations.length > 0) {
        setLocationMeta(response.location);
        setRecommendations(response.recommendations);
        setSelectedCropIndex(0);
        setFertResult(null);
        setViewState('crop_result');
      } else {
        throw new Error("Invalid response format received from server.");
      }
    } catch (err) {
      console.error('Prediction failed:', err);
      setErrorMsg("We couldn't generate a recommendation right now. Please check your inputs and try again.");
      setViewState('form');
    }
  };

  const currentCrop = recommendations[selectedCropIndex] || null;

  const handleFetchFertilizer = async (cropObj) => {
    const targetCrop = cropObj || currentCrop;
    if (!targetCrop) return;
    setErrorMsg(null);

    if (fertResult && fertResult.crop.toLowerCase() === targetCrop.crop.toLowerCase()) {
      setViewState('fert_result');
      return;
    }

    setViewState('loading');
    try {
      const response = await api.getFertilizerPlan({
        crop: targetCrop.crop,
        soil_type: targetCrop.soil_type || soilType,
        nitrogen: targetCrop.baseline_npk?.n || 40,
        phosphorus: targetCrop.baseline_npk?.p || 20,
        potassium: targetCrop.baseline_npk?.k || 20
      });

      if (response && response.fertilizer_name) {
        setFertResult(response);
        setViewState('fert_result');
      } else {
        throw new Error("Unable to retrieve fertilizer plan.");
      }
    } catch (err) {
      console.error('Fertilizer retrieval failed:', err);
      setErrorMsg("Unable to retrieve fertilizer recommendation at this time.");
      setViewState('crop_result');
    }
  };

  const handleSaveRecommendation = async () => {
    if (!currentCrop) return;
    try {
      await api.saveRecommendation({
        state: locationMeta?.state || selectedState,
        district: locationMeta?.district || selectedDistrict,
        location_match_level: locationMeta?.match_level || "district",
        water_availability: currentCrop.water_requirement || waterAvailability,
        soil_type: currentCrop.soil_type || soilType,
        previous_crop: currentCrop.previous_crop || previousCrop,
        recommended_crop: currentCrop.crop,
        ml_score: currentCrop.ml_score || 0.85,
        final_score: currentCrop.final_score,
        fertilizer_name: fertResult?.fertilizer_name || "14-35-14",
        nitrogen: fertResult?.nitrogen || 40,
        phosphorus: fertResult?.phosphorus || 20,
        potassium: fertResult?.potassium || 20
      });
      setSaveStatus('saved');
    } catch (err) {
      console.error('Save failed:', err);
      setSaveStatus('error');
    }
  };

  const handlePrint = () => {
    window.print();
  };

  const currentDate = new Date().toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });

  const getSuitabilityIcon = (suitability) => {
    switch ((suitability || '').toLowerCase()) {
      case 'high':
        return <Check size={15} />;
      case 'medium':
        return <Info size={15} />;
      default:
        return <AlertCircle size={15} />;
    }
  };

  const getLocationBadgeText = () => {
    if (!locationMeta) return `Supported in ${selectedDistrict || 'selected location'}`;
    if (locationMeta.match_level === 'district') {
      return `✓ Supported in ${locationMeta.district}`;
    } else if (locationMeta.match_level === 'state') {
      return `✓ Supported across ${locationMeta.state}`;
    }
    return 'Agronomically Viable';
  };

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto' }}>
      
      {/* Print Header */}
      <div className="print-header">
        <div className="print-header-title">CropMitra — Agricultural Advisory Report</div>
        <div className="print-header-meta">
          Date: {currentDate} | Location: {locationMeta ? `${locationMeta.district}, ${locationMeta.state}` : `${selectedDistrict}, ${selectedState}`}
        </div>
      </div>

      {errorMsg && (
        <div className="alert alert-error">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <AlertCircle size={18} />
            <span>{errorMsg}</span>
          </div>
        </div>
      )}

      {/* =========================================================================
          VIEW 1: CROP ADVISOR INPUT FORM
         ========================================================================= */}
      {viewState === 'form' && (
        <div className="card">
          <div className="page-header">
            <h1 className="page-title">Find the right crop for your field</h1>
            <p className="page-subtitle">
              Enter your location, water availability, soil type, and previous crop to receive an ML-backed recommendation.
            </p>
          </div>

          <form onSubmit={handleSubmitForm} noValidate>
            
            {/* 1. LOCATION SECTION */}
            <div className="form-group">
              <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <MapPin size={17} color="var(--color-primary)" />
                <span>1. Location (State & District)</span>
              </label>
              
              <div className="form-grid-2">
                <div>
                  <label htmlFor="stateSelect" style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', marginBottom: '4px', display: 'block' }}>
                    State / Region <span style={{ color: 'var(--color-error)' }}>*</span>
                  </label>
                  <select
                    id="stateSelect"
                    className={`form-select ${fieldErrors.state ? 'error' : ''}`}
                    value={selectedState}
                    onChange={handleStateChange}
                  >
                    <option value="">Select state / region</option>
                    {statesList.map((st) => (
                      <option key={st} value={st}>
                        {st}
                      </option>
                    ))}
                  </select>
                  {fieldErrors.state && (
                    <div className="field-error-text">
                      <AlertCircle size={13} />
                      <span>{fieldErrors.state}</span>
                    </div>
                  )}
                </div>

                <div>
                  <label htmlFor="districtSelect" style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', marginBottom: '4px', display: 'block' }}>
                    District / Location <span style={{ color: 'var(--color-error)' }}>*</span>
                  </label>
                  <select
                    id="districtSelect"
                    className={`form-select ${fieldErrors.district ? 'error' : ''}`}
                    value={selectedDistrict}
                    onChange={handleDistrictChange}
                    disabled={!selectedState}
                  >
                    <option value="">
                      {!selectedState ? "Select state first" : "Select district / location"}
                    </option>
                    {districtsList.map((dst) => (
                      <option key={dst} value={dst}>
                        {dst}
                      </option>
                    ))}
                  </select>
                  {fieldErrors.district && (
                    <div className="field-error-text">
                      <AlertCircle size={13} />
                      <span>{fieldErrors.district}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* 2. FIELD CONDITIONS (Water & Soil) */}
            <div className="form-group">
              <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <Droplets size={17} color="var(--color-primary)" />
                <span>2. Water Availability <span style={{ color: 'var(--color-error)' }}>*</span></span>
              </label>
              <div className={`form-radio-grid ${fieldErrors.water ? 'error-grid' : ''}`}>
                {WATER_OPTIONS.map((opt) => (
                  <div
                    key={opt.id}
                    className={`radio-card ${waterAvailability === opt.id ? 'selected' : ''}`}
                    onClick={() => handleWaterSelect(opt.id)}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') handleWaterSelect(opt.id); }}
                  >
                    <div className="radio-card-title">{opt.label}</div>
                    <div style={{ fontSize: '0.775rem', color: 'var(--color-text-muted)', marginTop: '2px' }}>
                      {opt.desc}
                    </div>
                  </div>
                ))}
              </div>
              {fieldErrors.water && (
                <div className="field-error-text">
                  <AlertCircle size={13} />
                  <span>{fieldErrors.water}</span>
                </div>
              )}
            </div>

            {/* 3. SOIL TYPE */}
            <div className="form-group">
              <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <Layers size={17} color="var(--color-primary)" />
                <span>3. Soil Type <span style={{ color: 'var(--color-error)' }}>*</span></span>
              </label>
              <div className={`form-radio-grid ${fieldErrors.soil ? 'error-grid' : ''}`}>
                {SOIL_OPTIONS.map((opt) => (
                  <div
                    key={opt.id}
                    className={`radio-card ${soilType === opt.id ? 'selected' : ''}`}
                    onClick={() => handleSoilSelect(opt.id)}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') handleSoilSelect(opt.id); }}
                  >
                    <div className="radio-card-title">{opt.label}</div>
                  </div>
                ))}
              </div>
              {fieldErrors.soil && (
                <div className="field-error-text">
                  <AlertCircle size={13} />
                  <span>{fieldErrors.soil}</span>
                </div>
              )}
            </div>

            {/* 4. PREVIOUS CROP */}
            <div className="form-group">
              <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.2rem' }}>
                <Sprout size={17} color="var(--color-primary)" />
                <span>4. Previous Crop <span style={{ color: 'var(--color-error)' }}>*</span></span>
              </label>
              <div style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)', marginBottom: '0.85rem' }}>
                Select the crop you grew in the previous season.
              </div>

              {!selectedDistrict ? (
                <div className={`previous-crop-empty-state ${fieldErrors.previousCrop ? 'error-border' : ''}`}>
                  <Info size={18} color="var(--color-primary)" />
                  <span>Select a district to see common crops.</span>
                </div>
              ) : loadingRegionalCrops ? (
                <div className="previous-crop-empty-state">
                  <div className="spinner-sm"></div>
                  <span>Loading common crops...</span>
                </div>
              ) : (
                <div className={`previous-crop-panel ${fieldErrors.previousCrop && !previousCrop ? 'error-border' : ''}`}>
                  {regionalCrops.length > 0 ? (
                    <>
                      {/* Regional crops header banner */}
                      <div className="regional-crops-banner">
                        <div className="regional-badge-icon">
                          <Sparkles size={16} />
                        </div>
                        <div>
                          <div className="regional-crops-heading">
                            Common crops in {selectedDistrict}
                          </div>
                          <div className="regional-crops-subtext">
                            Based on our regional dataset for {selectedDistrict}, {selectedState}
                          </div>
                        </div>
                      </div>

                      {/* Selectable button cards */}
                      <div className="regional-crop-grid">
                        {regionalCrops.map((crop) => {
                          const isSelected = isCommonCropSelected(crop);
                          return (
                            <div
                              key={crop}
                              className={`regional-crop-btn ${isSelected ? 'selected' : ''}`}
                              onClick={() => handleSelectRegionalCrop(crop)}
                              role="button"
                              tabIndex={0}
                              onKeyDown={(e) => {
                                if (e.key === 'Enter' || e.key === ' ') {
                                  e.preventDefault();
                                  handleSelectRegionalCrop(crop);
                                }
                              }}
                            >
                              {isSelected && <Check size={14} className="crop-check-icon" />}
                              <span>{crop}</span>
                            </div>
                          );
                        })}
                      </div>

                      {/* Divider */}
                      <div className="crop-or-divider">
                        <span>OR</span>
                      </div>
                    </>
                  ) : (
                    <div style={{ fontSize: '0.9rem', color: 'var(--color-text-muted)', marginBottom: '1rem', fontStyle: 'italic' }}>
                      No regional crop information is available for this location.
                    </div>
                  )}

                  {/* Other crops dropdown */}
                  <div className="other-crops-group">
                    <label htmlFor="otherCropSelect" style={{ fontSize: '0.825rem', fontWeight: 600, color: 'var(--color-text-muted)', marginBottom: '6px', display: 'block' }}>
                      Other crops
                    </label>
                    <select
                      id="otherCropSelect"
                      className={`form-select ${fieldErrors.previousCrop && !previousCrop ? 'error' : ''}`}
                      value={isOtherCropSelected ? previousCrop : ''}
                      onChange={handleSelectOtherCrop}
                    >
                      <option value="">Select from other crops</option>
                      {otherCrops.map((crop) => (
                        <option key={crop} value={crop}>
                          {crop}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              )}

              {fieldErrors.previousCrop && (
                <div className="field-error-text">
                  <AlertCircle size={13} />
                  <span>{fieldErrors.previousCrop}</span>
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="form-actions">
              <button type="submit" className="btn btn-primary btn-lg" style={{ flex: 1 }}>
                <span>Get Recommendation</span>
                <ArrowRight size={18} />
              </button>
              <button type="button" className="btn btn-secondary btn-lg" onClick={handleReset}>
                <RotateCcw size={18} />
                <span>Reset</span>
              </button>
            </div>
          </form>
        </div>
      )}

      {/* =========================================================================
          VIEW 2: LOADING STATE
         ========================================================================= */}
      {viewState === 'loading' && (
        <div className="card loading-box">
          <div className="spinner"></div>
          <h2 className="loading-text">Analyzing your field...</h2>
          <p className="loading-subtext">
            Filtering location crop registry, ML conditions, and rotation compatibility.
          </p>
        </div>
      )}

      {/* =========================================================================
          VIEW 3: RECOMMENDATION RESULT
         ========================================================================= */}
      {viewState === 'crop_result' && currentCrop && (
        <div className="card">
          
          {/* Your Field Summary Context */}
          <div className="field-context-box">
            <div className="field-context-item">
              <span className="field-context-label">Location</span>
              <span className="field-context-val">
                {locationMeta ? `${locationMeta.district}, ${locationMeta.state}` : `${selectedDistrict}, ${selectedState}`}
              </span>
            </div>
            <div className="field-context-item">
              <span className="field-context-label">Soil Type</span>
              <span className="field-context-val">{currentCrop.soil_type}</span>
            </div>
            <div className="field-context-item">
              <span className="field-context-label">Water</span>
              <span className="field-context-val">{waterAvailability.toUpperCase ? waterAvailability.toUpperCase() : waterAvailability}</span>
            </div>
            <div className="field-context-item">
              <span className="field-context-label">Previous Crop</span>
              <span className="field-context-val">{currentCrop.previous_crop}</span>
            </div>
          </div>

          <div className="page-header" style={{ marginBottom: '1.25rem' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--color-secondary-green)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Primary Recommendation
            </span>
            <h1 style={{ fontSize: '1.85rem', marginTop: '0.2rem' }}>Recommended Crop</h1>
          </div>

          {/* Banner */}
          <div className="result-banner">
            <div>
              <div style={{ fontSize: '0.825rem', fontWeight: 700, color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>
                Rank #{selectedCropIndex + 1} Best Match
              </div>
              <div className="result-crop-name">{currentCrop.crop}</div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.4rem' }}>
              <div className={`suitability-badge ${currentCrop.suitability.toLowerCase()}`}>
                {getSuitabilityIcon(currentCrop.suitability)}
                <span>Suitability: {currentCrop.suitability}</span>
              </div>
              <div style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--color-text-muted)' }}>
                Score: {currentCrop.final_score} / 10
              </div>
            </div>
          </div>

          {/* Location Compatibility Card */}
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '0.6rem', 
            padding: '0.75rem 1rem', 
            backgroundColor: 'var(--color-surface-subtle)', 
            border: '1px solid var(--color-border)', 
            borderRadius: 'var(--radius-md)', 
            marginBottom: '1.5rem',
            color: 'var(--color-primary)',
            fontWeight: 700,
            fontSize: '0.95rem'
          }}>
            <ShieldCheck size={20} color="var(--color-secondary-green)" />
            <span>Location Compatibility: </span>
            <span style={{ color: 'var(--color-text-main)', fontWeight: 600 }}>
              {getLocationBadgeText()}
            </span>
          </div>

          {/* Key Agronomic Metrics */}
          <div className="result-grid">
            <div className="result-meta-item">
              <div className="meta-label">Water Requirement</div>
              <div className="meta-val">{currentCrop.water_requirement}</div>
            </div>
            <div className="result-meta-item">
              <div className="meta-label">Soil Compatibility</div>
              <div className="meta-val">{currentCrop.soil_compatibility}</div>
            </div>
            <div className="result-meta-item">
              <div className="meta-label">Growing Season</div>
              <div className="meta-val">{currentCrop.growing_season || 'Kharif / Rabi'}</div>
            </div>
            <div className="result-meta-item">
              <div className="meta-label">Crop Category</div>
              <div className="meta-val">{currentCrop.crop_type || 'Field Crop'}</div>
            </div>
          </div>

          {/* Explainability Section */}
          <div className="explanation-card">
            <h3 className="explanation-title">Why this crop?</h3>
            <p className="explanation-body">{currentCrop.reason}</p>
          </div>

          {/* Multiple Recommendations (Rank #2, Rank #3) */}
          {recommendations.length > 1 && (
            <div className="candidates-section no-print">
              <h3 className="candidates-title">Alternative Suitable Crops for {locationMeta?.district || selectedDistrict}</h3>
              {recommendations.map((rec, idx) => (
                <div 
                  key={rec.crop} 
                  className="candidate-card"
                  style={{
                    borderColor: selectedCropIndex === idx ? 'var(--color-primary)' : 'var(--color-border)',
                    backgroundColor: selectedCropIndex === idx ? 'var(--color-very-light-green)' : 'var(--color-surface-subtle)'
                  }}
                >
                  <div className="candidate-info">
                    <span className="candidate-rank">#{idx + 1}</span>
                    <div>
                      <div className="candidate-name">{rec.crop}</div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
                        Water: {rec.water_requirement} | Soil: {rec.soil_compatibility}
                      </div>
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <span className={`suitability-badge ${rec.suitability.toLowerCase()}`}>
                      {getSuitabilityIcon(rec.suitability)}
                      <span>{rec.suitability}</span>
                    </span>
                    {selectedCropIndex !== idx && (
                      <button 
                        className="btn btn-secondary" 
                        style={{ padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}
                        onClick={() => setSelectedCropIndex(idx)}
                      >
                        Select
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Action Buttons */}
          <div className="form-actions no-print">
            <button className="btn btn-primary" onClick={() => handleFetchFertilizer(currentCrop)} style={{ flex: 1 }}>
              <FlaskConical size={18} />
              <span>View Fertilizer Plan for {currentCrop.crop}</span>
            </button>
            <button className="btn btn-secondary" onClick={handleReset}>
              <RotateCcw size={18} />
              <span>New Recommendation</span>
            </button>
            <button className="btn btn-secondary" onClick={handlePrint}>
              <Printer size={18} />
              <span>Print Result</span>
            </button>
          </div>
        </div>
      )}

      {/* =========================================================================
          VIEW 4: FERTILIZER PLAN RESULT
         ========================================================================= */}
      {viewState === 'fert_result' && fertResult && (
        <div className="card">
          <div className="page-header" style={{ marginBottom: '1.25rem' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--color-secondary-green)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Soil Nutrition Plan
            </span>
            <h1 style={{ fontSize: '1.85rem', marginTop: '0.2rem' }}>Fertilizer Recommendation</h1>
          </div>

          {/* Fertilizer Name Header */}
          <div className="result-banner">
            <div>
              <div style={{ fontSize: '0.825rem', fontWeight: 700, color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>
                Recommended Compound
              </div>
              <div className="result-crop-name" style={{ fontSize: '2rem' }}>
                {fertResult.fertilizer_name}
              </div>
              <div style={{ fontSize: '0.95rem', color: 'var(--color-text-muted)', fontWeight: 600 }}>
                {fertResult.full_name}
              </div>
            </div>
            <div>
              <span className="suitability-badge high">
                Target: {fertResult.crop} ({fertResult.soil_type} Soil)
              </span>
            </div>
          </div>

          {/* N-P-K Nutrient Cards */}
          <div className="npk-cards-grid">
            <div className="npk-card">
              <div className="npk-symbol">N</div>
              <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--color-text-light)' }}>Nitrogen</div>
              <div className="npk-val">{fertResult.nitrogen}</div>
              <div className="npk-unit">kg / acre</div>
            </div>

            <div className="npk-card">
              <div className="npk-symbol">P</div>
              <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--color-text-light)' }}>Phosphorus</div>
              <div className="npk-val">{fertResult.phosphorus}</div>
              <div className="npk-unit">kg / acre</div>
            </div>

            <div className="npk-card">
              <div className="npk-symbol">K</div>
              <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--color-text-light)' }}>Potassium</div>
              <div className="npk-val">{fertResult.potassium}</div>
              <div className="npk-unit">kg / acre</div>
            </div>
          </div>

          {/* Application Guidance */}
          <div className="guidance-section">
            <h3 className="guidance-title">Application Guidance</h3>
            <p style={{ color: 'var(--color-text-main)', fontSize: '0.95rem', lineHeight: 1.6, marginBottom: '0.75rem' }}>
              {fertResult.explanation}
            </p>
            <p style={{ color: 'var(--color-text-main)', fontSize: '0.95rem', lineHeight: 1.6 }}>
              {fertResult.guidance}
            </p>
          </div>

          {/* Standard Agronomic Disclaimer */}
          <div className="disclaimer-box">
            <strong>Advisory Note: </strong>
            {fertResult.disclaimer}
          </div>

          {/* Save Status Notification */}
          {saveStatus === 'saved' && (
            <div className="alert alert-success" style={{ marginBottom: '1.25rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <CheckCircle2 size={18} />
                <span>Recommendation plan successfully saved to database!</span>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="form-actions no-print">
            <button className="btn btn-secondary" onClick={() => setViewState('crop_result')}>
              <ArrowLeft size={18} />
              <span>Back to Crop Result</span>
            </button>
            <button 
              className="btn btn-secondary" 
              onClick={handleSaveRecommendation}
              disabled={saveStatus === 'saved'}
            >
              <Bookmark size={18} />
              <span>{saveStatus === 'saved' ? 'Saved' : 'Save Plan'}</span>
            </button>
            <button className="btn btn-primary" onClick={handlePrint}>
              <Printer size={18} />
              <span>Print Fertilizer Plan</span>
            </button>
          </div>
        </div>
      )}

    </div>
  );
}
