import React, { useState } from 'react';
import { useDropzone, Accept } from 'react-dropzone';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  LinearProgress,
  Alert,
  Paper,
  Grid,
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  Description as DescriptionIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { toast } from 'react-toastify';
import { uploadFile } from '../services/api';
import { Job } from '../types';

interface UploadScreenProps {
  onJobCreated: (job: Job) => void;
}

const UploadScreen: React.FC<UploadScreenProps> = ({ onJobCreated }) => {
  const [selectedTemplate, setSelectedTemplate] = useState<'Extraction Template 1' | 'Extraction Template 2'>('Extraction Template 1');
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const onDrop = async (acceptedFiles: File[]): Promise<void> => {
    if (acceptedFiles.length === 0) {
      toast.error('Please select a valid PDF file');
      return;
    }

    const file = acceptedFiles[0];

    if (file.type !== 'application/pdf') {
      toast.error('Only PDF files are accepted');
      return;
    }

    setUploading(true);
    setUploadProgress(0);

    try {
      let progress = 0;
      const progressInterval = setInterval(() => {
        progress = Math.min(progress + 10, 90);
        setUploadProgress(progress);
      }, 200);

      const response = await uploadFile(file, selectedTemplate);

      clearInterval(progressInterval);
      setUploadProgress(100);

      // Convert UploadResponse to Job
      const job: Job = {
        taskId: response.task_id,
        filename: file.name,
        template: selectedTemplate,
        status: 'processing',
        uploadedAt: new Date(),
        progress: 0
      };

      toast.success('File uploaded successfully!');
      onJobCreated(job);

      setTimeout(() => setUploadProgress(0), 800); // brief delay to show 100%

    } catch (error: any) {
      toast.error(error.message || 'Upload failed. Please try again.');
      setUploadProgress(0);
    } finally {
      setUploading(false);
    }
  };

  const acceptTypes: Accept = {
    'application/pdf': ['.pdf']
  };

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: acceptTypes,
    maxFiles: 1,
    disabled: uploading,
  });

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', px: 3 }}>
   

      {/* Template Selection */}
      <Card 
        sx={{ 
          mb: 4,
          borderRadius: 9,
          boxShadow: '0 8px 32px rgba(0,0,0,0.08)',
          background: 'linear-gradient(to bottom, #ffffff 0%, #f8f9fa 100%)',
          border: '1px solid rgba(30, 60, 114, 0.1)',
        }}
      >
        <CardContent sx={{ p: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <AssessmentIcon sx={{ fontSize: 32, mr: 2, color: '#1e3c72' }} />
            <Typography 
              variant="h5" 
              sx={{ 
                fontWeight: 700,
                background: 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              Choose Your Extraction Template
            </Typography>
          </Box>

      <Grid container spacing={2}>
  {/* Template 1 */}
  <Grid item xs={12} sm={6} md={6}>
    <Paper
      elevation={selectedTemplate === 'Extraction Template 1' ? 8 : 2}
      onClick={() => setSelectedTemplate('Extraction Template 1')}
      sx={{
        p: { xs: 2, sm: 3 }, // smaller padding for mobile
        cursor: uploading ? 'not-allowed' : 'pointer',
        borderRadius: 2.5,
        border: selectedTemplate === 'Extraction Template 1' 
          ? '3px solid #667eea' 
          : '1.5px solid rgba(0,0,0,0.08)',
        background: selectedTemplate === 'Extraction Template 1'
          ? 'linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%)'
          : 'white',
        transition: 'all 0.3s ease',
        position: 'relative',
        '&:hover': {
          transform: uploading ? 'none' : 'translateY(-2px)',
          boxShadow: uploading ? 'none' : '0 8px 16px rgba(102, 126, 234, 0.15)'
        },
        textAlign: 'center',
      }}
    >
      {selectedTemplate === 'Extraction Template 1' && (
        <Box sx={{ position: 'absolute', top: 8, right: 8, backgroundColor: '#667eea', borderRadius: '50%', p: 0.5 }}>
          <CheckCircleIcon sx={{ color: 'white', fontSize: 20 }} />
        </Box>
      )}

      <Box sx={{ width: 50, height: 50, borderRadius: 1.5, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', mx: 'auto', mb: 1.5 }}>
        <DescriptionIcon sx={{ fontSize: 28, color: 'white' }} />
      </Box>

      <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 700, color: '#1e3c72' }}>
        Template 1: Comprehensive
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
        Deep dive into fund data with detailed extraction
      </Typography>
    </Paper>
  </Grid>

  {/* Template 2 */}
  <Grid item xs={12} sm={6} md={6}>
    <Paper
      elevation={selectedTemplate === 'Extraction Template 2' ? 8 : 2}
      onClick={() => setSelectedTemplate('Extraction Template 2')}
      sx={{
        p: { xs: 2, sm: 3 },
        cursor: uploading ? 'not-allowed' : 'pointer',
        borderRadius: 2.5,
        border: selectedTemplate === 'Extraction Template 2' 
          ? '3px solid #f5576c' 
          : '1.5px solid rgba(0,0,0,0.08)',
        background: selectedTemplate === 'Extraction Template 2'
          ? 'linear-gradient(135deg, rgba(240, 147, 251, 0.08) 0%, rgba(245, 87, 108, 0.08) 100%)'
          : 'white',
        transition: 'all 0.3s ease',
        position: 'relative',
        '&:hover': {
          transform: uploading ? 'none' : 'translateY(-2px)',
          boxShadow: uploading ? 'none' : '0 8px 16px rgba(245, 87, 108, 0.15)'
        },
        textAlign: 'center',
      }}
    >
      {selectedTemplate === 'Extraction Template 2' && (
        <Box sx={{ position: 'absolute', top: 8, right: 8, backgroundColor: '#f5576c', borderRadius: '50%', p: 0.5 }}>
          <CheckCircleIcon sx={{ color: 'white', fontSize: 20 }} />
        </Box>
      )}

      <Box sx={{ width: 50, height: 50, borderRadius: 1.5, background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', mx: 'auto', mb: 1.5 }}>
        <TrendingUpIcon sx={{ fontSize: 28, color: 'white' }} />
      </Box>

      <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 700, color: '#1e3c72' }}>
        Template 2: Performance
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
        Portfolio-centric analysis with KPIs
      </Typography>
    </Paper>
  </Grid>
</Grid>





        </CardContent>
      </Card>

      {/* Premium Upload Area */}
      <Card
        sx={{
          borderRadius: 9,
          boxShadow: '0 8px 32px rgba(0,0,0,0.08)',
          border: '1px solid rgba(30, 60, 114, 0.1)',
        }}
      >
        <CardContent sx={{ p: 4 }}>
          <Box
            {...getRootProps()}
            sx={{
              border: 3,
              borderColor: isDragActive
                ? '#667eea'
                : isDragReject
                ? '#f5576c'
                : 'rgba(30, 60, 114, 0.2)',
              borderStyle: 'dashed',
              borderRadius: 4,
              p: 8,
              textAlign: 'center',
              cursor: uploading ? 'not-allowed' : 'pointer',
              background: isDragActive
                ? 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)'
                : isDragReject
                ? 'linear-gradient(135deg, rgba(245, 87, 108, 0.1) 0%, rgba(240, 147, 251, 0.1) 100%)'
                : 'linear-gradient(to bottom, #ffffff 0%, #f8f9fa 100%)',
              transition: 'all 0.3s ease',
              '&:hover': {
                backgroundColor: uploading ? 'transparent' : 'rgba(102, 126, 234, 0.05)',
                borderColor: uploading ? 'rgba(30, 60, 114, 0.2)' : '#667eea',
                transform: uploading ? 'none' : 'translateY(-2px)',
              },
            }}
          >
            <input {...getInputProps()} />
            
            <motion.div
              animate={uploading ? { rotate: 360 } : { rotate: 0 }}
              transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            >
              <DescriptionIcon sx={{ fontSize: 80, color: '#1e3c72', mb: 3 }} />
            </motion.div>

            {uploading ? (
              <>
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 700, color: '#1e3c72' }}>
                  Processing Your Document...
                </Typography>
                <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                  AI is extracting data with precision
                </Typography>
                <Box sx={{ maxWidth: 400, mx: 'auto' }}>
                  <LinearProgress 
                    variant="determinate" 
                    value={uploadProgress}
                    sx={{
                      height: 10,
                      borderRadius: 5,
                      backgroundColor: 'rgba(102, 126, 234, 0.2)',
                      '& .MuiLinearProgress-bar': {
                        background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
                        borderRadius: 5,
                      }
                    }}
                  />
                  <Typography variant="body2" sx={{ mt: 1, color: '#667eea', fontWeight: 600 }}>
                    {uploadProgress}% Complete
                  </Typography>
                </Box>
              </>
            ) : (
              <>
                {isDragActive ? (
                  <Typography variant="h5" gutterBottom sx={{ fontWeight: 700, color: '#667eea' }}>
                    Drop your PDF here
                  </Typography>
                ) : (
                  <>
                    <Typography variant="h5" gutterBottom sx={{ fontWeight: 700, color: '#1e3c72' }}>
                      Drag & Drop Your PDF
                    </Typography>
                    <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                      or click to browse from your computer
                    </Typography>
                    <Button
                      variant="contained"
                      size="large"
                      startIcon={<CloudUploadIcon />}
                      sx={{
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        color: 'white',
                        px: 5,
                        py: 1.5,
                        borderRadius: 3,
                        fontSize: '1.1rem',
                        fontWeight: 700,
                        textTransform: 'none',
                        boxShadow: '0 8px 16px rgba(102, 126, 234, 0.3)',
                        '&:hover': {
                          background: 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)',
                          boxShadow: '0 12px 24px rgba(102, 126, 234, 0.4)',
                          transform: 'translateY(-2px)',
                        },
                        transition: 'all 0.3s ease',
                      }}
                    >
                      Select PDF File
                    </Button>
                  </>
                )}

                <Box sx={{ mt: 4, pt: 3, borderTop: '1px solid rgba(0,0,0,0.08)' }}>
                  <Typography variant="body2" color="text.secondary">
                    Supported format: PDF • Maximum file size: 50MB
                  </Typography>
                </Box>
              </>
            )}
          </Box>

          {isDragReject && (
            <Alert severity="error" sx={{ mt: 3, borderRadius: 2 }}>
              Invalid file type. Please upload a PDF file only.
            </Alert>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default UploadScreen;
