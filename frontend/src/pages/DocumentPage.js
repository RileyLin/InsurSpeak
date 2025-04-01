import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  Paper,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  Divider,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import TextFieldsIcon from '@mui/icons-material/TextFields';
import { processDocument, setInsuranceType } from '../redux/documentSlice';

const DocumentPage = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { loading, error, insuranceType } = useSelector((state) => state.document);
  
  const [file, setFile] = useState(null);
  const [textContent, setTextContent] = useState('');
  const [inputMethod, setInputMethod] = useState('upload'); // 'upload' or 'paste'
  const [fileName, setFileName] = useState('');

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setFileName(e.target.files[0].name);
    }
  };

  const handleTextChange = (e) => {
    setTextContent(e.target.value);
  };

  const handleInsuranceTypeChange = (e) => {
    dispatch(setInsuranceType(e.target.value));
  };

  const handleInputMethodChange = (method) => {
    setInputMethod(method);
    // Clear inputs when switching methods
    if (method === 'upload') {
      setTextContent('');
    } else {
      setFile(null);
      setFileName('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate inputs
    if (inputMethod === 'upload' && !file) {
      alert('Please select a file to upload');
      return;
    }
    
    if (inputMethod === 'paste' && !textContent.trim()) {
      alert('Please enter some policy text');
      return;
    }
    
    // Prepare payload based on input method
    const payload = {
      insuranceType,
      file: inputMethod === 'upload' ? file : null,
      textContent: inputMethod === 'paste' ? textContent : null,
    };
    
    // Dispatch the process document action
    const resultAction = await dispatch(processDocument(payload));
    
    // If processing was successful, navigate to questions page
    if (processDocument.fulfilled.match(resultAction)) {
      navigate('/questions');
    }
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom align="center" sx={{ mb: 4 }}>
        Upload Your Insurance Document
      </Typography>
      
      <Paper elevation={3} sx={{ p: 4, maxWidth: 800, mx: 'auto' }}>
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}
        
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            Select Insurance Type
          </Typography>
          <FormControl fullWidth>
            <InputLabel id="insurance-type-label">Insurance Type</InputLabel>
            <Select
              labelId="insurance-type-label"
              id="insurance-type"
              value={insuranceType}
              label="Insurance Type"
              onChange={handleInsuranceTypeChange}
            >
              <MenuItem value="health">Health Insurance</MenuItem>
              <MenuItem value="life">Life Insurance</MenuItem>
              <MenuItem value="disability">Disability Insurance</MenuItem>
            </Select>
          </FormControl>
        </Box>
        
        <Divider sx={{ my: 3 }} />
        
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            Input Method
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant={inputMethod === 'upload' ? 'contained' : 'outlined'}
              onClick={() => handleInputMethodChange('upload')}
              startIcon={<CloudUploadIcon />}
            >
              Upload File
            </Button>
            <Button
              variant={inputMethod === 'paste' ? 'contained' : 'outlined'}
              onClick={() => handleInputMethodChange('paste')}
              startIcon={<TextFieldsIcon />}
            >
              Paste Text
            </Button>
          </Box>
        </Box>
        
        <Box component="form" onSubmit={handleSubmit}>
          {inputMethod === 'upload' ? (
            <Box sx={{ mb: 4 }}>
              <Typography variant="subtitle1" gutterBottom>
                Upload your insurance policy document (PDF recommended)
              </Typography>
              <Box
                sx={{
                  border: '2px dashed #ccc',
                  borderRadius: 2,
                  p: 3,
                  textAlign: 'center',
                  bgcolor: 'background.paper',
                  cursor: 'pointer',
                  '&:hover': {
                    bgcolor: 'grey.50',
                  },
                }}
                onClick={() => document.getElementById('file-input').click()}
              >
                <input
                  type="file"
                  id="file-input"
                  accept=".pdf,.doc,.docx,.txt"
                  style={{ display: 'none' }}
                  onChange={handleFileChange}
                />
                <CloudUploadIcon color="primary" sx={{ fontSize: 48, mb: 2 }} />
                <Typography variant="body1" gutterBottom>
                  {fileName || 'Drag and drop or click to select a file'}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Supports PDF, DOC, DOCX, and TXT files
                </Typography>
              </Box>
            </Box>
          ) : (
            <Box sx={{ mb: 4 }}>
              <Typography variant="subtitle1" gutterBottom>
                Paste your insurance policy text below
              </Typography>
              <TextField
                label="Policy Text"
                multiline
                rows={10}
                fullWidth
                value={textContent}
                onChange={handleTextChange}
                placeholder="Copy and paste your insurance policy text here..."
              />
            </Box>
          )}
          
          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2 }}>
            <Button
              type="submit"
              variant="contained"
              color="primary"
              size="large"
              disabled={loading || (inputMethod === 'upload' && !file) || (inputMethod === 'paste' && !textContent.trim())}
              startIcon={loading ? <CircularProgress size={24} color="inherit" /> : null}
            >
              {loading ? 'Processing...' : 'Process Document'}
            </Button>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};

export default DocumentPage;
