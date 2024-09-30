import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css'; // Ensure this file exists and is correctly styled
import App from './App';
import reportWebVitals from './reportWebVitals';


const rootElement = document.getElementById('root');

if (rootElement) {
  const root = ReactDOM.createRoot(rootElement);
  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );

  reportWebVitals();

} else {
  console.error("Root element not found");
}

