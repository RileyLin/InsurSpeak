import React from 'react';
import { Box, Typography, Container, Link } from '@mui/material';

const Footer = () => {
  return (
    <Box
      component="footer"
      sx={{
        py: 3,
        px: 2,
        mt: 'auto',
        backgroundColor: (theme) =>
          theme.palette.mode === 'light'
            ? theme.palette.grey[200]
            : theme.palette.grey[800],
      }}
    >
      <Container maxWidth="sm">
        <Typography variant="body2" color="text.secondary" align="center">
          {'© '}
          {new Date().getFullYear()}
          {' '}
          <Link color="inherit" href="/">
            InsurSpeak
          </Link>
          {' - Making insurance easy to understand.'}
        </Typography>
        <Typography variant="caption" color="text.secondary" align="center" display="block" sx={{ mt: 1 }}>
          Not a substitute for professional legal or insurance advice. Always consult with a licensed professional.
        </Typography>
      </Container>
    </Box>
  );
};

export default Footer;
