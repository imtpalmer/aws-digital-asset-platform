import React from 'react';
import { useNavigate } from 'react-router-dom';

const SplashPage = () => {
  const navigate = useNavigate();

  return (
    <div style={styles.container}>
      <h1>Welcome to the AWS Digital Assets Management Platform</h1>
      <div style={styles.buttons}>
        <button onClick={() => navigate('/login')} style={styles.button}>Login</button>
        <button onClick={() => navigate('/register')} style={styles.button}>Register</button>
      </div>
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
  buttons: {
    marginTop: '20px',
  },
  button: {
    margin: '10px',
    padding: '10px 20px',
    fontSize: '16px',
    cursor: 'pointer',
  },
};

export default SplashPage;