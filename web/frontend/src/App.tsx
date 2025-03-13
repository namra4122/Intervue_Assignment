import './App.css'
import { useEffect, useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import WelcomePage from './components/WelcomePage';
import ChatInterface from './components/ChatInterface';
function App() {
  console.log("app.tsx")
  const [sessionInfo, setSessionInfo] = useState({
    username: '',
    sessionId: '',
    isInit: false
  });

  useEffect(() => {
    const savedSession = localStorage.getItem('chatsession');
    if (savedSession) {
      setSessionInfo(JSON.parse(savedSession));
    }
  }, []);

  useEffect(() => {
    if (sessionInfo.sessionId) {
      localStorage.setItem('chatSession', JSON.stringify(sessionInfo));
    }
  }, [sessionInfo]);

  return (
    <div className='min-h-screen bg-gray-400'>
      <Router>
        <Routes>
          <Route
            path="/"
            element={
              sessionInfo.isInit ?
                <Navigate to="/chat" /> :
                <WelcomePage setSessionInfo={setSessionInfo} />
            }
          />

          <Route
            path="/chat"
            element={
              !sessionInfo.isInit ?
                <Navigate to="/" /> :
                <ChatInterface sessionInfo={sessionInfo} setSessionInfo={setSessionInfo} />
            }
          />

        </Routes>
      </Router>
    </div>
  )
}

export default App
