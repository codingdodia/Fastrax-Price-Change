import React, { useState, useEffect } from 'react';
import { useNavigate } from "react-router-dom";
// Import HomeButton if it exists in your components folder
import HomeButton from '../Components/HomeButton';

type uploadStatus = 'idle' | 'uploading' | 'success' | 'error';

function PriceChange() {
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

    // ...existing code...
    const navigate = useNavigate();
    const [file, setFile] = useState<File | null>(null);
    const [status, setStatus] = useState<uploadStatus>('idle');

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            setFile(e.target.files[0]);
        }
    };

    const handleSuccess = () => {
        navigate('/ChangePricePreview');
    }

    const onSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (!file) return;
        setStatus('uploading');
        const formData = new FormData();
        formData.append('file', file);
        try {
            const response = await fetch('http://localhost:5000/upload', {
                method: 'POST',
                body: formData,
            });
            setStatus('success');
            handleSuccess();
            const responseData = await response.json();
            console.log(responseData);
        } catch (error) {
            setStatus('error');
            console.error(error);
        }
    }

        return (
                <div style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
                        <HomeButton />
                        <div className="space-y-2" style={{ padding: '1rem' }}>
                                <h1>Price Change</h1>
                                <p>Upload a PDF file to change the price.</p>
                                <p> File name: {file?.name}</p>
                                <p
                                    style={
                                        status === 'uploading'
                                            ? { color: 'blue', fontWeight: 'bold' }
                                            : status === 'success'
                                            ? { color: 'green', fontWeight: 'bold' }
                                            : status === 'error'
                                            ? { color: 'red', fontWeight: 'bold' }
                                            : { color: 'gray' }
                                    }
                                >
                                    {status === 'uploading'
                                        ? 'Uploading...'
                                        : status === 'success'
                                        ? 'Upload successful!'
                                        : status === 'error'
                                        ? 'Upload failed.'
                                        : 'Waiting for upload'}
                                </p>
                                <form onSubmit={onSubmit}>
                                        {uploadFile(handleFileChange)}
                                        <button type="submit" className="btn btn-primary">Submit</button>
                                </form>
                        </div>
                </div>
        );
}

function uploadFile(handleFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void) {
    return (
        <div className="mb-3">
            <label htmlFor="formFile" className="form-label">Upload File</label>
            <input className="form-control" type="file" id="formFile" accept="application/pdf" onChange={handleFileChange} />
        </div>
    );
}

export default PriceChange;