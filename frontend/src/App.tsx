import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Detections from "./pages/Detections";
import CameraManagement from "./pages/CameraManagement";
import UserManagement from "./pages/UserManagement";
import Support from "./pages/Support";
import LiveCameras from "./pages/LiveCameras";
import NotFound from "./pages/NotFound";
import Layout from "./components/Layout";
import PrivateRoute from "./components/PrivateRoute";

const App = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<PrivateRoute><Layout /></PrivateRoute>}>
          <Route index element={<Dashboard />} />
          <Route path="live" element={<LiveCameras />} />
          <Route path="detections" element={<Detections />} />
          <Route path="admin/cameras" element={<CameraManagement />} />
          <Route path="admin/users" element={<UserManagement />} />
          <Route path="support" element={<Support />} />
        </Route>
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
