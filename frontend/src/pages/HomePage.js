import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Container,
  Collapse,
  IconButton,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import DescriptionIcon from '@mui/icons-material/Description';
import QuestionAnswerIcon from '@mui/icons-material/QuestionAnswer';
import TranslateIcon from '@mui/icons-material/Translate';
import LocalHospitalIcon from '@mui/icons-material/LocalHospital';
import DirectionsCarIcon from '@mui/icons-material/DirectionsCar';
import FavoriteIcon from '@mui/icons-material/Favorite';
import AccessibleIcon from '@mui/icons-material/Accessible';
import FlightIcon from '@mui/icons-material/Flight';
import HomeIcon from '@mui/icons-material/Home';
import PetsIcon from '@mui/icons-material/Pets';
import BusinessIcon from '@mui/icons-material/Business';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import FindInPageIcon from '@mui/icons-material/FindInPage';
import RecommendIcon from '@mui/icons-material/Recommend';

// Insurance types data with rights and benefits
const insuranceTypes = [
  {
    id: 'health',
    name: 'Health Insurance',
    icon: LocalHospitalIcon,
    color: '#e74c3c',
    description: 'Medical, dental, and vision coverage for you and your family',
    keyRights: [
      'Right to appeal denied claims',
      'Preventive care at 100% coverage',
      'Emergency care cannot be denied',
      'No lifetime coverage limits',
      'Coverage for pre-existing conditions'
    ],
    commonBenefits: [
      'Doctor visits and specialist consultations',
      'Prescription drug coverage',
      'Hospital stays and surgeries',
      'Mental health and substance abuse treatment',
      'Maternity and newborn care',
      'Lab tests and diagnostic imaging'
    ]
  },
  {
    id: 'auto',
    name: 'Auto Insurance',
    icon: DirectionsCarIcon,
    color: '#3498db',
    description: 'Vehicle damage, liability, and accident coverage',
    keyRights: [
      'Choose your own repair shop (in most states)',
      'Rental car during repairs if you have coverage',
      'Cancel policy anytime with proper notice',
      'Receive clear explanation of claim denials',
      'Get diminished value compensation after repairs'
    ],
    commonBenefits: [
      'Collision and comprehensive coverage',
      'Liability for injury and property damage',
      'Uninsured/underinsured motorist protection',
      'Roadside assistance and towing',
      'Glass and windshield repair',
      'Rental car reimbursement'
    ]
  },
  {
    id: 'life',
    name: 'Life Insurance',
    icon: FavoriteIcon,
    color: '#9b59b6',
    description: 'Financial protection for your loved ones',
    keyRights: [
      'Free look period (usually 10-30 days)',
      'Change beneficiaries at any time',
      'Guaranteed insurability options',
      'Grace period for late payments (typically 30 days)',
      'Contest period protection after 2 years'
    ],
    commonBenefits: [
      'Death benefit for beneficiaries',
      'Cash value accumulation (whole/universal life)',
      'Tax-free death benefit payout',
      'Living benefits for terminal illness',
      'Policy loans against cash value',
      'Accelerated death benefits'
    ]
  },
  {
    id: 'disability',
    name: 'Disability Insurance',
    icon: AccessibleIcon,
    color: '#f39c12',
    description: 'Income protection if you cannot work due to injury or illness',
    keyRights: [
      'Definition of disability (own-occupation vs any)',
      'Benefit period duration',
      'Guaranteed renewable coverage',
      'Partial disability benefits',
      'Residual benefits for reduced earnings'
    ],
    commonBenefits: [
      'Monthly income replacement (typically 60-70%)',
      'Short-term and long-term coverage options',
      'Rehabilitation and return-to-work support',
      'Cost of living adjustments (COLA)',
      'Waiver of premium during disability',
      'Social Security integration options'
    ]
  },
  {
    id: 'travel',
    name: 'Travel Insurance',
    icon: FlightIcon,
    color: '#1abc9c',
    description: 'Protection for trips, flights, and travel emergencies',
    keyRights: [
      'Flight delay compensation (EU: €250-€600)',
      'Trip cancellation for covered reasons',
      'Emergency medical evacuation',
      'Lost baggage reimbursement',
      '24/7 travel assistance hotline'
    ],
    commonBenefits: [
      'Trip cancellation and interruption',
      'Emergency medical and dental coverage abroad',
      'Baggage loss, delay, and damage',
      'Flight delays and missed connections',
      'Travel accident insurance',
      'Rental car coverage overseas'
    ]
  },
  {
    id: 'home',
    name: 'Home/Renters Insurance',
    icon: HomeIcon,
    color: '#e67e22',
    description: 'Property and liability protection for your home',
    keyRights: [
      'Additional living expenses if home is uninhabitable',
      'Right to independent adjuster for disputes',
      'Replacement cost vs actual cash value',
      'Personal property coverage off-premises',
      'Liability protection for injuries on property'
    ],
    commonBenefits: [
      'Dwelling and structure coverage',
      'Personal property protection',
      'Liability coverage for injuries/damages',
      'Medical payments for guests',
      'Loss of use/additional living expenses',
      'Natural disaster coverage (varies by type)'
    ]
  },
  {
    id: 'pet',
    name: 'Pet Insurance',
    icon: PetsIcon,
    color: '#16a085',
    description: 'Veterinary care and medical coverage for your pets',
    keyRights: [
      'Coverage for accidents and illnesses',
      'Choice of any licensed veterinarian',
      'Direct vet payment options',
      'Hereditary and congenital condition coverage',
      'No network restrictions (most plans)'
    ],
    commonBenefits: [
      'Accident and illness coverage',
      'Surgery and hospitalization',
      'Diagnostic tests and imaging',
      'Prescription medications',
      'Chronic condition management',
      'Wellness and preventive care add-ons'
    ]
  },
  {
    id: 'business',
    name: 'Business Insurance',
    icon: BusinessIcon,
    color: '#34495e',
    description: 'Protection for your business assets and operations',
    keyRights: [
      'General liability protection',
      'Professional liability/E&O coverage',
      'Business interruption compensation',
      'Workers compensation benefits',
      'Cyber liability protection'
    ],
    commonBenefits: [
      'Property and equipment coverage',
      'General and professional liability',
      'Business interruption income',
      'Workers compensation for employees',
      'Commercial auto coverage',
      'Cyber and data breach insurance'
    ]
  }
];

