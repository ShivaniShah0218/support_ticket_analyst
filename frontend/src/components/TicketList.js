import { useEffect, useState } from 'react';
import axios from 'axios';

function TicketList() {
    const [tickets, setTickets] = useState([]);

    useEffect(() => {
        axios.get('/api/tickets').then((response) => setTickets(response.data));
    }, []);

    return (
        <ul>
            {tickets.map(ticket => (
                <li key={ticket.id}>{ticket.title}</li>
            ))}
        </ul>
    );
}

export default TicketList;
