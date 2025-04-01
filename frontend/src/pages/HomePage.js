import React from 'react';
import { 
  Box, 
  Typography, 
  Button, 
  Card, 
  CardContent, 
  Grid, 
  Container 
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import DescriptionIcon from '@mui/icons-material/Description';
import QuestionAnswerIcon from '@mui/icons-material/QuestionAnswer';
import TranslateIcon from '@mui/icons-material/Translate';

const HomePage = () => {
  const navigate = useNavigate();

  return (
    <Container>
      {/* Hero Section */}
      <Box
        sx={{
          textAlign: 'center',
          py: 6,
          px: 2,
          mb: 6
        }}
      >
        <Typography variant="h3" component="h1" gutterBottom fontWeight="bold">
          Understand Your Insurance in Plain English
        </Typography>
        <Typography variant="h5" color="text.secondary" sx={{ mb: 4 }}>
          InsurSpeak translates complex insurance jargon into simple, easy-to-understand language
        </Typography>
        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, flexWrap: 'wrap' }}>
          <Button 
            variant="contained" 
            color="primary" 
            size="large"
            onClick={() => navigate('/document')}
            startIcon={<DescriptionIcon />}
          >
            Upload Your Policy
          </Button>
          <Button 
            variant="contained" 
            color="secondary" 
            size="large"
            onClick={() => navigate('/questions')}
            startIcon={<QuestionAnswerIcon />}
          >
            Ask Questions
          </Button>
        </Box>
      </Box>

      {/* How it Works Section */}
      <Typography variant="h4" component="h2" gutterBottom sx={{ mb: 4, textAlign: 'center' }}>
        How It Works
      </Typography>
      <Grid container spacing={4} sx={{ mb: 8 }}>
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent sx={{ textAlign: 'center', py: 4 }}>
              <DescriptionIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
              <Typography variant="h5" component="h3" gutterBottom>
                Upload Your Document
              </Typography>
              <Typography color="text.secondary">
                Upload or paste your insurance policy document. We support various formats including PDF.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent sx={{ textAlign: 'center', py: 4 }}>
              <TranslateIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
              <Typography variant="h5" component="h3" gutterBottom>
                View Simplified Terms
              </Typography>
              <Typography color="text.secondary">
                We highlight complex insurance terms and provide simple explanations to help you understand.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent sx={{ textAlign: 'center', py: 4 }}>
              <QuestionAnswerIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
              <Typography variant="h5" component="h3" gutterBottom>
                Ask Specific Questions
              </Typography>
              <Typography color="text.secondary">
                Ask questions about your policy in plain language and get straightforward answers.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Insurance Types Section */}
      <Typography variant="h4" component="h2" gutterBottom sx={{ mb: 4, textAlign: 'center' }}>
        Insurance Types We Support
      </Typography>
      <Grid container spacing={3} sx={{ mb: 6 }}>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="h3" gutterBottom sx={{ color: 'primary.main' }}>
                Health Insurance
              </Typography>
              <Typography>
                Understand your health benefits, coverage limits, in-network providers, copays, and more.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="h3" gutterBottom sx={{ color: 'primary.main' }}>
                Life Insurance
              </Typography>
              <Typography>
                Clarify terms about beneficiaries, death benefits, cash values, and policy exclusions.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="h3" gutterBottom sx={{ color: 'primary.main' }}>
                Disability Insurance
              </Typography>
              <Typography>
                Decode elimination periods, own-occupation vs. any-occupation, and benefit calculations.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Get Started CTA */}
      <Box sx={{ textAlign: 'center', py: 6 }}>
        <Typography variant="h4" component="h2" gutterBottom>
          Ready to Understand Your Insurance?
        </Typography>
        <Button 
          variant="contained" 
          color="secondary" 
          size="large"
          onClick={() => navigate('/questions')}
          sx={{ mt: 2 }}
        >
          Get Started Now
        </Button>
      </Box>
    </Container>
  );
};

export default HomePage;
