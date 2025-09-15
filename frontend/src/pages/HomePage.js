import React, { useState } from 'react';
import { Container, Box, Typography, Tabs, Tab } from '@mui/material';
import FileUpload from '../components/FileUpload';
import ProcessingStatus from '../components/ProcessingStatus';
import ResultsDisplay from '../components/ResultsDisplay';
import SearchInterface from '../components/SearchInterface';

const HomePage = () => {
  const [currentFile, setCurrentFile] = useState(null);
  const [activeTab, setActiveTab] = useState(0);

  const handleUploadComplete = (uploadResult) => {
    setCurrentFile(uploadResult);
    setActiveTab(1); // Switch to processing status tab
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ py: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom align="center">
          Polyglot Media Analyzer
        </Typography>
        <Typography variant="h6" color="text.secondary" align="center" sx={{ mb: 4 }}>
          AI-powered multilingual video and audio analysis platform
        </Typography>

        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs value={activeTab} onChange={handleTabChange} aria-label="main navigation tabs">
            <Tab label="Upload" />
            <Tab label="Processing Status" disabled={!currentFile} />
            <Tab label="Results" disabled={!currentFile} />
            <Tab label="Search" />
          </Tabs>
        </Box>

        <Box sx={{ mt: 3 }}>
          {activeTab === 0 && (
            <Box>
              <Typography variant="h5" gutterBottom>
                Upload Media File
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                Upload a video or audio file to start the analysis. Our AI will provide transcription, 
                translation, summarization, sentiment analysis, and object detection.
              </Typography>
              <FileUpload onUploadComplete={handleUploadComplete} />
            </Box>
          )}

          {activeTab === 1 && currentFile && (
            <Box>
              <Typography variant="h5" gutterBottom>
                Processing Status
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                Track the progress of your media analysis. Processing includes transcription, 
                summarization, sentiment analysis, and object detection.
              </Typography>
              <ProcessingStatus fileId={currentFile.file_id} />
            </Box>
          )}

          {activeTab === 2 && currentFile && (
            <Box>
              <Typography variant="h5" gutterBottom>
                Analysis Results
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                View and interact with the analysis results. You can translate content, 
                create highlight reels, and explore detailed insights.
              </Typography>
              <ResultsDisplay 
                fileId={currentFile.file_id} 
                fileType={currentFile.file_type}
              />
            </Box>
          )}

          {activeTab === 3 && (
            <Box>
              <Typography variant="h5" gutterBottom>
                Search Content
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                Search through all analyzed media content using natural language queries. 
                Filter by file type, language, sentiment, and more.
              </Typography>
              <SearchInterface />
            </Box>
          )}
        </Box>
      </Box>
    </Container>
  );
};

export default HomePage;