import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import TranslateIcon from '@mui/icons-material/Translate';

const Header = () => {
  return (
    <AppBar position="static" elevation={0} sx={{ backgroundColor: 'white', color: 'primary.main' }}>
      <Toolbar sx={{ justifyContent: 'space-between' }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <TranslateIcon sx={{ mr: 1 }} />
          <Typography
            variant="h5"
            component={RouterLink}
            to="/"
            sx={{
              textDecoration: 'none',
              color: 'primary.main',
              fontWeight: 'bold',
              letterSpacing: '0.5px'
            }}
          >
            InsurSpeak
          </Typography>
        </Box>
        <Box>
          <Button
            component={RouterLink}
            to="/"
            color="primary"
            sx={{ mx: 1 }}
          >
            Home
          </Button>
          <Button
            component={RouterLink}
            to="/document"
            color="primary"
            sx={{ mx: 1 }}
          >
            Process Document
          </Button>
          <Button
            component={RouterLink}
            to="/questions"
            color="primary"
            variant="contained"
            sx={{ mx: 1 }}
          >
            Ask Questions
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
