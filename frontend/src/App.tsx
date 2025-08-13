import { useState } from 'react';
import LoginForm from './pages/FastraxLogin';
import { useNavigate } from 'react-router-dom';

function App() {
  const [showLogin, setShowLogin] = useState(false);
  const navigate = useNavigate();

  const handleFetch = () => {
    navigate('/fastraxLogin');
  };

  return (
    <div className="App">
      <h1>What would you like to do?</h1>
      <button onClick={handleFetch} type="button" className="btn">Get Data from Fastrax POS</button>
      <button type="button" className="btn">Change price</button>
      {showLogin && <LoginForm />}
    </div>
  );
}

export default App;
