import React, { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";
import { uploadDocument } from "../../store/slices/documentSlice";
import "../../global.css";

const UploadDocument = () => {
  const [file, setFile] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");
  const dispatch = useDispatch();
  const navigate = useNavigate();

  // Extract loading and error states from the documents slice
  const loading = useSelector((state) => state.documents.loading);
  const error = useSelector((state) => state.documents.error);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setErrorMessage("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setErrorMessage("Please select a file to upload.");
      return;
    }

    const reader = new FileReader();
    reader.readAsDataURL(file);

    reader.onload = async () => {
      const base64Document = reader.result.split(",")[1];

      const payload = {
        document: base64Document,
        document_name: file.name,
      };

      dispatch(uploadDocument(payload))
        .unwrap()
        .then(() => {
          alert("Document uploaded successfully!");
          setFile(null);
          navigate("/dashboard");
        })
        .catch((error) => {
          setErrorMessage(error || "An unexpected error occurred during document upload.");
        });
    };

    reader.onerror = () => {
      setErrorMessage("Failed to read the file. Please try again.");
    };
  };

  return (
    <div style={styles.container}>
      <h1>Upload Document</h1>
      {errorMessage && <p style={{ color: "red" }}>{errorMessage}</p>}
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
          {loading ? "Uploading..." : "Upload Document"}
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

export default UploadDocument;