const HomePage = () => {
  const navigate = useNavigate();
  const [expandedCard, setExpandedCard] = useState(null);

  const handleExpandClick = (typeId) => {
    setExpandedCard(expandedCard === typeId ? null : typeId);
  };

  return (
    <Container maxWidth="lg">
      {/* Hero Section */}
      <Box
        sx={{
          textAlign: 'center',
          py: 8,
          px: 2,
          mb: 8
        }}
      >
        <Typography variant="h2" component="h1" gutterBottom fontWeight="bold" sx={{ mb: 2 }}>
          Know Your Insurance Rights
        </Typography>
        <Typography variant="h5" color="text.secondary" sx={{ mb: 2, maxWidth: '800px', mx: 'auto' }}>
          Upload any insurance policy and get AI-powered insights on what you can claim, your rights, and how to maximize your benefits
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4, fontStyle: 'italic' }}>
          Free for your first 2 policies • Works with any insurance type
        </Typography>
        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, flexWrap: 'wrap' }}>
          <Button
            variant="contained"
            color="primary"
            size="large"
            onClick={() => navigate('/document')}
            startIcon={<DescriptionIcon />}
            sx={{ px: 4, py: 1.5 }}
          >
            Upload Your Policy
          </Button>
          <Button
            variant="outlined"
            color="primary"
            size="large"
            onClick={() => {
              const section = document.getElementById('how-it-works');
              section?.scrollIntoView({ behavior: 'smooth' });
            }}
            sx={{ px: 4, py: 1.5 }}
          >
            Learn How It Works
          </Button>
        </Box>
      </Box>

      {/* How it Works Section */}
      <Box id="how-it-works" sx={{ mb: 10 }}>
        <Typography variant="h4" component="h2" gutterBottom sx={{ mb: 4, textAlign: 'center' }}>
          How It Works
        </Typography>
        <Grid container spacing={4} sx={{ mb: 4 }}>
          <Grid item xs={12} md={3}>
            <Card sx={{ height: '100%', textAlign: 'center', position: 'relative' }}>
              <CardContent sx={{ py: 4 }}>
                <Box sx={{
                  position: 'absolute',
                  top: -20,
                  left: '50%',
                  transform: 'translateX(-50%)',
                  bgcolor: 'primary.main',
                  color: 'white',
                  width: 40,
                  height: 40,
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 'bold',
                  fontSize: '1.2rem'
                }}>
                  1
                </Box>
                <DescriptionIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2, mt: 2 }} />
                <Typography variant="h6" component="h3" gutterBottom fontWeight="bold">
                  Upload Your Policy
                </Typography>
                <Typography color="text.secondary" variant="body2">
                  Upload any insurance document in PDF format. Works with health, auto, life, travel, home, and more.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card sx={{ height: '100%', textAlign: 'center', position: 'relative' }}>
              <CardContent sx={{ py: 4 }}>
                <Box sx={{
                  position: 'absolute',
                  top: -20,
                  left: '50%',
                  transform: 'translateX(-50%)',
                  bgcolor: 'primary.main',
                  color: 'white',
                  width: 40,
                  height: 40,
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 'bold',
                  fontSize: '1.2rem'
                }}>
                  2
                </Box>
                <FindInPageIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2, mt: 2 }} />
                <Typography variant="h6" component="h3" gutterBottom fontWeight="bold">
                  AI Analyzes Everything
                </Typography>
                <Typography color="text.secondary" variant="body2">
                  Our AI parses your policy and organizes coverage, benefits, exclusions, and claim processes.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card sx={{ height: '100%', textAlign: 'center', position: 'relative' }}>
              <CardContent sx={{ py: 4 }}>
                <Box sx={{
                  position: 'absolute',
                  top: -20,
                  left: '50%',
                  transform: 'translateX(-50%)',
                  bgcolor: 'primary.main',
                  color: 'white',
                  width: 40,
                  height: 40,
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 'bold',
                  fontSize: '1.2rem'
                }}>
                  3
                </Box>
                <CheckCircleIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2, mt: 2 }} />
                <Typography variant="h6" component="h3" gutterBottom fontWeight="bold">
                  Understand Your Rights
                </Typography>
                <Typography color="text.secondary" variant="body2">
                  Get a clear summary of what you CAN claim, what you CANNOT claim, and how to file.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card sx={{ height: '100%', textAlign: 'center', position: 'relative' }}>
              <CardContent sx={{ py: 4 }}>
                <Box sx={{
                  position: 'absolute',
                  top: -20,
                  left: '50%',
                  transform: 'translateX(-50%)',
                  bgcolor: 'secondary.main',
                  color: 'white',
                  width: 40,
                  height: 40,
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 'bold',
                  fontSize: '1.2rem'
                }}>
                  4
                </Box>
                <RecommendIcon sx={{ fontSize: 60, color: 'secondary.main', mb: 2, mt: 2 }} />
                <Typography variant="h6" component="h3" gutterBottom fontWeight="bold">
                  Get Claim Recommendations
                </Typography>
                <Typography color="text.secondary" variant="body2">
                  Describe what happened and get personalized recommendations for claims you can file.
                </Typography>
                <Chip label="Coming Soon" size="small" color="secondary" sx={{ mt: 1 }} />
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>

      {/* Insurance Types Section */}
      <Box sx={{ mb: 10 }}>
        <Typography variant="h4" component="h2" gutterBottom sx={{ mb: 2, textAlign: 'center' }}>
          Know Your Rights for Any Insurance Type
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 6, textAlign: 'center', maxWidth: '700px', mx: 'auto' }}>
          Browse common insurance types to learn about your rights and benefits. Click any card to see details.
        </Typography>
        <Grid container spacing={3}>
          {insuranceTypes.map((type) => {
            const Icon = type.icon;
            const isExpanded = expandedCard === type.id;

            return (
              <Grid item xs={12} sm={6} md={4} key={type.id}>
                <Card
                  sx={{
                    height: '100%',
                    cursor: 'pointer',
                    transition: 'all 0.3s',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: 4
                    },
                    border: isExpanded ? `2px solid ${type.color}` : '1px solid #e0e0e0'
                  }}
                  onClick={() => handleExpandClick(type.id)}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Icon sx={{ fontSize: 40, color: type.color, mr: 2 }} />
                      <Typography variant="h6" component="h3" fontWeight="bold">
                        {type.name}
                      </Typography>
                      <IconButton
                        size="small"
                        sx={{ ml: 'auto' }}
                      >
                        {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                      </IconButton>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {type.description}
                    </Typography>

                    <Collapse in={isExpanded} timeout="auto" unmountOnExit>
                      <Divider sx={{ my: 2 }} />
                      <Typography variant="subtitle2" fontWeight="bold" gutterBottom sx={{ color: type.color }}>
                        Key Rights You Have:
                      </Typography>
                      <List dense>
                        {type.keyRights.slice(0, 3).map((right, index) => (
                          <ListItem key={index} sx={{ py: 0.5, pl: 0 }}>
                            <ListItemIcon sx={{ minWidth: 30 }}>
                              <CheckCircleIcon sx={{ fontSize: 16, color: type.color }} />
                            </ListItemIcon>
                            <ListItemText
                              primary={right}
                              primaryTypographyProps={{ variant: 'body2' }}
                            />
                          </ListItem>
                        ))}
                      </List>

                      <Typography variant="subtitle2" fontWeight="bold" gutterBottom sx={{ color: type.color, mt: 2 }}>
                        Common Benefits:
                      </Typography>
                      <List dense>
                        {type.commonBenefits.slice(0, 3).map((benefit, index) => (
                          <ListItem key={index} sx={{ py: 0.5, pl: 0 }}>
                            <ListItemIcon sx={{ minWidth: 30 }}>
                              <CheckCircleIcon sx={{ fontSize: 16, color: type.color }} />
                            </ListItemIcon>
                            <ListItemText
                              primary={benefit}
                              primaryTypographyProps={{ variant: 'body2' }}
                            />
                          </ListItem>
                        ))}
                      </List>

                      <Button
                        variant="outlined"
                        size="small"
                        fullWidth
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate('/document');
                        }}
                        sx={{ mt: 2, borderColor: type.color, color: type.color }}
                      >
                        Upload {type.name.split(' ')[0]} Policy
                      </Button>
                    </Collapse>
                  </CardContent>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      </Box>

      {/* Value Proposition Section */}
      <Box sx={{ mb: 10, bgcolor: 'primary.main', color: 'white', py: 6, px: 4, borderRadius: 2 }}>
        <Grid container spacing={4} alignItems="center">
          <Grid item xs={12} md={8}>
            <Typography variant="h4" component="h2" gutterBottom fontWeight="bold">
              Stop Leaving Money on the Table
            </Typography>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Most people don't know what benefits they're entitled to. InsurSpeak helps you:
            </Typography>
            <List>
              <ListItem>
                <ListItemIcon>
                  <AttachMoneyIcon sx={{ color: 'white' }} />
                </ListItemIcon>
                <ListItemText
                  primary="Discover hidden benefits you didn't know existed"
                  primaryTypographyProps={{ fontWeight: 'medium' }}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <CheckCircleIcon sx={{ color: 'white' }} />
                </ListItemIcon>
                <ListItemText
                  primary="Know exactly what you can and cannot claim"
                  primaryTypographyProps={{ fontWeight: 'medium' }}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <FindInPageIcon sx={{ color: 'white' }} />
                </ListItemIcon>
                <ListItemText
                  primary="Understand complex policies in plain English"
                  primaryTypographyProps={{ fontWeight: 'medium' }}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <RecommendIcon sx={{ color: 'white' }} />
                </ListItemIcon>
                <ListItemText
                  primary="Get personalized claim recommendations based on your situation"
                  primaryTypographyProps={{ fontWeight: 'medium' }}
                />
              </ListItem>
            </List>
          </Grid>
          <Grid item xs={12} md={4} sx={{ textAlign: 'center' }}>
            <Typography variant="h3" fontWeight="bold" gutterBottom>
              Free
            </Typography>
            <Typography variant="h6" gutterBottom>
              for your first 2 policies
            </Typography>
            <Button
              variant="contained"
              size="large"
              onClick={() => navigate('/document')}
              sx={{
                mt: 2,
                bgcolor: 'white',
                color: 'primary.main',
                '&:hover': { bgcolor: 'grey.100' }
              }}
            >
              Get Started Now
            </Button>
          </Grid>
        </Grid>
      </Box>

      {/* Final CTA */}
      <Box sx={{ textAlign: 'center', py: 8 }}>
        <Typography variant="h4" component="h2" gutterBottom fontWeight="bold">
          Ready to Understand Your Insurance?
        </Typography>
        <Typography variant="h6" color="text.secondary" sx={{ mb: 4, maxWidth: '600px', mx: 'auto' }}>
          Upload your policy now and discover what benefits you're entitled to
        </Typography>
        <Button
          variant="contained"
          color="primary"
          size="large"
          onClick={() => navigate('/document')}
          startIcon={<DescriptionIcon />}
          sx={{ px: 6, py: 2 }}
        >
          Upload Your Policy
        </Button>
      </Box>
    </Container>
  );
};

export default HomePage;
