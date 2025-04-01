import React from 'react';
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider
} from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import FamilyRestroomIcon from '@mui/icons-material/FamilyRestroom';
import MedicalServicesIcon from '@mui/icons-material/MedicalServices';
import WorkIcon from '@mui/icons-material/Work';
import HomeIcon from '@mui/icons-material/Home';
import DirectionsCarIcon from '@mui/icons-material/DirectionsCar';
import SchoolIcon from '@mui/icons-material/School';
import HealthAndSafetyIcon from '@mui/icons-material/HealthAndSafety';

/**
 * Component that displays personalized question suggestions based on user context
 */
const PersonalizedSuggestions = ({ insuranceType }) => {
  // Create personalized suggestions based on insurance type
  const getSuggestions = () => {
    switch (insuranceType) {
      case 'health':
        return [
          {
            context: 'Family Coverage',
            icon: <FamilyRestroomIcon />,
            questions: [
              "Is my spouse covered under this plan?",
              "How do I add my newborn to my health insurance?",
              "What pediatric services are covered for my children?"
            ]
          },
          {
            context: 'Medical Conditions',
            icon: <MedicalServicesIcon />,
            questions: [
              "I have diabetes, are my supplies covered?",
              "Does this plan cover therapy for depression?",
              "How does this policy handle pre-existing conditions?"
            ]
          },
          {
            context: 'Life Stage',
            icon: <PersonIcon />,
            questions: [
              "I'm planning to have a baby next year, what's covered?",
              "I'm turning 65 soon, how does this work with Medicare?",
              "I'm a college student, what preventive care is included?"
            ]
          }
        ];
      case 'life':
        return [
          {
            context: 'Family Protection',
            icon: <FamilyRestroomIcon />,
            questions: [
              "I have two young children, is this coverage enough?",
              "How do I ensure my spouse gets the benefit if something happens to me?",
              "Can I set up a trust for my children as beneficiaries?"
            ]
          },
          {
            context: 'Financial Planning',
            icon: <WorkIcon />,
            questions: [
              "I'm 45 with a mortgage, is term or whole life better for me?",
              "How does the cash value in this policy grow over time?",
              "Can I borrow against this policy for my child's education?"
            ]
          },
          {
            context: 'Health Considerations',
            icon: <HealthAndSafetyIcon />,
            questions: [
              "I'm a smoker, how does that affect my premium?",
              "If I have a family history of heart disease, should I get more coverage?",
              "What happens if I'm diagnosed with a terminal illness?"
            ]
          }
        ];
      case 'disability':
        return [
          {
            context: 'Occupation',
            icon: <WorkIcon />,
            questions: [
              "I'm a surgeon, is 'own occupation' coverage right for me?",
              "I work remotely as a programmer, how would disability be determined?",
              "Does this policy protect my income if I can only work part-time?"
            ]
          },
          {
            context: 'Financial Protection',
            icon: <HomeIcon />,
            questions: [
              "Is 60% income replacement enough to cover my mortgage?",
              "How long should my elimination period be if I have 6 months of savings?",
              "Should I get short-term or long-term disability if I'm the sole provider?"
            ]
          },
          {
            context: 'Health Considerations',
            icon: <MedicalServicesIcon />,
            questions: [
              "I have back problems, will this be excluded from coverage?",
              "Does this policy cover mental health disabilities?",
              "If I'm recovering from surgery, when would benefits begin?"
            ]
          }
        ];
      default:
        return [];
    }
  };

  const suggestions = getSuggestions();

  if (!suggestions.length) {
    return null;
  }

  return (
    <Card sx={{ mb: 4, borderRadius: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Personalized Questions
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Here are some questions relevant to your situation that you might want to ask about your insurance policy:
        </Typography>

        <Divider sx={{ mb: 2 }} />

        {suggestions.map((category, index) => (
          <Box key={index} sx={{ mb: index < suggestions.length - 1 ? 3 : 0 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Box sx={{ 
                mr: 1, 
                display: 'flex', 
                alignItems: 'center', 
                color: 'primary.main'
              }}>
                {category.icon}
              </Box>
              <Typography variant="subtitle1" fontWeight="medium">
                {category.context}
              </Typography>
            </Box>
            
            <List dense disablePadding>
              {category.questions.map((question, qIndex) => (
                <ListItem key={qIndex} sx={{ py: 0.5 }}>
                  <Chip 
                    label={question}
                    clickable
                    color="primary"
                    variant="outlined"
                    size="medium"
                    sx={{ 
                      maxWidth: '100%',
                      height: 'auto',
                      '& .MuiChip-label': { 
                        whiteSpace: 'normal',
                        py: 0.5
                      }
                    }}
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        ))}
      </CardContent>
    </Card>
  );
};

export default PersonalizedSuggestions;
