import React, { useEffect, useState } from 'react';
import HomeButton from '../Components/HomeButton';
// import axios from 'axios';


async function fetchWithTimeout(resource: RequestInfo, options: RequestInit = {}, timeout = 10000) {
  return Promise.race([
    fetch(resource, options),
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error("Request timed out")), timeout)
    )
  ]);
}


function PricePreview() {
    const [matchedProducts, setMatchedProducts] = useState<any[]>([]);
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
                setMatchedProducts(data || []);
                console.log(data);
                // console.log('Comparison Result:', data);
                // CSV is ready after this, but download is now manual
            } catch (error) {
                console.error('Error comparing data:', error);
            }
        };

        extractDataFromPDF();
    }, []);

    // Download CSV on button click
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

    // You can now use extractedData for another API call or display

    const [changePrices, setChangePrices] = useState<null | boolean>(null);
    // departmentsDict: { [name: string]: number }
    const [departmentsDict, setDepartmentsDict] = useState<{ [name: string]: number }>({});
    // upcDeptMap: { [name: string]: string[] }
    const [upcDeptMap, setUpcDeptMap] = useState<{ [name: string]: string[] }>({});
    const [selectedDept, setSelectedDept] = useState<string>('');
    const [priceValue, setPriceValue] = useState<string>('');
    const [isPercent, setIsPercent] = useState<boolean>(false);

    // Fetch and parse CSV for departments as dict and upcDeptMap when user selects Yes
    useEffect(() => {
        if (changePrices === true) {
            const fetchDepartments = async () => {
                try {
                    const response = await fetch('http://localhost:5000/get_dept_list', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ matched_products: matchedProducts || [] }),
                    });
                    const data = await response.json();
                    console.log('Departments Data:', data);
                    const deptCount = data.deptCount || {};
                    const upcDept = data.upcDept || {};
                    setDepartmentsDict(deptCount);
                    setUpcDeptMap(upcDept);
                } catch (e) {
                    setDepartmentsDict({});
                    setUpcDeptMap({});
                }
            };
            fetchDepartments();
        }
    }, [changePrices]);

    return (
        <div>
            <HomeButton />
            <h2>Updated Cost</h2>
            <div style={{margin: '16px 0'}}>
                <p>Would you like to change prices?</p>
                <button onClick={() => setChangePrices(true)} style={{marginRight: '8px', padding: '6px 14px', background: '#007bff', color: '#fff', border: 'none', borderRadius: '4px'}}>Yes</button>
                <button onClick={() => setChangePrices(false)} style={{padding: '6px 14px', background: '#007bff', color: '#fff', border: 'none', borderRadius: '4px'}}>No</button>
            </div>
            {changePrices === false && (
                <button onClick={fetchAndDownloadCSV} style={{margin: '16px 0', padding: '8px 16px', fontSize: '16px', background: '#007bff', color: '#fff', border: 'none', borderRadius: '4px'}}>Download CSV</button>
            )}
            {changePrices === true && (
                <div style={{margin: '24px 0', padding: '16px', border: '1px solid #ccc', borderRadius: '8px', maxWidth: 400}}>
                    <div style={{marginBottom: '12px'}}>
                        <label htmlFor="department-select">Select Department:</label><br />
                        <select id="department-select" value={selectedDept} onChange={e => setSelectedDept(e.target.value)} style={{width: '100%', padding: '6px', marginTop: '4px'}}>
                            <option value="">-- Select --</option>
                            {Object.entries(departmentsDict).map(([dept, count], idx) => (
                                <option key={idx} value={dept}>{dept} ({count} products)</option>
                            ))}
                        </select>
                    </div>
                    <div style={{marginBottom: '12px'}}>
                        <label>Price Change Value:</label><br />
                        <input type="number" value={priceValue} onChange={e => setPriceValue(e.target.value)} style={{width: '100%', padding: '6px', marginTop: '4px'}} />
                    </div>
                    <div style={{marginBottom: '12px'}}>
                        <label>Change Type:</label><br />
                        <button onClick={() => setIsPercent(false)} style={{marginRight: '8px', padding: '6px 14px', background: !isPercent ? '#007bff' : '#eee', color: !isPercent ? '#fff' : '#000', border: 'none', borderRadius: '4px'}}>Dollar ($)</button>
                        <button onClick={() => setIsPercent(true)} style={{padding: '6px 14px', background: isPercent ? '#007bff' : '#eee', color: isPercent ? '#fff' : '#000', border: 'none', borderRadius: '4px'}}>Percent (%)</button>
                    </div>
                    {/* You can add a submit button here to trigger the update */}
                </div>
            )}
        </div>
    );
}

export default PricePreview;
