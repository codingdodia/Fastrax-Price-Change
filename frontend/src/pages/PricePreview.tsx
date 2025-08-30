
import React, { useState, useEffect } from 'react';
import HomeButton from '../Components/HomeButton';
// import axios from 'axios';

type UPCAndCost = {
    upc: string;
    cost: string;
};

function PricePreview() {
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
    // Handler to decline price change
    const handleDeclinePrices = () => {
        setProductsToConfirm(null);
        setOldProducts(null);
        setConfirmationMessage('Price change declined.');
    };
    const [productsToConfirm, setProductsToConfirm] = useState<any[] | null>(null);
    const [oldProducts, setOldProducts] = useState<any[] | null>(null);
    const [confirmationMessage, setConfirmationMessage] = useState<string | null>(null);
    const [matchedProducts, setMatchedProducts] = useState<any[]>([]);
    const [upcList, setUpcList] = useState<string[]>([]);

    // Debug: log matchedProducts and departments
    

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
                setUpcList(data)
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

    const writeToCsv = async () => {
        try {
            const response = await fetch('http://localhost:5000/write_to_csv', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ matched_products: matchedProducts || [], upc_list: upcList }),
            });
            if (!response.ok) {
                throw new Error('Failed to write to CSV');
            }
            console.log('CSV written successfully');
        } catch (error) {
            console.error('Error writing to CSV:', error);
        }
    };

    // Download CSV on button click
    const fetchAndDownloadCSV = async () => {
        try {
            // Call write_to_csv API first
            await writeToCsv();
            // Then download the CSV
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
    const [departments, setDepartments] = useState<{ department_name: string, product_count: string}[]>([]);
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
                    // If response is { deptCount: { 'TOBACCO': 240, ... } }
                    if (data && typeof data === 'object' && data.deptCount && typeof data.deptCount === 'object' && !Array.isArray(data.deptCount)) {
                        const deptArr = Object.entries(data.deptCount).map(([department_name, product_count]) => ({ department_name, product_count: String(product_count) }));
                        setDepartments(deptArr);
                    } else if (data && typeof data === 'object' && !Array.isArray(data) && !data.deptCount) {
                        const deptArr = Object.entries(data).map(([department_name, product_count]) => ({ department_name, product_count: String(product_count) }));
                        setDepartments(deptArr);
                    } else if (data.deptCount && Array.isArray(data.deptCount)) {
                        setDepartments(data.deptCount);
                    } else {
                        setDepartments([]);
                    }
                } catch (e) {
                    setDepartments([]);
                }
            };
            fetchDepartments();
        }
    }, [changePrices]);

    // Handle submit for price update
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedDept || !priceValue) {
            alert('Please select a department and enter a value.');
            return;
        }
        const payload = {
            department: selectedDept,
            value: priceValue,
            isPercent: isPercent,
            upc_list: upcList
        };
        try {
            const response = await fetch('http://localhost:5000/update_prices', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            const data = await response.json();
            console.log('Price Update Response:', data);
            if (data.products_updated && data.old_products) {
                setProductsToConfirm(data.products_updated);
                setOldProducts(data.old_products);
                console.log(data.old_products)
            } else {
                alert('Price update request sent!');
            }
        } catch (error) {
            alert('Error sending price update request.');
        }
    };

    const handleConfirmPrices = async () => {

        const payload = {
            department: selectedDept,
            isPercent: isPercent,
            value: priceValue
        }
        try {
            const response = await fetch('http://localhost:5000/confirm_prices', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            const data = await response.json();
            alert(data.message || 'Prices confirmed!');
            setConfirmationMessage(data.message || 'Prices confirmed!');
            setProductsToConfirm(null);
            setOldProducts(null);
        } catch (error) {
            setConfirmationMessage('Error confirming prices.');
        }
    };

    return (
        <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '100vh',
            width: '100vw',
        }}>
            <div style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                width: '100%',
                maxWidth: 900,
            }}>
                <HomeButton />
                <h2>Updated Cost</h2>
                <div style={{margin: '16px 0', textAlign: 'center'}}>
                    <p>Would you like to change prices?</p>
                    <button onClick={() => setChangePrices(true)} style={{marginRight: '8px', padding: '6px 14px', background: '#007bff', color: '#fff', border: 'none', borderRadius: '4px'}}>Yes</button>
                    <button onClick={() => setChangePrices(false)} style={{padding: '6px 14px', background: '#007bff', color: '#fff', border: 'none', borderRadius: '4px'}}>No</button>
                </div>
                {changePrices === false && (
                    <button onClick={fetchAndDownloadCSV} style={{margin: '16px 0', padding: '8px 16px', fontSize: '16px', background: '#007bff', color: '#fff', border: 'none', borderRadius: '4px'}}>Download CSV</button>
                )}
                {changePrices === true && (
                    <form onSubmit={handleSubmit} style={{margin: '24px 0', padding: '16px', border: '1px solid #ccc', borderRadius: '8px', maxWidth: 400, textAlign: 'center'}}>
                        <div style={{marginBottom: '12px'}}>
                            <label htmlFor="department-select">Select Department:</label><br />
                            <select id="department-select" value={selectedDept} onChange={e => setSelectedDept(e.target.value)} style={{width: '100%', padding: '6px', marginTop: '4px'}}>
                                <option value="">-- Select --</option>
                                {departments.map((dept, idx) => (
                                    <option key={idx} value={dept.department_name}>{dept.department_name} ({dept.product_count} products)</option>
                                ))}
                            </select>
                        </div>
                        <div style={{marginBottom: '12px'}}>
                            <label>Price Change Value:</label><br />
                            <input type="number" value={priceValue} onChange={e => setPriceValue(e.target.value)} style={{width: '100%', padding: '6px', marginTop: '4px'}} />
                        </div>
                        <div style={{marginBottom: '12px'}}>
                            <label>Change Type:</label><br />
                            <button type="button" onClick={() => setIsPercent(false)} style={{marginRight: '8px', padding: '6px 14px', background: !isPercent ? '#007bff' : '#eee', color: !isPercent ? '#fff' : '#000', border: 'none', borderRadius: '4px'}}>Dollar ($)</button>
                            <button type="button" onClick={() => setIsPercent(true)} style={{padding: '6px 14px', background: isPercent ? '#007bff' : '#eee', color: isPercent ? '#fff' : '#000', border: 'none', borderRadius: '4px'}}>Percent (%)</button>
                        </div>
                        <button type="submit" style={{marginTop: '12px', padding: '8px 16px', background: '#007bff', color: '#fff', border: 'none', borderRadius: '4px', fontSize: '16px'}}>Submit</button>
                    </form>
                )}
                {productsToConfirm && oldProducts && (
                    <div style={{marginTop: '32px', width: '100%', maxWidth: 800, textAlign: 'center'}}>
                        <h3>Confirm Price Updates</h3>
                        <table style={{width: '100%', borderCollapse: 'collapse', marginBottom: '16px', marginLeft: 'auto', marginRight: 'auto'}}>
                            <thead>
                                <tr>
                                    <th style={{border: '1px solid #ccc', padding: '8px'}}>Product Name</th>
                                    <th style={{border: '1px solid #ccc', padding: '8px'}}>Old Price</th>
                                    <th style={{border: '1px solid #ccc', padding: '8px'}}>New Price</th>
                                    <th style={{border: '1px solid #ccc', padding: '8px'}}>Old Cost</th>
                                    <th style={{border: '1px solid #ccc', padding: '8px'}}>New Cost</th>
                                </tr>
                            </thead>
                            <tbody>
                                {productsToConfirm.map((prod, idx) => {
                                    // Try to get old and new cost from both arrays
                                    const oldProd = oldProducts[idx] || {};
                                    return (
                                        <tr key={prod.upc || idx}>
                                            <td style={{border: '1px solid #ccc', padding: '8px'}}>{prod.name || prod.product_name || prod.upc}</td>
                                            <td style={{border: '1px solid #ccc', padding: '8px'}}>{oldProd.price ?? 'N/A'}</td>
                                            <td style={{border: '1px solid #ccc', padding: '8px'}}>{prod.price}</td>
                                            <td style={{border: '1px solid #ccc', padding: '8px'}}>{oldProd.cost ?? oldProd.old_cost ?? 'N/A'}</td>
                                            <td style={{border: '1px solid #ccc', padding: '8px'}}>{prod.cost ?? prod.new_cost ?? 'N/A'}</td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                        <div style={{display: 'flex', justifyContent: 'center', gap: '16px', marginTop: '8px'}}>
                            <button
                                onClick={handleConfirmPrices}
                                style={{
                                    padding: '8px 16px',
                                    background: '#28a745',
                                    color: '#fff',
                                    border: 'none',
                                    borderRadius: '4px',
                                    fontSize: '16px',
                                    cursor: 'pointer',
                                }}
                            >
                                Confirm Prices
                            </button>
                            <button
                                onClick={handleDeclinePrices}
                                title="Decline Price Change"
                                style={{
                                    padding: '8px 16px',
                                    background: '#dc3545',
                                    color: '#fff',
                                    border: 'none',
                                    borderRadius: '4px',
                                    fontSize: '16px',
                                    cursor: 'pointer',
                                }}
                            >
                                X
                            </button>
                        </div>
                        {confirmationMessage && <div style={{marginTop: '12px', color: '#007bff'}}>{confirmationMessage}</div>}
                    </div>
                )}
                {confirmationMessage && changePrices !== false && (
                    <button
                        onClick={fetchAndDownloadCSV}
                        style={{
                            margin: '16px 0',
                            padding: '8px 16px',
                            fontSize: '16px',
                            background: '#007bff',
                            color: '#fff',
                            border: 'none',
                            borderRadius: '4px'
                        }}
                    >
                        Download CSV
                    </button>
                )}
            </div>
        </div>
    );
}

export default PricePreview;
