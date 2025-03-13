interface Message {
    id: number;
    text: string;
    sender: 'user' | 'bot';
    timestamp: Date;
}

interface MessageBubbleProps {
    message: Message;
    username: string;
}

function MessageBubble({ message, username }: MessageBubbleProps) {
    const { text, sender, timestamp } = message;
    const isUser = sender === 'user';
    const formattedTime = new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    return (
        <div className={`flex mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] rounded-lg px-4 py-2 ${isUser
                ? 'bg-blue-600 text-white rounded-br-none'
                : 'bg-white text-gray-800 rounded-bl-none shadow-sm'
                }`}>
                <div className="font-medium text-sm mb-1">
                    {isUser ? username : 'Intervue Bot'}
                </div>
                <div className="whitespace-pre-wrap">{text}</div>
                <div className={`text-xs mt-1 text-right ${isUser ? 'text-blue-200' : 'text-gray-500'}`}>
                    {formattedTime}
                </div>
            </div>
        </div>
    );
}

export default MessageBubble;