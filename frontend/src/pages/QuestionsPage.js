import React, { useState, useEffect, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Divider,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  IconButton,
  Chip,
  Tooltip,
  Grid,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import InfoIcon from '@mui/icons-material/Info';
import QuestionAnswerIcon from '@mui/icons-material/QuestionAnswer';
import LightbulbIcon from '@mui/icons-material/Lightbulb';
import PersonIcon from '@mui/icons-material/Person';
import { askQuestion, setCurrentQuestion } from '../redux/questionSlice';
import TermHighlighter from '../components/TermHighlighter';

const QuestionsPage = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const inputRef = useRef(null);
  
  const { 
    originalText, 
    terms, 
    insuranceType, 
    isDocumentProcessed, 
    loading: documentLoading 
  } = useSelector((state) => state.document);
  
  const { 
    questions, 
    loading: questionLoading, 
    error,
    currentQuestion 
  } = useSelector((state) => state.questions);

  const [showExamples, setShowExamples] = useState(true);

  // Sample questions based on insurance type
  const exampleQuestions = {
    health: [
      "What is my deductible?",
      "Are pre-existing conditions covered?",
      "How much will I pay for out-of-network care?",
      "What happens if I visit the emergency room?",
      "Is therapy covered under my plan?"
    ],
    life: [
      "What happens if I miss a premium payment?",
      "Can I change my beneficiary?",
      "Is suicide covered under this policy?",
      "What is the cash value of this policy?",
      "Is accidental death covered differently?"
    ],
    disability: [
      "What is the elimination period?",
      "How is 'disability' defined in this policy?",
      "What percentage of my income will be replaced?",
      "Is my specific occupation covered?",
      "What happens if I can work part-time but not full-time?"
    ]
  };

  // Check if there's a document uploaded or pasted
  useEffect(() => {
    if (!isDocumentProcessed && !documentLoading) {
      // If no document has been processed, show a message
      // Can optionally redirect to document upload page
    }
  }, [isDocumentProcessed, documentLoading, navigate]);

  const handleQuestionChange = (e) => {
    dispatch(setCurrentQuestion(e.target.value));
  };

  const handleSubmitQuestion = async (e) => {
    e.preventDefault();
    
    if (!currentQuestion.trim()) {
      return;
    }
    
    if (!originalText) {
      alert('Please upload or paste a document first');
      navigate('/document');
      return;
    }
    
    await dispatch(askQuestion({
      question: currentQuestion,
      documentText: originalText,
      insuranceType
    }));
    
    // Focus on the input after submission
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  const handleExampleClick = (question) => {
    dispatch(setCurrentQuestion(question));
    if (inputRef.current) {
      inputRef.current.focus();
    }
    setShowExamples(false);
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom align="center" sx={{ mb: 4 }}>
        Ask Questions About Your Insurance
      </Typography>
      
      {!isDocumentProcessed && !documentLoading ? (
        <Paper elevation={3} sx={{ p: 4, maxWidth: 800, mx: 'auto', mb: 4 }}>
          <Alert severity="info" sx={{ mb: 3 }}>
            No insurance document has been processed yet. Please upload or paste your document first.
          </Alert>
          <Box sx={{ display: 'flex', justifyContent: 'center' }}>
            <Button
              variant="contained"
              color="primary"
              onClick={() => navigate('/document')}
            >
              Process Document
            </Button>
          </Box>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {/* Left column: Document display */}
          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 3, height: '100%', minHeight: '300px', overflow: 'auto' }}>
              <Typography variant="h6" gutterBottom>
                Your {insuranceType.charAt(0).toUpperCase() + insuranceType.slice(1)} Insurance Document
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Box sx={{ mb: 2 }}>
                {documentLoading ? (
                  <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                    <CircularProgress />
                  </Box>
                ) : (
                  <TermHighlighter 
                    text={originalText} 
                    terms={terms} 
                    maxHeight="400px"
                  />
                )}
              </Box>
            </Paper>
          </Grid>
          
          {/* Right column: Q&A */}
          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" gutterBottom>
                Ask a Question
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              {/* Question input form */}
              <Box component="form" onSubmit={handleSubmitQuestion} sx={{ mb: 3 }}>
                <TextField
                  inputRef={inputRef}
                  label="Type your question about the policy..."
                  fullWidth
                  value={currentQuestion}
                  onChange={handleQuestionChange}
                  variant="outlined"
                  sx={{ mb: 2 }}
                  InputProps={{
                    endAdornment: (
                      <Button
                        type="submit"
                        disabled={!currentQuestion.trim() || questionLoading}
                        color="primary"
                        sx={{ minWidth: 'auto', p: 1 }}
                      >
                        {questionLoading ? <CircularProgress size={24} /> : <SendIcon />}
                      </Button>
                    ),
                  }}
                />
              </Box>
              
              {/* Error message if question fails */}
              {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                  {error}
                </Alert>
              )}
              
              {/* Example questions */}
              {showExamples && exampleQuestions[insuranceType] && questions.length === 0 && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                    <LightbulbIcon fontSize="small" sx={{ mr: 1, color: 'warning.main' }} />
                    Example questions you can ask:
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {exampleQuestions[insuranceType].map((question, index) => (
                      <Chip
                        key={index}
                        label={question}
                        onClick={() => handleExampleClick(question)}
                        clickable
                        color="primary"
                        variant="outlined"
                        sx={{ mb: 1 }}
                      />
                    ))}
                  </Box>
                </Box>
              )}
              
              {/* Questions and answers */}
              <Box sx={{ maxHeight: '500px', overflow: 'auto' }}>
                {questions.length > 0 ? (
                  [...questions].reverse().map((qa) => (
                    <Card key={qa.id} sx={{ mb: 2, backgroundColor: 'background.paper' }}>
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 1 }}>
                          <PersonIcon sx={{ mr: 1, color: 'primary.main' }} />
                          <Typography variant="subtitle1" fontWeight="bold">
                            {qa.question}
                          </Typography>
                        </Box>
                        <Divider sx={{ my: 1 }} />
                        <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
                          <QuestionAnswerIcon sx={{ mr: 1, mt: 0.5, color: 'secondary.main' }} />
                          <Typography variant="body1">
                            {qa.answer}
                          </Typography>
                        </Box>
                      </CardContent>
                    </Card>
                  ))
                ) : (
                  <Box sx={{ textAlign: 'center', py: 4, color: 'text.secondary' }}>
                    <QuestionAnswerIcon sx={{ fontSize: 48, mb: 2, opacity: 0.7 }} />
                    <Typography>
                      Ask a question about your insurance policy to get started
                    </Typography>
                  </Box>
                )}
              </Box>
              
              {/* Disclaimer */}
              <Box sx={{ mt: 3, display: 'flex', alignItems: 'center' }}>
                <InfoIcon color="action" fontSize="small" sx={{ mr: 1 }} />
                <Typography variant="caption" color="text.secondary">
                  The answers provided are for informational purposes and should not be considered legal or professional advice.
                </Typography>
              </Box>
            </Paper>
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default QuestionsPage;
