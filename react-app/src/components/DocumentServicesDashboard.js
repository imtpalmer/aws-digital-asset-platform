import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../global.css';

const DocumentServicesDashboard = () => {
  const navigate = useNavigate();

  return (
    <div style={styles.container}>
      <h1>Document Dashboard</h1>
      <div style={styles.servicesContainer}>
        <h2>Document Services</h2>
        <div style={styles.buttonContainer}>
          <button onClick={() => navigate('/upload')} style={styles.button}>Upload Document</button>
          <button onClick={() => navigate('/multipart-upload')} style={styles.button}>Multipart Upload Document</button>
          <button onClick={() => navigate('/list')} style={styles.button}>List Documents</button>
          <button onClick={() => navigate('/view')} style={styles.button}>View Document</button>
          <button onClick={() => navigate('/update')} style={styles.button}>Update Document</button>
          <button onClick={() => navigate('/delete')} style={styles.button}>Delete Document</button>
        </div>
      </div>
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
    padding: "20px",
  },
  servicesContainer: {
    textAlign: "center",
    maxWidth: "400px", // Limit the width of the content
    width: "100%", // Make it responsive
  },
  buttonContainer: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    marginTop: "20px",
    width: "100%", // Make the container responsive
  },
  button: {
    width: "100%", // Buttons take full width within their container
    maxWidth: "300px", // Set a max-width for buttons
    padding: "15px 20px",
    margin: "10px 0", // Uniform margin
    fontSize: "16px",
    cursor: "pointer",
    backgroundColor: "#007bff", // Example background color
    color: "#fff", // Text color
    border: "none", // Remove default border
    borderRadius: "5px", // Rounded corners
    transition: "background-color 0.3s", // Smooth transition
  },
  buttonHover: {
    backgroundColor: "#0056b3", // Darker shade on hover
  },
};

export default DocumentServicesDashboard;