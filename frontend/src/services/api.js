/**
 * CropMitra V2 Backend API Client
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

async function handleResponse(response) {
  if (!response.ok) {
    let errorMsg = `Server error (${response.status})`;
    try {
      const errData = await response.json();
      if (errData.detail) {
        if (Array.isArray(errData.detail)) {
          errorMsg = errData.detail.map(d => d.msg || d.loc?.join('.')).join(', ');
        } else {
          errorMsg = errData.detail;
        }
      }
    } catch {
      // ignore json parse error
    }
    throw new Error(errorMsg);
  }
  return response.json();
}

export const api = {
  /**
   * Fetch unique Indian States
   */
  async getStates() {
    try {
      const res = await fetch(`${API_BASE_URL}/api/locations/states`);
      return await handleResponse(res);
    } catch (err) {
      console.error('Failed to fetch states:', err);
      return ["Maharashtra", "Punjab", "Gujarat", "Karnataka", "Tamil Nadu", "Uttar Pradesh", "Madhya Pradesh", "Rajasthan"];
    }
  },

  /**
   * Fetch districts for a selected state
   */
  async getDistricts(state) {
    if (!state) return [];
    try {
      const res = await fetch(`${API_BASE_URL}/api/locations/districts?state=${encodeURIComponent(state)}`);
      return await handleResponse(res);
    } catch (err) {
      console.error(`Failed to fetch districts for ${state}:`, err);
      return [state];
    }
  },

  /**
   * Fetch crops registered for a location
   */
  async getLocationCrops(state, district) {
    try {
      const res = await fetch(`${API_BASE_URL}/api/locations/crops?state=${encodeURIComponent(state)}&district=${encodeURIComponent(district)}`);
      return await handleResponse(res);
    } catch (err) {
      console.error('Failed to fetch location crops:', err);
      return [];
    }
  },

  /**
   * Fetch generic crops list for previous crop selector
   */
  async getCrops() {
    try {
      const res = await fetch(`${API_BASE_URL}/api/crops`);
      return await handleResponse(res);
    } catch (err) {
      console.error('Failed to fetch crops:', err);
      return [
        "Rice", "Wheat", "Maize", "Soybean", "Cotton", "Sugarcane",
        "Chickpea", "Kidney Beans", "Pigeon Peas (Tur)", "Moth Beans", "Mung Bean",
        "Black Gram (Urad)", "Lentil (Masoor)", "Pomegranate", "Banana", "Mango",
        "Grapes", "Watermelon", "Muskmelon", "Apple", "Orange",
        "Papaya", "Coconut", "Jute", "Coffee", "Pulses", "Vegetables", "Other", "Unknown"
      ];
    }
  },

  /**
   * Get ML + Location-aware Crop Recommendations
   */
  async getCropRecommendation(data) {
    const res = await fetch(`${API_BASE_URL}/api/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return await handleResponse(res);
  },

  /**
   * Get Fertilizer Plan
   */
  async getFertilizerPlan(data) {
    const res = await fetch(`${API_BASE_URL}/api/fertilizer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return await handleResponse(res);
  },

  /**
   * Save Recommendation
   */
  async saveRecommendation(data) {
    const res = await fetch(`${API_BASE_URL}/api/recommendations/save`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return await handleResponse(res);
  },

  /**
   * List saved recommendations
   */
  async getSavedRecommendations() {
    const res = await fetch(`${API_BASE_URL}/api/recommendations`);
    return await handleResponse(res);
  }
};
