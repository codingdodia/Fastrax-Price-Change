import React, { useEffect, useState } from 'react';
import axios from 'axios';


async function fetchWithTimeout(resource: RequestInfo, options: RequestInit = {}, timeout = 10000) {
  return Promise.race([
    fetch(resource, options),
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error("Request timed out")), timeout)
    )
  ]);
}

function PricePreview() {
    const [extractedData, setExtractedData] = useState<any>(null);

    useEffect(() => {

        const extractDataFromPDF = async () => {
            try {
                const response =  await fetch('http://localhost:5000/extract_upcs', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });
                const data = await (response as Response).json();
                console.log('Extracted Data:', data);
                setExtractedData(data);
                //console.log('Extracted Data:', data);
                compareData(data.upcs_and_costs);
            } catch (error) {
                console.error('Error extracting data from PDF:', error);
            }
        };

        const compareData = async (upcs_and_costs: { upc: string; cost: string }[]) => {
            try {

                const response = await fetch('http://localhost:5000/compare_upcs', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ upcs_and_costs: upcs_and_costs }),
                });
                const data = await (response as Response).json();
                console.log('Comparison Result:', data);
                //fetchAndDownloadCSV();
            } catch (error) {
                console.error('Error comparing data:', error);
            }
        }
        const fetchAndDownloadCSV = async () => {
            try {
                const response = await fetch('http://localhost:5000/updated-cost-csv', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.setAttribute('download', 'updated_cost.csv');
                document.body.appendChild(link);
                link.click();
                link.remove();
            } catch (error) {
                console.error('Error downloading CSV:', error);
            }
        };
        extractDataFromPDF();
    }, []);

    // You can now use extractedData for another API call or display

    return (
        <div>
            <h2>Updated Cost</h2>
            <p>Your CSV file should download automatically.</p>
        </div>
    );
}

export default PricePreview;
