import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { NodesProvider } from './context/NodesContext';
import { RelationshipsProvider } from './context/RelationshipsContext';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <NodesProvider>
      <RelationshipsProvider>
        <App />
      </RelationshipsProvider>
    </NodesProvider>
  </React.StrictMode>
);
