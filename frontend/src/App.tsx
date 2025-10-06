import React, { useState, useEffect } from 'react';
import {
  Container,
  AppBar,
  Toolbar,
  Typography,
  Box,
  Tab,
  Tabs,
} from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import UploadScreen from './components/UploadScreen';
import Dashboard from './components/Dashboard';
import { getJobStatus } from './services/api';
import { Job } from './types';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel({ children, value, index }: TabPanelProps) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const App: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [jobs, setJobs] = useState<Job[]>([]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const addJob = (job: Job) => {
    setJobs(prevJobs => [...prevJobs, job]);
    setTabValue(1); // Switch to dashboard after upload
  };

  const updateJob = (taskId: string, updates: Partial<Job>) => {
    setJobs(prevJobs =>
      prevJobs.map(job =>
        job.taskId === taskId ? { ...job, ...updates } : job
      )
    );
  };

  // Poll for job status updates
  useEffect(() => {
    const interval = setInterval(() => {
      const processingJobs = jobs.filter(job => job.status === 'processing');
      
      processingJobs.forEach(async (job) => {
        try {
          const data = await getJobStatus(job.taskId);
          updateJob(job.taskId, {
            status: data.status,
            downloadUrl: data.download_url,
            error: data.error,
            progress: data.progress,
          });
        } catch (error) {
          console.error('Error polling job status:', error);
        }
      });
    }, 2000);

    return () => clearInterval(interval);
  }, [jobs]);

  return (
    <Box sx={{ flexGrow: 1, minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      <AppBar position="static" elevation={0} sx={{ backgroundColor: '#1976d2' }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
            PDF Data Extractor
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.8 }}>
            Professional Financial Data Processing
          </Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs
            value={tabValue}
            onChange={handleTabChange}
            aria-label="navigation tabs"
            sx={{
              '& .MuiTab-root': {
                textTransform: 'none',
                fontWeight: 500,
                fontSize: '1rem',
              },
            }}
          >
            <Tab label="Upload Files" />
            <Tab label={`Dashboard ${jobs.length > 0 ? `(${jobs.length})` : ''}`} />
          </Tabs>
        </Box>

        <AnimatePresence mode="wait">
          <motion.div
            key={tabValue}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <TabPanel value={tabValue} index={0}>
              <UploadScreen onJobCreated={addJob} />
            </TabPanel>
            <TabPanel value={tabValue} index={1}>
              <Dashboard jobs={jobs} onJobUpdate={updateJob} />
            </TabPanel>
          </motion.div>
        </AnimatePresence>
      </Container>
    </Box>
  );
};

export default App;