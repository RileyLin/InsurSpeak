import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Box, Container } from '@mui/material';
import Header from './components/Header';
import Footer from './components/Footer';
import HomePage from './pages/HomePage';
import DocumentPage from './pages/DocumentPage';
import QuestionsPage from './pages/QuestionsPage';

function App() {
  return (
    <Router>
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column', 
        minHeight: '100vh' 
      }}>
        <Header />
        <Container component="main" sx={{ flexGrow: 1, py: 4 }}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/document" element={<DocumentPage />} />
            <Route path="/questions" element={<QuestionsPage />} />
          </Routes>
        </Container>
        <Footer />
      </Box>
    </Router>
  );
}

export default App;
