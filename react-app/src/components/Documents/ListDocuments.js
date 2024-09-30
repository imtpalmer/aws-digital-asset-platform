import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchDocuments } from '../../store/slices/documentSlice';
import { useNavigate } from 'react-router-dom';
import '../../global.css';

const ListDocuments = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  
  // Use Redux state for loading, error, and documents
  const loading = useSelector((state) => state.documents.loading);
  const error = useSelector((state) => state.documents.error);
  const documents = useSelector((state) => state.documents.items);
  
  const [filter, setFilter] = useState('');

  useEffect(() => {
    // Dispatch the fetchDocuments action to load the documents
    dispatch(fetchDocuments());
  }, [dispatch]);

  const handleFilterChange = (event) => {
    setFilter(event.target.value);
  };

  const filteredDocuments = documents.filter((doc) =>
    doc.document_name && doc.document_name.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div style={styles.container}>
      <h1>Document List</h1>

      {loading && <p>Loading documents...</p>}
      {error && <p style={{ color: 'red' }}>Error: {error}</p>}

      <input
        type="text"
        placeholder="Filter documents"
        value={filter}
        onChange={handleFilterChange}
        style={styles.input}
      />

      <ul style={styles.list}>
        {filteredDocuments.length > 0 ? (
          filteredDocuments.map((doc) => (
            <li key={doc.document_name || doc.user_id} style={styles.listItem}>
              <div style={styles.documentInfo}>
                <a href={`/${doc.document_name}`} download style={styles.link}>
                  {doc.document_name || 'Unnamed Document'}
                </a>
                <span style={styles.uploadDate}>Uploaded on: {doc.upload_date}</span>
              </div>
            </li>
          ))
        ) : (
          <li style={styles.listItem}>No documents found</li>
        )}
      </ul>

      <button style={styles.button} onClick={() => navigate('/dashboard')}>
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
  input: {
    margin: "10px 0",
    padding: "10px",
    fontSize: "16px",
    width: "300px",
  },
  list: {
    listStyleType: "none",
    padding: 0,
    width: "100%",
    maxWidth: "600px",
  },
  listItem: {
    margin: "10px 0",
    padding: "10px",
    backgroundColor: "#ffffff",
    borderRadius: "5px",
    boxShadow: "0px 0px 5px rgba(0, 0, 0, 0.1)",
  },
  documentInfo: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  link: {
    textDecoration: "none",
    color: "#007bff",
    fontWeight: "bold",
    marginRight: "10px",
  },
  uploadDate: {
    fontSize: "14px",
    color: "#555",
  },
  button: {
    marginTop: "20px",
    padding: "10px 20px",
    fontSize: "16px",
    cursor: "pointer",
    backgroundColor: "#4CAF50",
    color: "#fff",
    border: "none",
    borderRadius: "5px",
  },
};

export default ListDocuments;