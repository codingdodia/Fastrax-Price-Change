import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import { BrowserRouter, Route, Routes, Navigate } from "react-router-dom";
import FastraxLoginPage from "./pages/FastraxLogin.tsx";
import Welcome from "./pages/Welcome";
import PriceChange from "./pages/PriceChange.tsx";
import PricePreview from "./pages/PricePreview.tsx";

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/welcome" element={<Welcome />} />
        <Route path="/fastraxLogin" element={<FastraxLoginPage />} />
        <Route path="/priceChange" element={<PriceChange />} />
        <Route path="/ChangePricePreview" element={<PricePreview />} />
        <Route path="*" element={<Navigate to="/welcome" replace />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)
