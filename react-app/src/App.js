import logo from './logo.svg';
import './App.css'; 

import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import SplashPage from './components/SplashPage';
import DocumentServicesDashboard from './components/DocumentServicesDashboard';
import Register from './components/Auth/Register';
import ConfirmRegistration from "./components/Auth/ConfirmRegistration";
import Login from './components/Auth/Login';
import UploadDocument from './components/Documents/UploadDocument';
import ViewDocument from './components/Documents/ViewDocument';
import ListDocuments from './components/Documents/ListDocuments';
import UpdateDocument from './components/Documents/UpdateDocument';
import DeleteDocument from './components/Documents/DeleteDocument';
import MultipartUploadDocument from './components/Documents/MultipartUploadDocument';


const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<SplashPage />} />
        <Route path="/register" element={<Register />} />
        <Route path="/confirm-registration" element={<ConfirmRegistration />} /> 
        <Route path="/login" element={<Login />} />
        <Route path="/upload" element={<UploadDocument />} />
        <Route path="/view" element={<ViewDocument />} />
        <Route path="/list" element={<ListDocuments />} />
        <Route path="/update" element={<UpdateDocument />} />
        <Route path="/delete" element={<DeleteDocument />} />
        <Route path="/multipart-upload" element={<MultipartUploadDocument />} />
        <Route path="/dashboard" element={<DocumentServicesDashboard />} />
      </Routes>
    </Router>
  );
};

export default App;