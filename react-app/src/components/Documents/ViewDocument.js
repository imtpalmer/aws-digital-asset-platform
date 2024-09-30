import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { viewDocument, clearViewUrl } from '../../store/slices/documentSlice';

const ViewDocument = () => {
  const [documentName, setDocumentName] = useState('');
  const dispatch = useDispatch();
  const navigate = useNavigate();

  // Extract the loading state, error, and document URL from Redux store
  const loading = useSelector((state) => state.documents.loading);
  const error = useSelector((state) => state.documents.error);
  const documentUrl = useSelector((state) => state.documents.viewUrl);

  const handleSubmit = (e) => {
    e.preventDefault();
    dispatch(clearViewUrl()); // Clear any previous document URL
    dispatch(viewDocument(documentName));
  };

  return (
    <div style={styles.container}>
      <h1>View Document</h1>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <form onSubmit={handleSubmit} style={styles.form}>
        <input
          type="text"
          placeholder="Document Name"
          value={documentName}
          onChange={(e) => setDocumentName(e.target.value)}
          required
          style={styles.input}
        />

        <button type="submit" style={styles.button} disabled={loading}>
          {loading ? 'Loading...' : 'View Document'}
        </button>
      </form>

      {documentUrl && (
        <div style={styles.documentContainer}>
          <p>Document URL:</p>
          <a href={documentUrl} target="_blank" rel="noopener noreferrer" style={styles.link}>
            {documentUrl}
          </a>
        </div>
      )}

      <button onClick={() => navigate('/dashboard')} style={styles.dashboardButton}>
        Back to Dashboard
      </button>
    </div>
  );
};

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100vh',
    backgroundColor: '#f0f0f0',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    width: '300px',
  },
  input: {
    margin: '10px 0',
    padding: '10px',
    fontSize: '16px',
  },
  button: {
    marginTop: '20px',
    padding: '10px 20px',
    fontSize: '16px',
    cursor: 'pointer',
  },
  documentContainer: {
    marginTop: '20px',
  },
  link: {
    textDecoration: 'none',
    color: '#0000EE',
  },
  dashboardButton: {
    marginTop: '20px',
    padding: '10px 20px',
    fontSize: '16px',
    cursor: 'pointer',
    backgroundColor: '#4CAF50',
    color: '#fff',
    border: 'none',
  },
};

export default ViewDocument;