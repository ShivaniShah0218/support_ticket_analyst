import logo from './logo.svg';
import './App.css';
import TicketForm from './components/TicketForm';
import TicketList from './components/TicketList';
import AnalysisResults from './components/AnalysisResults';
import AnalysisLatestResults from './components/AnalysisLatestResults';

function App() {
    return (
        <div>
            <h1>Support Ticket Analyst</h1>
            <TicketForm />
            <TicketList />
            <AnalysisResults />
            <AnalysisLatestResults />
        </div>
    );
}

export default App;
