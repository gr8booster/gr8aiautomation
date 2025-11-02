const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

/**
 * Make authenticated API call
 * Automatically adds Authorization header from localStorage token
 */
export async function apiCall(endpoint, options = {}) {
  const token = localStorage.getItem('gr8_session_token');
  
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const config = {
    ...options,
    headers,
    credentials: 'include'
  };
  
  const response = await fetch(`${BACKEND_URL}${endpoint}`, config);
  
  // Handle 401 - redirect to login
  if (response.status === 401) {
    localStorage.removeItem('gr8_session_token');
    window.location.href = '/login';
    throw new Error('Session expired');
  }
  
  return response;
}
