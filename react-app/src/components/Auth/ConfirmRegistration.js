import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { confirmRegistration } from "../../store/slices/authSlice";
import axios from "axios";

const ConfirmRegistration = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const [formData, setFormData] = useState({
    username: "",
    confirmation_code: "",
  });
  const [errorMessage, setErrorMessage] = useState("");
  const [infoMessage, setInfoMessage] = useState(""); // Success message for resend confirmation
  const { error } = useSelector((state) => state.auth);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setErrorMessage("");
    setInfoMessage("");

    dispatch(confirmRegistration(formData))
      .unwrap()
      .then(() => {
        alert("Confirmation successful! You can now log in.");
        navigate("/login");
      })
      .catch((error) => {
        setErrorMessage(error || "Confirmation failed. Please try again.");
      });
  };

  const handleResendCode = async () => {
    setErrorMessage("");
    setInfoMessage("");

    try {
      await axios.post(
        `${process.env.REACT_APP_API_BASE_URL}/resend_confirmation_code`,
        { username: formData.username },
        {
          headers: { "Content-Type": "application/json" },
        }
      );
      setInfoMessage("Confirmation code has been resent. Please check your email.");
    } catch (error) {
      setErrorMessage("Failed to resend confirmation code. Please try again later.");
    }
  };

  return (
    <div style={styles.container}>
      <h1>Confirm Registration</h1>
      {errorMessage && <p style={{ color: "red" }}>{errorMessage}</p>}
      {infoMessage && <p style={{ color: "green" }}>{infoMessage}</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      <form onSubmit={handleSubmit} style={styles.form}>
        <input
          type="text"
          name="username"
          placeholder="Username"
          onChange={handleChange}
          required
          style={styles.input}
        />
        <input
          type="text"
          name="confirmation_code"
          placeholder="Confirmation Code"
          onChange={handleChange}
          required
          style={styles.input}
        />
        <button type="submit" style={styles.button}>Confirm</button>
        <button type="button" onClick={handleResendCode} style={styles.button}>
          Resend Confirmation Code
        </button>
      </form>
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
};

export default ConfirmRegistration;