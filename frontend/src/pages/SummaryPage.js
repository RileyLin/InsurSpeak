import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Container,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Paper,
  Alert,
  AlertTitle,
  IconButton,
  Collapse
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import WarningIcon from '@mui/icons-material/Warning';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import DescriptionIcon from '@mui/icons-material/Description';
import GavelIcon from '@mui/icons-material/Gavel';
import LightbulbIcon from '@mui/icons-material/Lightbulb';
import DownloadIcon from '@mui/icons-material/Download';
import ShareIcon from '@mui/icons-material/Share';
import PrintIcon from '@mui/icons-material/Print';
import QuestionAnswerIcon from '@mui/icons-material/QuestionAnswer';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import InfoIcon from '@mui/icons-material/Info';

const SummaryPage = () => {
  const navigate = useNavigate();
  const { summary, insuranceType, isLoading } = useSelector(state => state.document);
  const [expandedSections, setExpandedSections] = useState({
    coverage: true,
    benefits: true,
    exclusions: true,
    claims: true,
    costs: true,
    rights: true,
    insights: true
  });

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const handlePrint = () => {
    window.print();
  };

  const handleDownload = () => {
    // TODO: Implement PDF download
    alert('PDF download feature coming soon!');
  };

  const handleShare = () => {
    // TODO: Implement sharing
    alert('Sharing feature coming soon! Sign up to save and share your policies.');
  };

  if (!summary) {
    return (
      <Container>
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <InfoIcon sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h4" gutterBottom>
            No Policy Summary Available
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            Please upload a policy document first to see the summary.
          </Typography>
          <Button
            variant="contained"
            color="primary"
            onClick={() => navigate('/document')}
          >
            Upload Policy
          </Button>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header Section */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box>
            <Typography variant="h3" component="h1" gutterBottom fontWeight="bold">
              Your Policy Summary
            </Typography>
            <Chip
              label={insuranceType ? `${insuranceType.charAt(0).toUpperCase() + insuranceType.slice(1)} Insurance` : 'Insurance Policy'}
              color="primary"
              sx={{ mr: 1 }}
            />
            {summary.policyNumber && (
              <Chip label={`Policy #${summary.policyNumber}`} variant="outlined" />
            )}
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <IconButton onClick={handlePrint} title="Print">
              <PrintIcon />
            </IconButton>
            <IconButton onClick={handleDownload} title="Download PDF">
              <DownloadIcon />
            </IconButton>
            <IconButton onClick={handleShare} title="Share">
              <ShareIcon />
            </IconButton>
          </Box>
        </Box>

        <Alert severity="success" sx={{ mb: 2 }}>
          <AlertTitle>Policy Analysis Complete</AlertTitle>
          We've analyzed your policy and organized it into easy-to-understand sections below.
        </Alert>

        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Button
            variant="contained"
            color="primary"
            startIcon={<QuestionAnswerIcon />}
            onClick={() => navigate('/questions')}
          >
            Ask Questions About This Policy
          </Button>
          <Button
            variant="outlined"
            onClick={() => navigate('/document')}
          >
            Upload Another Policy
          </Button>
        </Box>
      </Box>

      {/* Coverage Overview Card */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <DescriptionIcon sx={{ fontSize: 32, color: 'primary.main', mr: 2 }} />
              <Typography variant="h5" component="h2" fontWeight="bold">
                Coverage Overview
              </Typography>
            </Box>
            <IconButton onClick={() => toggleSection('coverage')}>
              {expandedSections.coverage ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Box>

          <Collapse in={expandedSections.coverage}>
            <Grid container spacing={2}>
              {summary.policyHolder && (
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Policy Holder
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {summary.policyHolder}
                  </Typography>
                </Grid>
              )}
              {summary.policyNumber && (
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Policy Number
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {summary.policyNumber}
                  </Typography>
                </Grid>
              )}
              {summary.coveragePeriod && (
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Coverage Period
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {summary.coveragePeriod}
                  </Typography>
                </Grid>
              )}
              {summary.coverageLimit && (
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Coverage Limit
                  </Typography>
                  <Typography variant="body1" fontWeight="medium" color="success.main">
                    {summary.coverageLimit}
                  </Typography>
                </Grid>
              )}
            </Grid>
          </Collapse>
        </CardContent>
      </Card>

      {/* Benefits & Rights Section */}
      <Card sx={{ mb: 3, border: '2px solid', borderColor: 'success.light' }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <CheckCircleIcon sx={{ fontSize: 32, color: 'success.main', mr: 2 }} />
              <Box>
                <Typography variant="h5" component="h2" fontWeight="bold">
                  What You CAN Claim
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Benefits and coverage you're entitled to
                </Typography>
              </Box>
            </Box>
            <IconButton onClick={() => toggleSection('benefits')}>
              {expandedSections.benefits ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Box>

          <Collapse in={expandedSections.benefits}>
            <Divider sx={{ mb: 2 }} />
            {summary.benefits && summary.benefits.length > 0 ? (
              <List>
                {summary.benefits.map((benefit, index) => (
                  <ListItem key={index} sx={{ alignItems: 'flex-start', py: 1 }}>
                    <ListItemIcon sx={{ minWidth: 40, mt: 0.5 }}>
                      <CheckCircleIcon sx={{ color: 'success.main' }} />
                    </ListItemIcon>
                    <ListItemText
                      primary={benefit.name || benefit}
                      secondary={benefit.details}
                      primaryTypographyProps={{ fontWeight: 'medium' }}
                    />
                    {benefit.amount && (
                      <Chip
                        label={benefit.amount}
                        color="success"
                        size="small"
                        sx={{ ml: 2 }}
                      />
                    )}
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography color="text.secondary">
                Benefits information will be extracted from your policy document.
              </Typography>
            )}
          </Collapse>
        </CardContent>
      </Card>

      {/* Exclusions & Limitations Section */}
      <Card sx={{ mb: 3, border: '2px solid', borderColor: 'error.light' }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <CancelIcon sx={{ fontSize: 32, color: 'error.main', mr: 2 }} />
              <Box>
                <Typography variant="h5" component="h2" fontWeight="bold">
                  What You CANNOT Claim
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Exclusions and limitations to be aware of
                </Typography>
              </Box>
            </Box>
            <IconButton onClick={() => toggleSection('exclusions')}>
              {expandedSections.exclusions ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Box>

          <Collapse in={expandedSections.exclusions}>
            <Divider sx={{ mb: 2 }} />
            <Alert severity="warning" sx={{ mb: 2 }}>
              <AlertTitle>Important</AlertTitle>
              Pay close attention to these exclusions to avoid denied claims
            </Alert>
            {summary.exclusions && summary.exclusions.length > 0 ? (
              <List>
                {summary.exclusions.map((exclusion, index) => (
                  <ListItem key={index} sx={{ alignItems: 'flex-start', py: 1 }}>
                    <ListItemIcon sx={{ minWidth: 40, mt: 0.5 }}>
                      <CancelIcon sx={{ color: 'error.main' }} />
                    </ListItemIcon>
                    <ListItemText
                      primary={exclusion.name || exclusion}
                      secondary={exclusion.details}
                      primaryTypographyProps={{ fontWeight: 'medium' }}
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography color="text.secondary">
                Exclusions information will be extracted from your policy document.
              </Typography>
            )}
          </Collapse>
        </CardContent>
      </Card>

      {/* Claims Process Section */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <GavelIcon sx={{ fontSize: 32, color: 'primary.main', mr: 2 }} />
              <Box>
                <Typography variant="h5" component="h2" fontWeight="bold">
                  How to File a Claim
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Step-by-step claims process
                </Typography>
              </Box>
            </Box>
            <IconButton onClick={() => toggleSection('claims')}>
              {expandedSections.claims ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Box>

          <Collapse in={expandedSections.claims}>
            <Divider sx={{ mb: 2 }} />
            {summary.claimsProcess && (
              <Box>
                {summary.claimsProcess.steps && summary.claimsProcess.steps.length > 0 ? (
                  <List>
                    {summary.claimsProcess.steps.map((step, index) => (
                      <ListItem key={index} sx={{ alignItems: 'flex-start' }}>
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
                          primary={step.title || step}
                          secondary={step.description}
                          primaryTypographyProps={{ fontWeight: 'medium' }}
                        />
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Typography color="text.secondary" sx={{ mb: 2 }}>
                    Claims process information will be extracted from your policy.
                  </Typography>
                )}

                {summary.claimsProcess.contact && (
                  <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                    <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                      Claims Contact Information
                    </Typography>
                    <Typography variant="body2">{summary.claimsProcess.contact}</Typography>
                  </Paper>
                )}

                {summary.claimsProcess.deadline && (
                  <Alert severity="info" sx={{ mt: 2 }}>
                    <AlertTitle>Filing Deadline</AlertTitle>
                    {summary.claimsProcess.deadline}
                  </Alert>
                )}
              </Box>
            )}
          </Collapse>
        </CardContent>
      </Card>

      {/* Deductibles & Costs Section */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <AttachMoneyIcon sx={{ fontSize: 32, color: 'primary.main', mr: 2 }} />
              <Box>
                <Typography variant="h5" component="h2" fontWeight="bold">
                  Your Costs
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Deductibles, co-pays, and out-of-pocket expenses
                </Typography>
              </Box>
            </Box>
            <IconButton onClick={() => toggleSection('costs')}>
              {expandedSections.costs ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Box>

          <Collapse in={expandedSections.costs}>
            <Divider sx={{ mb: 2 }} />
            {summary.costs ? (
              <Grid container spacing={2}>
                {summary.costs.deductible && (
                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'grey.50' }}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Deductible
                      </Typography>
                      <Typography variant="h5" fontWeight="bold" color="primary.main">
                        {summary.costs.deductible}
                      </Typography>
                    </Paper>
                  </Grid>
                )}
                {summary.costs.copay && (
                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'grey.50' }}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Co-pay
                      </Typography>
                      <Typography variant="h5" fontWeight="bold" color="primary.main">
                        {summary.costs.copay}
                      </Typography>
                    </Paper>
                  </Grid>
                )}
                {summary.costs.coinsurance && (
                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'grey.50' }}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Co-insurance
                      </Typography>
                      <Typography variant="h5" fontWeight="bold" color="primary.main">
                        {summary.costs.coinsurance}
                      </Typography>
                    </Paper>
                  </Grid>
                )}
                {summary.costs.outOfPocketMax && (
                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'grey.50' }}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Out-of-Pocket Max
                      </Typography>
                      <Typography variant="h5" fontWeight="bold" color="success.main">
                        {summary.costs.outOfPocketMax}
                      </Typography>
                    </Paper>
                  </Grid>
                )}
              </Grid>
            ) : (
              <Typography color="text.secondary">
                Cost information will be extracted from your policy.
              </Typography>
            )}
          </Collapse>
        </CardContent>
      </Card>

      {/* Special Rights & Protections */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <GavelIcon sx={{ fontSize: 32, color: 'primary.main', mr: 2 }} />
              <Box>
                <Typography variant="h5" component="h2" fontWeight="bold">
                  Your Rights & Protections
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Important rights you should know about
                </Typography>
              </Box>
            </Box>
            <IconButton onClick={() => toggleSection('rights')}>
              {expandedSections.rights ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Box>

          <Collapse in={expandedSections.rights}>
            <Divider sx={{ mb: 2 }} />
            {summary.rights && summary.rights.length > 0 ? (
              <List>
                {summary.rights.map((right, index) => (
                  <ListItem key={index} sx={{ alignItems: 'flex-start' }}>
                    <ListItemIcon sx={{ minWidth: 40, mt: 0.5 }}>
                      <CheckCircleIcon sx={{ color: 'primary.main' }} />
                    </ListItemIcon>
                    <ListItemText
                      primary={right.name || right}
                      secondary={right.description}
                      primaryTypographyProps={{ fontWeight: 'medium' }}
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography color="text.secondary">
                Rights and protections information will be extracted from your policy.
              </Typography>
            )}
          </Collapse>
        </CardContent>
      </Card>

      {/* AI-Powered Insights */}
      <Card sx={{ mb: 3, bgcolor: 'info.lighter', border: '2px solid', borderColor: 'info.main' }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <LightbulbIcon sx={{ fontSize: 32, color: 'info.main', mr: 2 }} />
              <Box>
                <Typography variant="h5" component="h2" fontWeight="bold">
                  AI Insights & Recommendations
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Hidden benefits and money-saving tips
                </Typography>
              </Box>
            </Box>
            <IconButton onClick={() => toggleSection('insights')}>
              {expandedSections.insights ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Box>

          <Collapse in={expandedSections.insights}>
            <Divider sx={{ mb: 2 }} />
            {summary.insights ? (
              <Box>
                {summary.insights.hiddenBenefits && summary.insights.hiddenBenefits.length > 0 && (
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="subtitle1" fontWeight="bold" gutterBottom color="success.main">
                      Hidden Benefits You Might Miss
                    </Typography>
                    <List>
                      {summary.insights.hiddenBenefits.map((benefit, index) => (
                        <ListItem key={index}>
                          <ListItemIcon>
                            <LightbulbIcon sx={{ color: 'success.main' }} />
                          </ListItemIcon>
                          <ListItemText primary={benefit} />
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                )}

                {summary.insights.watchOut && summary.insights.watchOut.length > 0 && (
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="subtitle1" fontWeight="bold" gutterBottom color="warning.main">
                      Watch Out For
                    </Typography>
                    <List>
                      {summary.insights.watchOut.map((item, index) => (
                        <ListItem key={index}>
                          <ListItemIcon>
                            <WarningIcon sx={{ color: 'warning.main' }} />
                          </ListItemIcon>
                          <ListItemText primary={item} />
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                )}

                {summary.insights.moneySavingTips && summary.insights.moneySavingTips.length > 0 && (
                  <Box>
                    <Typography variant="subtitle1" fontWeight="bold" gutterBottom color="info.main">
                      Money-Saving Tips
                    </Typography>
                    <List>
                      {summary.insights.moneySavingTips.map((tip, index) => (
                        <ListItem key={index}>
                          <ListItemIcon>
                            <AttachMoneyIcon sx={{ color: 'info.main' }} />
                          </ListItemIcon>
                          <ListItemText primary={tip} />
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                )}
              </Box>
            ) : (
              <Alert severity="info">
                AI insights will be generated based on your specific policy details.
              </Alert>
            )}
          </Collapse>
        </CardContent>
      </Card>

      {/* Bottom Actions */}
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <Typography variant="h6" gutterBottom>
          Have Questions About Your Policy?
        </Typography>
        <Button
          variant="contained"
          color="primary"
          size="large"
          startIcon={<QuestionAnswerIcon />}
          onClick={() => navigate('/questions')}
          sx={{ mr: 2 }}
        >
          Ask AI Questions
        </Button>
        <Button
          variant="outlined"
          size="large"
          onClick={() => navigate('/document')}
        >
          Upload Another Policy
        </Button>
      </Box>
    </Container>
  );
};

export default SummaryPage;
