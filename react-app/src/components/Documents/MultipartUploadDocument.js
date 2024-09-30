// MultipartUploadDocument.js

import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';

import {
  initiateMultipartUpload,
  generatePresignedUrls,
  uploadPart,
  completeMultipartUpload,
  resetUploadProgress,
} from '../../store/slices/documentSlice';

const MultipartUploadDocument = () => {
  const [file, setFile] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const loading = useSelector((state) => state.documents.loading);
  const uploadProgress = useSelector((state) => state.documents.uploadProgress);
  const error = useSelector((state) => state.documents.error);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setErrorMessage('');
    console.log(
      'File selected:',
      selectedFile.name,
      selectedFile.size,
      selectedFile.type
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setErrorMessage('Please select a file to upload.');
      console.warn('No file selected for upload.');
      return;
    }
    dispatch(resetUploadProgress());

    try {
      console.log('Starting multipart upload process for file:', file.name);

      // Step 1: Initiate Upload
      const uploadId = await dispatch(
        initiateMultipartUpload(file.name)
      ).unwrap();

      // Step 2: Generate Presigned URLs
      const partSize = 5 * 1024 * 1024; // 5MB
      const totalParts = Math.ceil(file.size / partSize);

      const partUrls = await dispatch(
        generatePresignedUrls({
          uploadId,
          filename: file.name,
          parts: totalParts,
        })
      ).unwrap();

      // Step 3: Upload Parts
      const parts = [];
      for (let i = 0; i < file.size; i += partSize) {
        const partNumber = Math.floor(i / partSize) + 1;
        const part = file.slice(i, i + partSize);

        // Get the URL by accessing the 'url' property of the corresponding object
        const partUrl = partUrls[partNumber - 1];

        console.log(`Uploading part ${partNumber} of ${totalParts}... to partUrl: ${partUrl}`);

        const partData = await dispatch(
          uploadPart({
            partUrl: partUrl,
            partData: part,
            partNumber,
            totalParts,
          })
        ).unwrap();

        parts.push(partData);
        console.log(`Part ${partNumber} uploaded and recorded.`);
      }

      // Step 4: Complete Upload
      await dispatch(
        completeMultipartUpload({
          uploadId,
          filename: file.name,
          parts,
        })
      ).unwrap();

      alert('File uploaded successfully!');
      setFile(null);
      navigate('/dashboard');
    } catch (err) {
      console.error('Multipart upload failed:', err);
      setErrorMessage(err || 'An error occurred during upload.');
    }
  };

  // Calculate total progress
  const totalProgress =
    Object.values(uploadProgress).reduce((a, b) => a + b, 0) /
    (Object.keys(uploadProgress).length || 1);

  return (
    <div style={styles.container}>
      <h1>Multipart Upload Document</h1>
      {(errorMessage || error) && (
        <p style={{ color: 'red' }}>{errorMessage || error}</p>
      )}
      <form onSubmit={handleSubmit} style={styles.form}>
        <input
          type="file"
          onChange={handleFileChange}
          className="file-input"
          accept=".pdf,.doc,.docx,.txt"
          required
          style={styles.input}
        />
        <button type="submit" style={styles.button} disabled={loading}>
          {loading
            ? `Uploading... ${Math.round(totalProgress)}%`
            : 'Upload Document'}
        </button>
      </form>
      {totalProgress > 0 && (
        <div style={styles.progressBarContainer}>
          <div
            style={{
              ...styles.progressBar,
              width: `${totalProgress}%`,
            }}
          >
            {Math.round(totalProgress)}%
          </div>
        </div>
      )}
      <button
        onClick={() => navigate('/dashboard')}
        style={styles.dashboardButton}
      >
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
    padding: '20px',
    backgroundColor: '#ffffff',
    minHeight: '100vh',
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
    padding: '10px',
    fontSize: '16px',
    cursor: 'pointer',
  },
  progressBarContainer: {
    marginTop: '10px',
    width: '100%',
    backgroundColor: '#f0f0f0',
  },
  progressBar: {
    height: '20px',
    backgroundColor: '#4caf50',
    textAlign: 'center',
    color: 'white',
    lineHeight: '20px',
  },
  dashboardButton: {
    marginTop: '20px',
    padding: '10px',
    fontSize: '16px',
    cursor: 'pointer',
    backgroundColor: '#4CAF50',
    color: '#fff',
    border: 'none',
  },
};

export default MultipartUploadDocument;