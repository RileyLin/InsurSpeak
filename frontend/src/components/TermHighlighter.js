import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Popper, 
  Fade, 
  Divider, 
  Chip
} from '@mui/material';

/**
 * Component that displays text with highlighted insurance terms
 * When a user clicks on a highlighted term, a popover displays with the explanation
 */
const TermHighlighter = ({ text, terms, maxHeight }) => {
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedTerm, setSelectedTerm] = useState(null);
  const open = Boolean(anchorEl);

  // If no text or terms, display a placeholder
  if (!text || !terms || terms.length === 0) {
    return (
      <Typography variant="body1" gutterBottom>
        No document content available.
      </Typography>
    );
  }

  // Handle click on a highlighted term
  const handleTermClick = (event, term) => {
    setSelectedTerm(term);
    setAnchorEl(anchorEl ? null : event.currentTarget);
  };

  // Close the popover
  const handleClose = () => {
    setAnchorEl(null);
  };

  // Sort terms by start index to process in order
  const sortedTerms = [...terms].sort((a, b) => a.start_index - b.start_index);
  
  // Build the highlighted text
  let lastIndex = 0;
  const textParts = [];

  sortedTerms.forEach((term, index) => {
    // Add text before this term
    if (term.start_index > lastIndex) {
      textParts.push(
        <span key={`text-${lastIndex}`}>
          {text.substring(lastIndex, term.start_index)}
        </span>
      );
    }

    // Add the highlighted term
    textParts.push(
      <span 
        key={`term-${term.start_index}`}
        className={`highlighted-term term-${term.category}`}
        onClick={(e) => handleTermClick(e, term)}
        style={{ cursor: 'pointer' }}
      >
        {text.substring(term.start_index, term.end_index)}
      </span>
    );

    lastIndex = term.end_index;
  });

  // Add any remaining text after the last term
  if (lastIndex < text.length) {
    textParts.push(
      <span key={`text-${lastIndex}`}>
        {text.substring(lastIndex)}
      </span>
    );
  }

  return (
    <>
      <Box sx={{ 
        whiteSpace: 'pre-wrap', 
        overflow: 'auto', 
        maxHeight: maxHeight || '400px',
        p: 1
      }}>
        {textParts}
      </Box>

      {/* Popover for term explanation */}
      <Popper
        open={open}
        anchorEl={anchorEl}
        placement="top"
        transition
        sx={{ zIndex: 1300 }}
      >
        {({ TransitionProps }) => (
          <Fade {...TransitionProps} timeout={350}>
            <Paper sx={{ 
              p: 2, 
              maxWidth: 350, 
              boxShadow: 3, 
              borderLeft: '4px solid', 
              borderColor: 'primary.main' 
            }}>
              {selectedTerm && (
                <>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                    <Typography variant="h6" component="h3">{selectedTerm.term}</Typography>
                    <Chip 
                      label={selectedTerm.category} 
                      size="small" 
                      color="primary" 
                      variant="outlined" 
                    />
                  </Box>
                  <Divider sx={{ mb: 2 }} />
                  
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Explanation:
                  </Typography>
                  <Typography variant="body2" paragraph>
                    {selectedTerm.explanation}
                  </Typography>
                  
                  {selectedTerm.implications && (
                    <>
                      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                        What this means for you:
                      </Typography>
                      <Typography variant="body2">
                        {selectedTerm.implications}
                      </Typography>
                    </>
                  )}
                </>
              )}
            </Paper>
          </Fade>
        )}
      </Popper>
    </>
  );
};

export default TermHighlighter;
