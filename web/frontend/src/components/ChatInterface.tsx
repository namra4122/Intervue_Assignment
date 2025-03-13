import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import MessageBuble from "./MessageBuble";

interface SessionInfo {
    username: string;
    sessionId: string;
    isInit: boolean;
    currentNode?: string;
}

interface ChatInterfaceProps {
    sessionInfo: SessionInfo;
    setSessionInfo: React.Dispatch<React.SetStateAction<SessionInfo>>;
}

interface Message {
    id: number;
    text: string;
    sender: 'user' | 'bot';
    timestamp: Date;
}

function ChatInterface({ sessionInfo, setSessionInfo }: ChatInterfaceProps) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputMessage, setInputMessage] = useState<string>('');
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string>('');
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const navigate = useNavigate();

    useEffect(() => {
        const savedMessages = localStorage.getItem('chatMessages');
        if (savedMessages) {
            setMessages(JSON.parse(savedMessages));
        }
    }, [sessionInfo.username]);
    // asd
    useEffect(() => {
        scrollToBottom();
        if (messages.length > 0) {
            localStorage.setItem('chatMessages', JSON.stringify(messages));
        }
    }, [messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }

    const sendMessage = async () => {
        if (!inputMessage.trim()) return;

        const userMessage: Message = {
            id: messages.length + 1,
            text: inputMessage,
            sender: 'user',
            timestamp: new Date()
        };

        setMessages((prevMessages) => [...prevMessages, userMessage]);
        setInputMessage('');
        setIsLoading(true);
        setError('');

        try {
            const response = await fetch('http://0.0.0.0:8000/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: sessionInfo.sessionId,
                    message: inputMessage,
                })
            });

            if (!response.ok) {
                throw new Error('Failed to send message');
            }

            const data = await response.json();
            console.log(data)
            setMessages((prevMessages) => [...prevMessages, {
                id: prevMessages.length + 2,
                text: data.response,
                sender: 'bot',
                timestamp: new Date()
            }]);

            if (data.session_id !== sessionInfo.sessionId) {
                setSessionInfo(prev => ({
                    ...prev,
                    sessionId: data.session_id,
                    currentNode: data.current_node
                }));
            }
        } catch (error) {
            setError((error as Error).message || 'Failed to send message');
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === "Enter" && !e.shiftKey) {
            {
                e.preventDefault();
                sendMessage();
            }
        }
    };

    const resetChat = async () => {
        setIsLoading(true);
        setError('');

        try {
            const response = await fetch('http://0.0.0.0:8000/api/reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: sessionInfo.sessionId
                }),
            });

            if (!response.ok) {
                throw new Error('Failed to reset chat');
            }

            const data = await response.json();

            setMessages([
                {
                    id: 1,
                    text: data.response || `Chat has been reset. How can I help you, ${sessionInfo.username}?`,
                    sender: 'bot',
                    timestamp: new Date()
                }
            ]);

            if (data.session_id !== sessionInfo.sessionId) {
                setSessionInfo(prev => ({
                    ...prev,
                    sessionId: data.session_id,
                    currentNode: data.current_node
                }));
            }
        } catch (error) {
            setError((error as Error).message || 'An error occurred while resetting the chat');
        } finally {
            setIsLoading(false);
        }
    };

    const startNewChat = () => {
        localStorage.removeItem('chatSession');
        localStorage.removeItem('chatMessages');
        setSessionInfo({
            username: '',
            sessionId: '',
            isInit: false
        });
        navigate('/');
    };

    return (
        <div className="flex flex-col h-screen">
            {/* Header */}
            <header className="bg-blue-600 text-white p-4 shadow-md">
                <div className="container mx-auto flex justify-between items-center">
                    <h1 className="text-xl font-bold">Interview Bot</h1>
                    <div className="flex gap-2">
                        <button
                            onClick={resetChat}
                            disabled={isLoading}
                            className="bg-blue-500 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm transition duration-200"
                        >
                            Reset Chat
                        </button>
                        <button
                            onClick={startNewChat}
                            disabled={isLoading}
                            className="bg-gray-600 hover:bg-gray-700 text-white px-3 py-1 rounded text-sm transition duration-200"
                        >
                            New Session
                        </button>
                    </div>
                </div>
            </header>

            {/* Chat messages container */}
            <div className="flex-1 bg-gray-100 p-4 overflow-y-auto">
                <div className="container mx-auto max-w-3xl">
                    {messages.map((message) => (
                        <MessageBuble
                            key={message.id}
                            message={message}
                            username={sessionInfo.username}
                        />
                    ))}
                    {isLoading && (
                        <div className="flex justify-center my-4">
                            <div className="typing-indicator bg-gray-200 p-3 rounded-lg inline-flex items-center">
                                <span className="dot"></span>
                                <span className="dot"></span>
                                <span className="dot"></span>
                            </div>
                        </div>
                    )}
                    {error && (
                        <div className="p-3 my-2 bg-red-100 text-red-700 rounded-lg">
                            {error}
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>
            </div>

            {/* Message input form */}
            <div className="bg-white border-t border-gray-200 p-4">
                <div className="container mx-auto max-w-3xl">
                    <div className="flex items-end gap-2">
                        <textarea
                            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none max-h-32"
                            placeholder="Type your message..."
                            value={inputMessage}
                            onChange={(e) => setInputMessage(e.target.value)}
                            onKeyDown={handleKeyPress}
                            disabled={isLoading}
                            rows={2}
                        />
                        <button
                            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition duration-200 disabled:bg-blue-400"
                            onClick={sendMessage}
                            disabled={!inputMessage.trim() || isLoading}
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z" clipRule="evenodd" />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default ChatInterface;