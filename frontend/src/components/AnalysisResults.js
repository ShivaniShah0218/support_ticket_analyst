import { useState } from 'react';
import axios from 'axios';

function AnalysisResults() {
    const [results, setResults] = useState(null);

    const analyzeTickets = async () => {
        const response = await axios.post('/api/analyze');
        setResults(response.data);
    };

    return (
        <div>
            <button onClick={analyzeTickets}>Analyze Tickets</button>
            {results && (
                <div>
                    <h3>Summary: {results.summary}</h3>
                    <ul>
                        {results.tickets.map((ticket, index) => (
                            <li key={index}>
                                <h4>{ticket.title}</h4>
                                <p>Category: {ticket.category}</p>
                                <p>Priority: {ticket.priority}</p>
                                <p>Notes: {ticket.notes}</p>
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}

export default AnalysisResults;
