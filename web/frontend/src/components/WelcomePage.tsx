import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { v4 as uuidv4 } from 'uuid';

interface SessionInfo {
    username: string;
    sessionId: string;
    isInit: boolean;
}

interface WelcomePageProps {
    setSessionInfo: React.Dispatch<React.SetStateAction<SessionInfo>>;
}

interface WelcomePageState {
    username: string;
    isLoading: boolean;
    error: string;
}

function WelcomePage({ setSessionInfo }: WelcomePageProps) {
    const [state, setState] = useState<WelcomePageState>({
        username: '',
        isLoading: false,
        error: '',
    });
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (!state.username.trim()) {
            setState({ ...state, error: 'Please enter your name' });
            return;
        }

        setState({ ...state, isLoading: true, error: '' });

        const sessionId = uuidv4();

        try {
            const response = await fetch('http://0.0.0.0:8000/api/init', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: state.username,
                    session_id: sessionId
                }),
            });

            if (!response.ok) {
                throw new Error('Failed to initialize session');
            }

            const data = await response.json();
            console.log(data);

            const initalMessages = [{
                id: 1,
                text: data.response,
                sender: 'bot',
                timestamp: new Date()
            }];

            console.log(JSON.stringify(initalMessages));

            localStorage.setItem('chatMessages', JSON.stringify(initalMessages));

            setSessionInfo({
                username: state.username,
                sessionId: data.session_id || sessionId,
                isInit: true,
            });
            navigate('/chat');
        } catch (error) {
            setState({ ...state, error: (error as Error).message || 'Failed to initialize session' });
        } finally {
            setState({ ...state, isLoading: false });
        }
    };

    return (
        <div className=" flex items-center justify-center min-h-screen bg-gradient-to-b from-blue-100 to-white p-4">
            <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full">
                <h1 className="text-3xl font-bold text-center text-gray-800 mb-6">
                    Welcome to Intervue Bot
                </h1>
                <p className="text-center text-gray-600 mb-8">
                    Please enter your name to begin the interview session.
                </p>
                <form onSubmit={handleSubmit}>
                    <div className="mb-6">
                        <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="username">
                            Your Name
                        </label>
                        <input
                            type="text"
                            id="username"
                            value={state.username}
                            onChange={(e) => setState({ ...state, username: e.target.value })}
                            placeholder="Enter your name"
                            className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            disabled={state.isLoading}
                        />
                    </div>
                    {state.error && (
                        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg">
                            {state.error}
                        </div>
                    )}
                    <button
                        type="submit"
                        disabled={state.isLoading}
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 transition duration-200"
                    >
                        {state.isLoading ? 'Initializing...' : 'Start Interview'}
                    </button>
                </form>
            </div>
        </div>
    )
}

export default WelcomePage;