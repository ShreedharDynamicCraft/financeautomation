import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  ToggleButton,
  ToggleButtonGroup,
  LinearProgress,
  Alert,
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  Description as DescriptionIcon,
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

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    // Validate file type
    if (file.type !== 'application/pdf') {
      toast.error('Please upload a PDF file only');
      return;
    }

    // Validate file size (50MB limit)
    if (file.size > 50 * 1024 * 1024) {
      toast.error('File size must be less than 50MB');
      return;
    }

    setUploading(true);
    setUploadProgress(0);

    try {
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      const response = await uploadFile(file, selectedTemplate);
      
      clearInterval(progressInterval);
      setUploadProgress(100);

      const newJob: Job = {
        taskId: response.task_id,
        filename: file.name,
        template: selectedTemplate,
        status: 'processing',
        uploadedAt: new Date(),
      };

      onJobCreated(newJob);
      toast.success('File uploaded successfully! Processing started.');
      
      // Reset state
      setTimeout(() => {
        setUploadProgress(0);
        setUploading(false);
      }, 1000);

    } catch (error: any) {
      console.error('Upload error:', error);
      setUploadProgress(0);
      setUploading(false);
      toast.error(error.message || 'Upload failed. Please try again.');
    }
  }, [selectedTemplate, onJobCreated]);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    maxFiles: 1,
    disabled: uploading,
  });

  const handleTemplateChange = (event: React.MouseEvent<HTMLElement>, newTemplate: 'Extraction Template 1' | 'Extraction Template 2' | null) => {
    if (newTemplate !== null) {
      setSelectedTemplate(newTemplate);
    }
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto' }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Typography variant="h4" component="h1" gutterBottom align="center" sx={{ mb: 4 }}>
          Upload PDF for Data Extraction
        </Typography>

        {/* Template Selection */}
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Select Extraction Template
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Choose the template that best matches your document type
            </Typography>
            <ToggleButtonGroup
              value={selectedTemplate}
              exclusive
              onChange={handleTemplateChange}
              aria-label="extraction template"
              fullWidth
              sx={{ mb: 2 }}
            >
              <ToggleButton 
                value="Extraction Template 1" 
                aria-label="template 1"
                sx={{ py: 2, flex: 1 }}
              >
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                    Template 1
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Comprehensive Fund Analysis
                  </Typography>
                </Box>
              </ToggleButton>
              <ToggleButton 
                value="Extraction Template 2" 
                aria-label="template 2"
                sx={{ py: 2, flex: 1 }}
              >
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                    Template 2
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Portfolio Summary Report
                  </Typography>
                </Box>
              </ToggleButton>
            </ToggleButtonGroup>
            
            {selectedTemplate === 'Extraction Template 1' && (
              <Alert severity="info" sx={{ mt: 2 }}>
                <strong>Template 1:</strong> Extracts comprehensive fund data including fund details, manager information, and detailed investment positions.
              </Alert>
            )}
            
            {selectedTemplate === 'Extraction Template 2' && (
              <Alert severity="info" sx={{ mt: 2 }}>
                <strong>Template 2:</strong> Focuses on portfolio summary metrics and schedule of investments with key performance indicators.
              </Alert>
            )}
          </CardContent>
        </Card>

        {/* File Upload Area */}
        <Card>
          <CardContent>
            <Box
              {...getRootProps()}
              sx={{
                border: 2,
                borderColor: isDragActive
                  ? 'primary.main'
                  : isDragReject
                  ? 'error.main'
                  : 'grey.300',
                borderStyle: 'dashed',
                borderRadius: 2,
                p: 6,
                textAlign: 'center',
                cursor: uploading ? 'not-allowed' : 'pointer',
                backgroundColor: isDragActive
                  ? 'action.hover'
                  : isDragReject
                  ? 'error.light'
                  : 'background.paper',
                transition: 'all 0.2s ease-in-out',
                '&:hover': {
                  backgroundColor: uploading ? 'background.paper' : 'action.hover',
                  borderColor: uploading ? 'grey.300' : 'primary.main',
                },
              }}
            >
              <input {...getInputProps()} />
              
              <motion.div
                animate={isDragActive ? { scale: 1.05 } : { scale: 1 }}
                transition={{ type: "spring", stiffness: 300, damping: 30 }}
              >
                {uploading ? (
                  <DescriptionIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
                ) : (
                  <CloudUploadIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
                )}
              </motion.div>

              {uploading ? (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Uploading...
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={uploadProgress} 
                    sx={{ 
                      mt: 2, 
                      mb: 2,
                      height: 8,
                      borderRadius: 4,
                    }} 
                  />
                  <Typography variant="body2" color="text.secondary">
                    {uploadProgress}% complete
                  </Typography>
                </Box>
              ) : (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    {isDragActive
                      ? 'Drop your PDF file here'
                      : 'Drag & drop a PDF file here, or click to select'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                    Supports PDF files up to 50MB
                  </Typography>
                  
                  {isDragReject && (
                    <Typography variant="body2" color="error" sx={{ mb: 2 }}>
                      Only PDF files are accepted
                    </Typography>
                  )}

                  <Button
                    variant="contained"
                    size="large"
                    startIcon={<CloudUploadIcon />}
                    disabled={uploading}
                    sx={{ mt: 2 }}
                  >
                    Choose File
                  </Button>
                </Box>
              )}
            </Box>
          </CardContent>
        </Card>
      </motion.div>
    </Box>
  );
};

export default UploadScreen;