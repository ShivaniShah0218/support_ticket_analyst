import { useState, useEffect } from 'react';
import axios from 'axios';

function AnalysisLatestResults() {
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);

    // Function to fetch the latest analysis from the backend
    const fetchLatestAnalysis = async () => {
        setLoading(true);
        try {
            const response = await axios.get('/api/analysis/latest');
            setResults(response.data);
        } catch (error) {
            console.error('Error fetching analysis results:', error);
        } finally {
            setLoading(false);
        }
    };

    // Call fetchLatestAnalysis on component mount
    useEffect(() => {
        fetchLatestAnalysis();
    }, []);

    // Render loading state or the results
    if (loading) {
        return <div>Loading...</div>;
    }

    // If no results, render a message to the user
    if (!results) {
        return <div>No analysis results available.</div>;
    }

    return (
        <div>
            <h2>Latest Analysis</h2>
            <h3>Summary:</h3>
            <p>{results.summary}</p>
            <h3>Ticket Analysis:</h3>
            <ul>
                {results.tickets.map((ticket, index) => (
                    <li key={index}>
                        <h4>{ticket.title}</h4>
                        <p><strong>Category:</strong> {ticket.category}</p>
                        <p><strong>Priority:</strong> {ticket.priority}</p>
                        <p><strong>Notes:</strong> {ticket.notes || 'No additional notes'}</p>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default AnalysisLatestResults;
