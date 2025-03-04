import React, { createContext, useContext, useReducer } from 'react';

// Utility function to perform API requests
const request = async (endpoint, method = 'GET', data = null) => {
  const options = { method, headers: {} };
  if (data) {
    options.headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(data);
  }
  const res = await fetch('/api/' + endpoint, options);
  let resData;
  try {
    resData = await res.json();
  } catch (error) {
    resData = null;
  }
  if (!res.ok) {
    // Extract error message from response if available
    const errorMsg = resData?.error || (resData?.errors ? JSON.stringify(resData.errors) : res.statusText);
    throw new Error(errorMsg);
  }
  return resData;
};

// Initial state for nodes context
const initialState = {
  nodes: [],
  loading: false,
  error: null,
  aggregated: null,
  aggLoading: false,
  aggError: null,
  searched: false
};

// Reducer to manage node state
function nodesReducer(state, action) {
  switch(action.type) {
    case 'SEARCH_NODES_START':
      return { ...state, loading: true, error: null };
    case 'SEARCH_NODES_SUCCESS':
      return { ...state, loading: false, nodes: action.payload, error: null, searched: true };
    case 'SEARCH_NODES_ERROR':
      return { ...state, loading: false, error: action.payload, searched: true };
    case 'AGG_START':
      return { ...state, aggLoading: true, aggError: null, aggregated: null };
    case 'AGG_SUCCESS':
      return { ...state, aggLoading: false, aggregated: action.payload, aggError: null };
    case 'AGG_ERROR':
      return { ...state, aggLoading: false, aggError: action.payload };
    default:
      return state;
  }
}

const NodesContext = createContext(null);

export const NodesProvider = ({ children }) => {
  const [state, dispatch] = useReducer(nodesReducer, initialState);

  // Fetch nodes with optional filters
  const searchNodes = async ({ labels = [], filters = {}, limit = 100 }) => {
    dispatch({ type: 'SEARCH_NODES_START' });
    try {
      const data = await request('search-nodes/', 'POST', { labels, filters, limit });
      // If successful, data.nodes will contain the list of nodes
      dispatch({ type: 'SEARCH_NODES_SUCCESS', payload: data.nodes || [] });
      return data;
    } catch (error) {
      dispatch({ type: 'SEARCH_NODES_ERROR', payload: error.message });
      throw error;
    }
  };

  // Get aggregated data for nodes of a certain label and numeric property
  const getAggregatedData = async ({ label, property }) => {
    dispatch({ type: 'AGG_START' });
    try {
      const data = await request('get-aggregated-data/', 'POST', { label, property });
      dispatch({ type: 'AGG_SUCCESS', payload: data });
      return data;
    } catch (error) {
      dispatch({ type: 'AGG_ERROR', payload: error.message });
      throw error;
    }
  };

  // Create a node with a single label
  const createNodeSingle = async ({ label }) => {
    return await request('create-node-single-label/', 'POST', { label });
  };

  // Create a node with multiple labels
  const createNodeMultiple = async ({ labels }) => {
    return await request('create-node-multiple-labels/', 'POST', { labels });
  };

  // Create a node with properties (requires at least 5 properties)
  const createNodeWithProperties = async ({ label, properties }) => {
    return await request('create-node-with-properties/', 'POST', { label, properties });
  };

  // Update (add/modify) properties on multiple nodes
  const updateNodesProperties = async ({ label, node_ids, properties }) => {
    return await request('update-multiple-nodes-properties/', 'PUT', { label, node_ids, properties });
  };

  // Remove properties from multiple nodes
  const removeNodesProperties = async ({ label, node_ids, properties }) => {
    return await request('remove-multiple-nodes-properties/', 'PUT', { label, node_ids, properties });
  };

  // Delete multiple nodes (with checks for no relationships)
  const deleteNodes = async ({ label, node_ids }) => {
    return await request('delete-multiple-nodes/', 'DELETE', { label, node_ids });
  };

  return (
    <NodesContext.Provider value={{
      ...state,
      searchNodes,
      getAggregatedData,
      createNodeSingle,
      createNodeMultiple,
      createNodeWithProperties,
      updateNodesProperties,
      removeNodesProperties,
      deleteNodes
    }}>
      {children}
    </NodesContext.Provider>
  );
};

// Custom hook to use NodeContext easily
export const useNodes = () => useContext(NodesContext);
