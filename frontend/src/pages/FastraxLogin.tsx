import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import HomeButton from '../Components/HomeButton';

function FastraxLoginPage() {
    // Gracefully shutdown backend when tab is closed
    useEffect(() => {
        const handleBeforeUnload = () => {
            navigator.sendBeacon('http://localhost:5000/shutdown');
        };
        window.addEventListener('beforeunload', handleBeforeUnload);
        return () => {
            window.removeEventListener('beforeunload', handleBeforeUnload);
        };
    }, []);
    const [userName, setUserName] = useState<string>("");
    const [password, setPassword] = useState<string>("");
    const [logInStatus, setLogInStatus] = useState<'idle' | 'Logging in' | 'Success' | 'error'>('idle');
    const [fetchStatus, setFetchStatus] = useState<'idle' | 'fetching' | 'fetched' | 'error'>('idle');
    const [timer, setTimer] = useState<number>(0);

    useEffect(() => {
        let interval: ReturnType<typeof setInterval> | undefined;
        if (logInStatus === 'Success' && fetchStatus === 'fetching') {
            setTimer(0);
            interval = setInterval(() => {
                setTimer(prev => prev + 1);
            }, 1000);
        } else {
            setTimer(0);
        }
        return () => {
            if (interval) clearInterval(interval);
        };
    }, [logInStatus, fetchStatus]);

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setLogInStatus('Logging in');
        try {
            const response = await fetch('http://localhost:5000/Login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: userName,
                    password: password,
                }),
            });
            const data = await response.json();
            if (data.message === "Login successful") {
                setLogInStatus('Success');
                handleLoginSuccess();
            } else {
                setLogInStatus('error');
            }
        } catch (error) {
            setLogInStatus('error');
            console.error('Error during login:', error);
        }
    };

    const handleLoginSuccess = async () => {
        setFetchStatus('fetching');
        try {
            const response = await fetch('http://localhost:5000/fetch_products_data', {
                method: 'GET',
            }).then(res => res.json());
            setFetchStatus('fetched');
            console.log('Fetched Data:', response);
            // Handle the response as needed
        } catch (error) {
            setFetchStatus('error');
        }
    };
    return (
        <div style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
            <HomeButton />
            <div className="container" style={{ maxWidth: 400 }}>
                <h1>Fastrax Login</h1>
                <form onSubmit={handleSubmit}>
                    <div className="mb-3 d-flex align-items-center" style={{ gap: '8px' }}>
                        <label htmlFor="exampleFormControlInput1" className="form-label" style={{ marginBottom: 0 }}>Username</label>
                        <input
                            type="text"
                            className="form-control"
                            id="exampleFormControlInput1"
                            placeholder="Enter your username"
                            value={userName}
                            onChange={e => setUserName(e.target.value)}
                            style={{ width: 'auto' }}
                        />
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <label htmlFor="inputPassword6" style={{ marginBottom: 0 }}>Password</label>
                        <input
                            type="password"
                            id="inputPassword6"
                            className="form-control"
                            aria-describedby="passwordHelpInline"
                            style={{ width: 'auto' }}
                            placeholder="Enter your password"
                            value={password}
                            onChange={e => setPassword(e.target.value)}
                        />
                    </div>
                    <button type="submit" className="btn btn-primary">Login</button>
                </form>
                {logInStatus === 'error' && (
                    <div className="mt-3" style={{ color: 'red', fontWeight: 'bold' }}>
                        Login failed. Please check your credentials and try again by re-entering your username and password.
                    </div>
                )}
                {logInStatus === 'Success' && fetchStatus === 'fetching' && (
                    <div className="mt-3 d-flex align-items-center" style={{ fontWeight: 'bold', color: 'blue' }}>
                        <span>Fetching</span>
                        <span className="spinner-border spinner-border-sm ms-2" role="status" aria-hidden="true"></span>
                        <span className="ms-2">{timer}s</span>
                    </div>
                )}
                {logInStatus === 'Success' && fetchStatus === 'fetched' && (
                    <div className="mt-3 d-flex align-items-center" style={{ fontWeight: 'bold', color: 'green' }}>
                        <span>Fetched</span>
                    </div>
                )}
                {/* <Link to="/welcome">Back to Home</Link> */}
            </div>
        </div>
    );
}

export default FastraxLoginPage;