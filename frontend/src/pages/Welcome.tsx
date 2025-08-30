
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

function Welcome() {
  // Gracefully shutdown backend when tab is closed
  useEffect(() => {
    const handleBeforeUnload = () => {
      navigator.sendBeacon('http://backend:5000/shutdown');
    };
    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, []);

  const navigate = useNavigate();

  const handleLogin = () => {
    navigate("/fastraxLogin");
  };

  const handlePriceChange = () => {
    navigate("/priceChange");
  };

  return (
    <div style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
      <h1>Welcome</h1>
      <p>Select an action to continue.</p>
      <div style={{ display: 'flex', gap: '16px' }}>
        <button onClick={handleLogin}>Pull Data from Fastrax</button>
        <button onClick={handlePriceChange}>Change Price</button>
      </div>
    </div>
  );
}

export default Welcome;
