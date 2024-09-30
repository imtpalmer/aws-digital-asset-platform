import React, { useState } from 'react';
import axios from 'axios';
import { useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { deleteDocument } from '../../store/slices/documentSlice';

const DeleteDocument = () => {
  const [documentName, setDocumentName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('IdToken');
      console.log("Attempting to delete document:", documentName);

      // Attempt to delete the document through the thunk
      const resultAction = await dispatch(deleteDocument(documentName));

      if (deleteDocument.fulfilled.match(resultAction)) {
        console.log("Document deleted successfully:", documentName);
        alert('Document deleted successfully!');
        setDocumentName('');
        navigate("/dashboard"); // Navigate to the dashboard after successful deletion
      } else {
        console.error("Failed to delete document:", resultAction.payload);
        setError(resultAction.payload || 'Failed to delete document.');
      }
    } catch (error) {
      console.error("An unexpected error occurred during document deletion:", error);
      setError(error.response?.data || 'An unexpected error occurred during document deletion.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <h1>Delete Document</h1>
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
          {loading ? 'Deleting...' : 'Delete Document'}
        </button>
      </form>
      <button onClick={() => navigate("/dashboard")} style={styles.dashboardButton}>
        Back to Dashboard
      </button>
    </div>
  );
};

const styles = {
  container: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    height: "100vh",
    backgroundColor: "#f0f0f0",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    width: "300px",
  },
  input: {
    margin: "10px 0",
    padding: "10px",
    fontSize: "16px",
  },
  button: {
    marginTop: "20px",
    padding: "10px 20px",
    fontSize: "16px",
    cursor: "pointer",
  },
  dashboardButton: {
    marginTop: "20px",
    padding: "10px 20px",
    fontSize: "16px",
    cursor: "pointer",
    backgroundColor: "#4CAF50",
    color: "#fff",
    border: "none",
  },
};

export default DeleteDocument;