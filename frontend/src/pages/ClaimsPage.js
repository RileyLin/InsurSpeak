import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  TextField,
  Card,
  CardContent,
  Grid,
  Container,
  Alert,
  AlertTitle,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  CircularProgress,
  Paper,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import DescriptionIcon from '@mui/icons-material/Description';
import AssignmentTurnedInIcon from '@mui/icons-material/AssignmentTurnedIn';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import InfoIcon from '@mui/icons-material/Info';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import LocationOnIcon from '@mui/icons-material/LocationOn';

const ClaimsPage = () => {
  const navigate = useNavigate();
  const [situation, setSituation] = useState('');
  const [incidentDate, setIncidentDate] = useState('');
  const [location, setLocation] = useState('');
  const [estimatedCost, setEstimatedCost] = useState('');
  const [category, setCategory] = useState('');
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState(null);

  const categories = [
    'Medical/Health',
    'Auto Accident',
    'Travel Disruption',
    'Property Damage',
    'Theft/Loss',
    'Disability/Injury',
    'Other'
  ];

  const exampleSituations = [
    "My flight was delayed 6 hours and I had to book a hotel",
    "I was in a car accident and my vehicle was damaged",
    "I had to go to the emergency room for chest pain",
    "My luggage was lost by the airline",
    "I slipped and fell at work and injured my back"
  ];

  const handleAnalyze = async () => {
    if (!situation.trim()) {
      setError('Please describe your situation');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('situation', situation);
      if (incidentDate) formData.append('incident_date', incidentDate);
      if (location) formData.append('location', location);
      if (estimatedCost) formData.append('estimated_cost', estimatedCost);
      if (category) formData.append('category', category);

      // Get token from localStorage (you'll need to implement auth state management)
      const token = localStorage.getItem('access_token');

      const response = await fetch('http://localhost:8000/analyze-situation', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to analyze situation');
      }

      setAnalysis(data);
    } catch (err) {
      setError(err.message || 'Failed to analyze situation. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  const getLikelihoodColor = (likelihood) => {
    switch (likelihood?.toLowerCase()) {
      case 'high': return 'success';
      case 'medium': return 'warning';
      case 'low': return 'error';
      default: return 'default';
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ textAlign: 'center', mb: 6 }}>
        <Typography variant="h3" component="h1" gutterBottom fontWeight="bold">
          Get Claim Recommendations
        </Typography>
        <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
          Describe what happened, and we'll tell you what you can claim
        </Typography>
        <Alert severity="info" sx={{ maxWidth: '800px', mx: 'auto' }}>
          <AlertTitle>How It Works</AlertTitle>
          Tell us about your situation, and our AI will analyze all your insurance policies to find
          what claims you can file, required documents, and step-by-step guidance.
        </Alert>
      </Box>

      {/* Input Section */}
      {!analysis && (
        <Card sx={{ mb: 4, maxWidth: '900px', mx: 'auto' }}>
          <CardContent sx={{ p: 4 }}>
            <Typography variant="h5" gutterBottom fontWeight="bold" sx={{ mb: 3 }}>
              Describe Your Situation
            </Typography>

            <TextField
              label="What happened?"
              placeholder="Example: My flight was delayed 8 hours due to weather and I had to book a hotel overnight..."
              multiline
              rows={6}
              fullWidth
              value={situation}
              onChange={(e) => setSituation(e.target.value)}
              sx={{ mb: 3 }}
              helperText="Be as detailed as possible. Include dates, costs, and relevant details."
            />

            <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 2 }}>
              Or try an example:
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 4 }}>
              {exampleSituations.map((example, index) => (
                <Chip
                  key={index}
                  label={example}
                  onClick={() => setSituation(example)}
                  variant="outlined"
                  sx={{ cursor: 'pointer' }}
                />
              ))}
            </Box>

            <Divider sx={{ my: 3 }} />

            <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
              Additional Details (Optional)
            </Typography>

            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Category</InputLabel>
                  <Select
                    value={category}
                    label="Category"
                    onChange={(e) => setCategory(e.target.value)}
                  >
                    <MenuItem value="">
                      <em>None</em>
                    </MenuItem>
                    {categories.map((cat) => (
                      <MenuItem key={cat} value={cat}>{cat}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  label="Date of Incident"
                  type="date"
                  fullWidth
                  value={incidentDate}
                  onChange={(e) => setIncidentDate(e.target.value)}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  label="Location"
                  fullWidth
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="City, State or Country"
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  label="Estimated Cost/Loss"
                  fullWidth
                  value={estimatedCost}
                  onChange={(e) => setEstimatedCost(e.target.value)}
                  placeholder="$500"
                />
              </Grid>
            </Grid>

            {error && (
              <Alert severity="error" sx={{ mt: 3 }}>
                {error}
              </Alert>
            )}

            <Box sx={{ textAlign: 'center', mt: 4 }}>
              <Button
                variant="contained"
                color="primary"
                size="large"
                onClick={handleAnalyze}
                disabled={loading || !situation.trim()}
                startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <AssignmentTurnedInIcon />}
                sx={{ px: 6, py: 1.5 }}
              >
                {loading ? 'Analyzing...' : 'Analyze My Situation'}
              </Button>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Analysis Results */}
      {analysis && (
        <Box sx={{ maxWidth: '1200px', mx: 'auto' }}>
          {/* Summary Card */}
          <Card sx={{ mb: 4, border: analysis.can_file_claims ? '2px solid' : '1px solid', borderColor: analysis.can_file_claims ? 'success.main' : 'grey.300' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                {analysis.can_file_claims ? (
                  <CheckCircleIcon sx={{ fontSize: 48, color: 'success.main', mr: 2 }} />
                ) : (
                  <InfoIcon sx={{ fontSize: 48, color: 'warning.main', mr: 2 }} />
                )}
                <Box>
                  <Typography variant="h4" fontWeight="bold">
                    {analysis.can_file_claims ? 'Claims Available!' : 'No Claims Found'}
                  </Typography>
                  <Typography variant="h6" color="text.secondary">
                    {analysis.total_potential_value && `Potential Value: ${analysis.total_potential_value}`}
                  </Typography>
                </Box>
              </Box>

              <Typography variant="body1" sx={{ mb: 2 }}>
                <strong>Your Situation:</strong> {analysis.situation}
              </Typography>

              {analysis.recommendations && analysis.recommendations.length > 0 && (
                <Typography variant="body1" color="success.main" fontWeight="medium">
                  We found {analysis.recommendations.length} potential claim(s) you can file!
                </Typography>
              )}
            </CardContent>
          </Card>

          {/* Recommendations */}
          {analysis.recommendations && analysis.recommendations.map((rec, index) => (
            <Accordion key={index} defaultExpanded={index === 0} sx={{ mb: 2 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', pr: 2 }}>
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="h6" fontWeight="bold">
                      {rec.policy_name || rec.claim_type}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {rec.policy_type?.toUpperCase()} • {rec.claim_type}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Chip
                      label={`Priority: ${rec.priority || 'Medium'}`}
                      color={getPriorityColor(rec.priority)}
                      size="small"
                    />
                    <Chip
                      label={`Likelihood: ${rec.likelihood || 'Medium'}`}
                      color={getLikelihoodColor(rec.likelihood)}
                      size="small"
                    />
                  </Box>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={3}>
                  {/* Amount */}
                  <Grid item xs={12}>
                    <Paper sx={{ p: 2, bgcolor: 'success.lighter' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <AttachMoneyIcon sx={{ color: 'success.main', mr: 1 }} />
                        <Typography variant="h6" fontWeight="bold">
                          {rec.estimated_amount || 'Amount varies'}
                        </Typography>
                      </Box>
                    </Paper>
                  </Grid>

                  {/* Reason */}
                  <Grid item xs={12}>
                    <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                      Why This Applies:
                    </Typography>
                    <Typography variant="body1">
                      {rec.reason}
                    </Typography>
                  </Grid>

                  {/* Required Documents */}
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                      Required Documents:
                    </Typography>
                    <List dense>
                      {rec.required_docs && rec.required_docs.map((doc, i) => (
                        <ListItem key={i}>
                          <ListItemIcon sx={{ minWidth: 32 }}>
                            <DescriptionIcon sx={{ fontSize: 20, color: 'primary.main' }} />
                          </ListItemIcon>
                          <ListItemText primary={doc} />
                        </ListItem>
                      ))}
                    </List>
                  </Grid>

                  {/* Filing Steps */}
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                      How to File:
                    </Typography>
                    <List dense>
                      {rec.filing_steps && rec.filing_steps.map((step, i) => (
                        <ListItem key={i}>
                          <ListItemIcon sx={{ minWidth: 32 }}>
                            <Box sx={{
                              bgcolor: 'primary.main',
                              color: 'white',
                              width: 24,
                              height: 24,
                              borderRadius: '50%',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              fontSize: '0.875rem',
                              fontWeight: 'bold'
                            }}>
                              {i + 1}
                            </Box>
                          </ListItemIcon>
                          <ListItemText primary={step} />
                        </ListItem>
                      ))}
                    </List>
                  </Grid>

                  {/* Deadline & Notes */}
                  {rec.deadline && (
                    <Grid item xs={12}>
                      <Alert severity="warning">
                        <AlertTitle>Deadline</AlertTitle>
                        {rec.deadline}
                      </Alert>
                    </Grid>
                  )}

                  {rec.notes && (
                    <Grid item xs={12}>
                      <Alert severity="info">
                        {rec.notes}
                      </Alert>
                    </Grid>
                  )}
                </Grid>
              </AccordionDetails>
            </Accordion>
          ))}

          {/* Warnings */}
          {analysis.warnings && analysis.warnings.length > 0 && (
            <Card sx={{ mb: 4, bgcolor: 'warning.lighter' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <WarningIcon sx={{ color: 'warning.main', mr: 1 }} />
                  <Typography variant="h6" fontWeight="bold">
                    Important Warnings
                  </Typography>
                </Box>
                <List>
                  {analysis.warnings.map((warning, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <WarningIcon sx={{ color: 'warning.main' }} />
                      </ListItemIcon>
                      <ListItemText primary={warning} />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          )}

          {/* Next Steps */}
          {analysis.next_steps && analysis.next_steps.length > 0 && (
            <Card sx={{ mb: 4 }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <TrendingUpIcon sx={{ color: 'primary.main', mr: 1 }} />
                  <Typography variant="h6" fontWeight="bold">
                    Your Next Steps
                  </Typography>
                </Box>
                <List>
                  {analysis.next_steps.map((step, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <Box sx={{
                          bgcolor: 'primary.main',
                          color: 'white',
                          width: 32,
                          height: 32,
                          borderRadius: '50%',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontWeight: 'bold'
                        }}>
                          {index + 1}
                        </Box>
                      </ListItemIcon>
                      <ListItemText
                        primary={step}
                        primaryTypographyProps={{ fontWeight: 'medium' }}
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          )}

          {/* Actions */}
          <Box sx={{ textAlign: 'center', mt: 4 }}>
            <Button
              variant="outlined"
              onClick={() => {
                setAnalysis(null);
                setSituation('');
                setIncidentDate('');
                setLocation('');
                setEstimatedCost('');
                setCategory('');
              }}
              sx={{ mr: 2 }}
            >
              Analyze Another Situation
            </Button>
            <Button
              variant="contained"
              onClick={() => navigate('/policies')}
            >
              View My Policies
            </Button>
          </Box>
        </Box>
      )}
    </Container>
  );
};

export default ClaimsPage;
