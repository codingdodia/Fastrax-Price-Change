import React from 'react';
import { useNavigate } from 'react-router-dom';

const HomeButton: React.FC = () => {
  const navigate = useNavigate();
  return (
    <button
      onClick={() => navigate('/welcome')}
      style={{
        background: '#007bff',
        color: '#fff',
        border: 'none',
        borderRadius: '4px',
        padding: '8px 20px',
        fontSize: '16px',
        fontWeight: 500,
        cursor: 'pointer',
        margin: '16px 0',
        boxShadow: '0 2px 6px rgba(0,0,0,0.07)'
      }}
    >
      Home
    </button>
  );
};

export default HomeButton;
