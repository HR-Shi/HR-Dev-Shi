import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  TextField,
  InputAdornment,
  Card,
  CardContent,
  CardActionArea,
  Grid,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tabs,
  Tab,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Breadcrumbs,
  Link,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Paper,
} from '@mui/material';
import {
  Search,
  ExpandMore,
  PlayArrow,
  Book,
  Quiz,
  VideoLibrary,
  Help,
  Feedback,
  NavigateNext,
  CheckCircle,
  Launch,
  Download,
  Share,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

interface HelpArticle {
  id: string;
  title: string;
  description: string;
  category: string;
  tags: string[];
  content: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimatedTime: string;
  videoUrl?: string;
  lastUpdated: string;
}

interface Tutorial {
  id: string;
  title: string;
  description: string;
  steps: TutorialStep[];
  category: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
}

interface TutorialStep {
  title: string;
  description: string;
  action?: string;
  screenshot?: string;
  code?: string;
}

interface FAQ {
  id: string;
  question: string;
  answer: string;
  category: string;
  tags: string[];
}

const HelpCenter: React.FC = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTab, setSelectedTab] = useState(0);
  const [selectedArticle, setSelectedArticle] = useState<HelpArticle | null>(null);
  const [tutorialOpen, setTutorialOpen] = useState(false);
  const [selectedTutorial, setSelectedTutorial] = useState<Tutorial | null>(null);
  const [currentStep, setCurrentStep] = useState(0);

  // Mock data - in real implementation, this would come from API
  const helpArticles: HelpArticle[] = [
    {
      id: '1',
      title: 'Getting Started with HR Dashboard',
      description: 'Learn the basics of navigating and using the HR Dashboard',
      category: 'Getting Started',
      tags: ['basics', 'navigation', 'overview'],
      content: `# Getting Started with HR Dashboard

Welcome to the HR Dashboard! This comprehensive guide will help you get started with our powerful HR analytics platform.

## Overview
The HR Dashboard is designed to help HR professionals make data-driven decisions through:
- Real-time KPI tracking
- Employee engagement surveys
- Predictive analytics
- Action plan management

## Navigation
- **Overview**: Main dashboard with key metrics
- **Employees**: Manage employee profiles and data
- **Surveys**: Create and analyze employee surveys
- **KPIs**: Track and manage key performance indicators
- **Analytics**: Deep-dive into HR data insights
- **Action Plans**: Create and track improvement initiatives

## Quick Start
1. Review your dashboard overview
2. Set up your first KPIs
3. Create an employee engagement survey
4. Analyze results and create action plans`,
      difficulty: 'beginner',
      estimatedTime: '10 min',
      videoUrl: 'https://example.com/getting-started-video',
      lastUpdated: '2024-01-15',
    },
    {
      id: '2',
      title: 'Creating Effective Employee Surveys',
      description: 'Best practices for designing and deploying employee surveys',
      category: 'Surveys',
      tags: ['surveys', 'engagement', 'best-practices'],
      content: `# Creating Effective Employee Surveys

## Survey Types
- **Pulse Surveys**: Quick, frequent check-ins
- **Annual Surveys**: Comprehensive yearly assessments
- **Exit Surveys**: Understand why employees leave
- **Custom Surveys**: Tailored to specific needs

## Best Practices
1. Keep surveys short (5-10 questions for pulse)
2. Use a mix of question types
3. Ensure anonymity when needed
4. Time deployment appropriately
5. Follow up with action plans

## Question Examples
- "How satisfied are you with your current role?" (Scale 1-5)
- "How likely are you to recommend this company as a place to work?" (NPS)
- "What one thing would improve your work experience?" (Open text)`,
      difficulty: 'intermediate',
      estimatedTime: '15 min',
      lastUpdated: '2024-01-12',
    },
    {
      id: '3',
      title: 'Understanding KPI Analytics',
      description: 'How to interpret and act on KPI data',
      category: 'Analytics',
      tags: ['kpis', 'analytics', 'metrics'],
      content: `# Understanding KPI Analytics

## Key Metrics to Track
- **Employee Engagement Score**: Overall satisfaction and engagement
- **Turnover Rate**: Percentage of employees leaving
- **Time to Fill**: Speed of recruitment process
- **Training Effectiveness**: Impact of development programs

## Reading Charts
- Trend lines show direction over time
- Variance indicators highlight unusual patterns
- Benchmarks compare against industry standards

## Taking Action
When KPIs indicate issues:
1. Investigate root causes
2. Create targeted action plans
3. Monitor progress regularly
4. Adjust strategies as needed`,
      difficulty: 'advanced',
      estimatedTime: '20 min',
      lastUpdated: '2024-01-10',
    },
  ];

  const tutorials: Tutorial[] = [
    {
      id: 'tutorial-1',
      title: 'Creating Your First Survey',
      description: 'Step-by-step guide to creating and launching your first employee survey',
      category: 'Surveys',
      difficulty: 'beginner',
      steps: [
        {
          title: 'Navigate to Surveys',
          description: 'Go to the Surveys section from the main navigation menu',
          action: 'Click on "Surveys" in the left sidebar',
        },
        {
          title: 'Create New Survey',
          description: 'Start creating a new survey by clicking the Create button',
          action: 'Click the "Create Survey" button',
        },
        {
          title: 'Choose Survey Type',
          description: 'Select the type of survey you want to create',
          action: 'Select "Pulse Survey" for a quick engagement check',
        },
        {
          title: 'Add Questions',
          description: 'Add questions to your survey using our question bank',
          action: 'Select questions from the predefined question bank or create custom ones',
        },
        {
          title: 'Configure Settings',
          description: 'Set up survey timing, target audience, and privacy settings',
          action: 'Configure survey settings and click "Launch Survey"',
        },
      ],
    },
    {
      id: 'tutorial-2',
      title: 'Setting Up KPI Tracking',
      description: 'Learn how to configure and monitor key performance indicators',
      category: 'KPIs',
      difficulty: 'intermediate',
      steps: [
        {
          title: 'Access KPI Management',
          description: 'Navigate to the KPI management section',
          action: 'Click on "KPI Management" in the navigation',
        },
        {
          title: 'Select KPI Category',
          description: 'Choose from predefined KPI categories',
          action: 'Select "Employee Engagement" category',
        },
        {
          title: 'Configure Targets',
          description: 'Set target values and measurement frequency',
          action: 'Set target values and choose measurement frequency',
        },
        {
          title: 'Add to Dashboard',
          description: 'Add the KPI to your main dashboard',
          action: 'Click "Add to Dashboard" to start tracking',
        },
      ],
    },
  ];

  const faqs: FAQ[] = [
    {
      id: 'faq-1',
      question: 'How often should we conduct employee engagement surveys?',
      answer: 'For pulse surveys, monthly or quarterly is recommended. Annual comprehensive surveys should be conducted once per year. The frequency depends on your organization size and change rate.',
      category: 'Surveys',
      tags: ['frequency', 'engagement', 'timing'],
    },
    {
      id: 'faq-2',
      question: 'What is a good employee engagement score?',
      answer: 'Industry benchmarks suggest that an engagement score above 70% is good, above 80% is excellent. However, focus on trends and improvement over time rather than absolute numbers.',
      category: 'KPIs',
      tags: ['benchmarks', 'engagement', 'scoring'],
    },
    {
      id: 'faq-3',
      question: 'How do I ensure survey anonymity?',
      answer: 'Enable the "Anonymous" setting when creating surveys. Anonymous responses cannot be traced back to individual employees. For sensitive topics, anonymity increases response rates and honesty.',
      category: 'Privacy',
      tags: ['anonymity', 'privacy', 'responses'],
    },
    {
      id: 'faq-4',
      question: 'Can I export survey results?',
      answer: 'Yes, all survey results can be exported in multiple formats (CSV, PDF, Excel). Go to the survey results page and click the "Export" button.',
      category: 'Data Export',
      tags: ['export', 'data', 'results'],
    },
  ];

  const categories = ['All', 'Getting Started', 'Surveys', 'Analytics', 'KPIs', 'Privacy', 'Data Export'];

  const filteredArticles = helpArticles.filter(article =>
    (selectedTab === 0 || article.category === categories[selectedTab]) &&
    (searchQuery === '' || 
     article.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
     article.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
     article.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase())))
  );

  const filteredFAQs = faqs.filter(faq =>
    (selectedTab === 0 || faq.category === categories[selectedTab]) &&
    (searchQuery === '' || 
     faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
     faq.answer.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'success';
      case 'intermediate': return 'warning';
      case 'advanced': return 'error';
      default: return 'default';
    }
  };

  const handleTutorialStart = (tutorial: Tutorial) => {
    setSelectedTutorial(tutorial);
    setCurrentStep(0);
    setTutorialOpen(true);
  };

  const handleTutorialNext = () => {
    if (selectedTutorial && currentStep < selectedTutorial.steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleTutorialPrev = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleTutorialComplete = () => {
    setTutorialOpen(false);
    setSelectedTutorial(null);
    setCurrentStep(0);
  };

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
          Help Center
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          Find answers, learn best practices, and get the most out of your HR Dashboard
        </Typography>

        {/* Search */}
        <TextField
          fullWidth
          placeholder="Search help articles, tutorials, and FAQs..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search />
              </InputAdornment>
            ),
          }}
          sx={{ maxWidth: 600 }}
        />
      </Box>

      {/* Quick Actions */}
      <Grid container spacing={2} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardActionArea onClick={() => handleTutorialStart(tutorials[0])}>
              <CardContent sx={{ textAlign: 'center', py: 3 }}>
                <PlayArrow sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                <Typography variant="h6">Interactive Tours</Typography>
                <Typography variant="body2" color="text.secondary">
                  Guided walkthroughs of key features
                </Typography>
              </CardContent>
            </CardActionArea>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardActionArea>
              <CardContent sx={{ textAlign: 'center', py: 3 }}>
                <VideoLibrary sx={{ fontSize: 40, color: 'secondary.main', mb: 1 }} />
                <Typography variant="h6">Video Tutorials</Typography>
                <Typography variant="body2" color="text.secondary">
                  Watch step-by-step video guides
                </Typography>
              </CardContent>
            </CardActionArea>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardActionArea>
              <CardContent sx={{ textAlign: 'center', py: 3 }}>
                <Book sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
                <Typography variant="h6">Documentation</Typography>
                <Typography variant="body2" color="text.secondary">
                  Comprehensive user guides
                </Typography>
              </CardContent>
            </CardActionArea>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardActionArea>
              <CardContent sx={{ textAlign: 'center', py: 3 }}>
                <Feedback sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
                <Typography variant="h6">Contact Support</Typography>
                <Typography variant="body2" color="text.secondary">
                  Get help from our team
                </Typography>
              </CardContent>
            </CardActionArea>
          </Card>
        </Grid>
      </Grid>

      {/* Category Tabs */}
      <Tabs
        value={selectedTab}
        onChange={(e, newValue) => setSelectedTab(newValue)}
        sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}
      >
        {categories.map((category, index) => (
          <Tab key={category} label={category} />
        ))}
      </Tabs>

      {/* Content Sections */}
      <Grid container spacing={4}>
        {/* Help Articles */}
        <Grid item xs={12} md={6}>
          <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            <Book sx={{ mr: 1 }} />
            Help Articles
          </Typography>
          <Box sx={{ space: 2 }}>
            {filteredArticles.map((article) => (
              <Card key={article.id} sx={{ mb: 2, cursor: 'pointer' }} onClick={() => setSelectedArticle(article)}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                    <Typography variant="h6" component="div">
                      {article.title}
                    </Typography>
                    <Chip
                      label={article.difficulty}
                      size="small"
                      color={getDifficultyColor(article.difficulty) as any}
                    />
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {article.description}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 1 }}>
                    {article.tags.map((tag) => (
                      <Chip key={tag} label={tag} size="small" variant="outlined" />
                    ))}
                  </Box>
                  <Typography variant="caption" color="text.secondary">
                    {article.estimatedTime} read • Updated {article.lastUpdated}
                  </Typography>
                </CardContent>
              </Card>
            ))}
          </Box>
        </Grid>

        {/* FAQs */}
        <Grid item xs={12} md={6}>
          <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            <Quiz sx={{ mr: 1 }} />
            Frequently Asked Questions
          </Typography>
          <Box>
            {filteredFAQs.map((faq) => (
              <Accordion key={faq.id}>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant="subtitle1">{faq.question}</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography variant="body2" sx={{ mb: 2 }}>
                    {faq.answer}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {faq.tags.map((tag) => (
                      <Chip key={tag} label={tag} size="small" variant="outlined" />
                    ))}
                  </Box>
                </AccordionDetails>
              </Accordion>
            ))}
          </Box>
        </Grid>
      </Grid>

      {/* Article Detail Dialog */}
      <Dialog
        open={!!selectedArticle}
        onClose={() => setSelectedArticle(null)}
        maxWidth="md"
        fullWidth
      >
        {selectedArticle && (
          <>
            <DialogTitle>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                {selectedArticle.title}
                <Box sx={{ display: 'flex', gap: 1 }}>
                  {selectedArticle.videoUrl && (
                    <IconButton>
                      <PlayArrow />
                    </IconButton>
                  )}
                  <IconButton>
                    <Share />
                  </IconButton>
                  <IconButton>
                    <Download />
                  </IconButton>
                </Box>
              </Box>
            </DialogTitle>
            <DialogContent>
              <Box sx={{ mb: 2 }}>
                <Chip
                  label={selectedArticle.difficulty}
                  size="small"
                  color={getDifficultyColor(selectedArticle.difficulty) as any}
                  sx={{ mr: 1 }}
                />
                <Chip label={selectedArticle.estimatedTime} size="small" variant="outlined" />
              </Box>
              <Typography variant="body1" sx={{ whiteSpace: 'pre-line', lineHeight: 1.7 }}>
                {selectedArticle.content}
              </Typography>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setSelectedArticle(null)}>Close</Button>
              <Button variant="contained" startIcon={<Feedback />}>
                Was this helpful?
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>

      {/* Interactive Tutorial Dialog */}
      <Dialog
        open={tutorialOpen}
        onClose={() => setTutorialOpen(false)}
        maxWidth="md"
        fullWidth
      >
        {selectedTutorial && (
          <>
            <DialogTitle>
              {selectedTutorial.title}
            </DialogTitle>
            <DialogContent>
              <Box sx={{ mb: 3 }}>
                <Typography variant="body1" color="text.secondary">
                  {selectedTutorial.description}
                </Typography>
              </Box>
              
              <Stepper activeStep={currentStep} orientation="vertical">
                {selectedTutorial.steps.map((step, index) => (
                  <Step key={index}>
                    <StepLabel>
                      {step.title}
                    </StepLabel>
                    <StepContent>
                      <Typography variant="body2" sx={{ mb: 2 }}>
                        {step.description}
                      </Typography>
                      {step.action && (
                        <Paper sx={{ p: 2, bgcolor: 'grey.50', mb: 2 }}>
                          <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                            <strong>Action:</strong> {step.action}
                          </Typography>
                        </Paper>
                      )}
                    </StepContent>
                  </Step>
                ))}
              </Stepper>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleTutorialComplete}>Close</Button>
              <Button onClick={handleTutorialPrev} disabled={currentStep === 0}>
                Previous
              </Button>
              {currentStep < selectedTutorial.steps.length - 1 ? (
                <Button variant="contained" onClick={handleTutorialNext}>
                  Next
                </Button>
              ) : (
                <Button variant="contained" onClick={handleTutorialComplete} startIcon={<CheckCircle />}>
                  Complete
                </Button>
              )}
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default HelpCenter; 