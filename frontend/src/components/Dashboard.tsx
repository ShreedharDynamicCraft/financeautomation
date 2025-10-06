import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Button,
  Grid,
  LinearProgress,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  Description as DescriptionIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'react-toastify';
import { getJobStatus, downloadFile } from '../services/api';
import { Job } from '../types';

interface DashboardProps {
  jobs: Job[];
  onJobUpdate: (taskId: string, updates: Partial<Job>) => void;
}

const Dashboard: React.FC<DashboardProps> = ({ jobs, onJobUpdate }) => {
  const handleDownload = async (job: Job) => {
    if (!job.downloadUrl) {
      toast.error('Download URL not available');
      return;
    }

    try {
      const blob = await downloadFile(job.downloadUrl);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${job.filename.replace('.pdf', '')}_extracted.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast.success('File downloaded successfully!');
    } catch (error) {
      console.error('Download error:', error);
      toast.error('Failed to download file');
    }
  };

  const handleRefreshStatus = async (job: Job) => {
    try {
      const data = await getJobStatus(job.taskId);
      onJobUpdate(job.taskId, {
        status: data.status,
        downloadUrl: data.download_url,
        error: data.error,
        progress: data.progress,
      });
      toast.info('Status refreshed');
    } catch (error) {
      console.error('Error refreshing status:', error);
      toast.error('Failed to refresh status');
    }
  };

  const getStatusIcon = (status: Job['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon color="success" />;
      case 'failed':
        return <ErrorIcon color="error" />;
      case 'processing':
        return <ScheduleIcon color="primary" />;
      default:
        return <ScheduleIcon />;
    }
  };

  const getStatusColor = (status: Job['status']) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      case 'processing':
        return 'primary';
      default:
        return 'default';
    }
  };

  const formatTime = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  if (jobs.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 8 }}>
        <DescriptionIcon sx={{ fontSize: 64, color: 'grey.400', mb: 2 }} />
        <Typography variant="h6" color="text.secondary" gutterBottom>
          No jobs yet
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Upload a PDF file to get started with data extraction
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h5" component="h2" gutterBottom sx={{ mb: 4 }}>
        Extraction Jobs ({jobs.length})
      </Typography>

      <Grid container spacing={3}>
        <AnimatePresence>
          {jobs.map((job, index) => (
            <Grid item xs={12} md={6} lg={4} key={job.taskId}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                whileHover={{ y: -4 }}
              >
                <Card sx={{ height: '100%', position: 'relative' }}>
                  <CardContent>
                    {/* Header */}
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <DescriptionIcon sx={{ mr: 1, color: 'primary.main' }} />
                      <Box sx={{ flexGrow: 1, minWidth: 0 }}>
                        <Typography 
                          variant="h6" 
                          noWrap 
                          title={job.filename}
                          sx={{ fontSize: '1rem' }}
                        >
                          {job.filename}
                        </Typography>
                      </Box>
                      <Tooltip title="Refresh status">
                        <IconButton
                          size="small"
                          onClick={() => handleRefreshStatus(job)}
                          disabled={job.status === 'completed'}
                        >
                          <RefreshIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>

                    {/* Template and Status */}
                    <Box sx={{ mb: 2 }}>
                      <Chip
                        label={job.template}
                        size="small"
                        variant="outlined"
                        sx={{ mb: 1, fontSize: '0.75rem' }}
                      />
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {getStatusIcon(job.status)}
                        <Chip
                          label={job.status.charAt(0).toUpperCase() + job.status.slice(1)}
                          color={getStatusColor(job.status) as any}
                          size="small"
                          sx={{ fontWeight: 500 }}
                        />
                      </Box>
                    </Box>

                    {/* Progress Bar */}
                    {job.status === 'processing' && (
                      <Box sx={{ mb: 2 }}>
                        <LinearProgress 
                          variant={job.progress ? 'determinate' : 'indeterminate'}
                          value={job.progress || 0}
                          sx={{ 
                            height: 6, 
                            borderRadius: 3,
                          }}
                        />
                        {job.progress && (
                          <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                            {job.progress}% complete
                          </Typography>
                        )}
                      </Box>
                    )}

                    {/* Error Message */}
                    {job.status === 'failed' && job.error && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" color="error" sx={{ fontSize: '0.875rem' }}>
                          Error: {job.error}
                        </Typography>
                      </Box>
                    )}

                    {/* Timestamps */}
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="caption" color="text.secondary" display="block">
                        Uploaded: {formatTime(job.uploadedAt)}
                      </Typography>
                      {job.completedAt && (
                        <Typography variant="caption" color="text.secondary" display="block">
                          Completed: {formatTime(job.completedAt)}
                        </Typography>
                      )}
                    </Box>

                    {/* Download Button */}
                    <Box sx={{ pt: 1 }}>
                      <Button
                        variant="contained"
                        startIcon={<DownloadIcon />}
                        onClick={() => handleDownload(job)}
                        disabled={job.status !== 'completed' || !job.downloadUrl}
                        fullWidth
                        sx={{ 
                          borderRadius: 2,
                          textTransform: 'none',
                        }}
                      >
                        {job.status === 'completed' ? 'Download Excel' : 'Processing...'}
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </AnimatePresence>
      </Grid>
    </Box>
  );
};

export default Dashboard;