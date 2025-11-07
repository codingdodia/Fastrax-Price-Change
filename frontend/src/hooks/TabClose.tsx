import { useEffect } from 'react';
import { apiCall } from '../config/api';

export const useTabCloseHandler = () => {
    useEffect(() => {
        const handleBeforeUnload = async () => {
            try {
                await fetch(apiCall('/shutdown'), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });
            } catch (error) {
                console.error('Error during shutdown:', error);
            }
        };

        const handleUnload = () => {
            try {
                // Use sendBeacon for more reliable cleanup on page unload
                navigator.sendBeacon(apiCall('/shutdown'), 
                    new Blob([JSON.stringify({})], { type: 'application/json' })
                );
            } catch (error) {
                console.error('Error during beacon shutdown:', error);
            }
        };

        // Add event listeners
        window.addEventListener('beforeunload', handleBeforeUnload);
        window.addEventListener('unload', handleUnload);

        // Cleanup
        return () => {
            window.removeEventListener('beforeunload', handleBeforeUnload);
            window.removeEventListener('unload', handleUnload);
        };
    }, []);
};