import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { updateDocument } from '../../store/slices/documentSlice';

const UpdateDocument = () => {
  const [file, setFile] = useState(null);
  const [documentName, setDocumentName] = useState('');
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const loading = useSelector((state) => state.documents.loading);
  const error = useSelector((state) => state.documents.error);

  // Convert file to Base64 encoded string
  const encodeFileToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result.split(',')[1]); // Get only the Base64 part
      reader.onerror = (error) => reject(error);
    });
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      alert('Please select a file to upload.');
      return;
    }

    try {
      const encodedFile = await encodeFileToBase64(file);

      const payload = {
        document_name: documentName,
        document: encodedFile,
      };

      // Dispatch the updateDocument action with JSON payload
      dispatch(updateDocument(payload))
        .unwrap()
        .then(() => {
          alert('Document updated successfully!');
          setDocumentName('');
          setFile(null);
          navigate('/dashboard');
        })
        .catch((error) => {
          alert(error || 'An unexpected error occurred during document update.');
        });
    } catch (error) {
      alert('Failed to encode the file.');
    }
  };

  return (
    <div style={styles.container}>
      <h1>Update Document</h1>
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

        <input
          type="file"
          onChange={handleFileChange}
          required
          style={styles.input}
        />

        <button type="submit" style={styles.button} disabled={loading}>
          {loading ? 'Updating...' : 'Update Document'}
        </button>
      </form>
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

export default UpdateDocument;