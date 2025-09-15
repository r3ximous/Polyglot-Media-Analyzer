import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  Alert,
  Grid,
  Divider
} from '@mui/material';
import {
  CheckCircle,
  Error,
  AccessTime,
  Psychology,
  Translate,
  Summarize,
  Visibility
} from '@mui/icons-material';
import { getProcessingStatus } from '../services/api';

const ProcessingStatus = ({ fileId }) => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!fileId) return;

    const checkStatus = async () => {
      try {
        const statusData = await getProcessingStatus(fileId);
        setStatus(statusData);
        setLoading(false);

        // Poll for updates if still processing
        if (statusData.status === 'processing' || statusData.status === 'uploaded') {
          setTimeout(checkStatus, 3000);
        }
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to get status');
        setLoading(false);
      }
    };

    checkStatus();
  }, [fileId]);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle color="success" />;
      case 'error':
        return <Error color="error" />;
      case 'processing':
      case 'uploaded':
        return <AccessTime color="primary" />;
      default:
        return <AccessTime />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'error':
        return 'error';
      case 'processing':
        return 'primary';
      case 'uploaded':
        return 'secondary';
      default:
        return 'default';
    }
  };

  const getTaskIcon = (taskType) => {
    switch (taskType) {
      case 'transcription':
        return <Psychology />;
      case 'translation':
        return <Translate />;
      case 'summarization':
        return <Summarize />;
      case 'sentiment':
        return <Psychology />;
      case 'object_detection':
        return <Visibility />;
      default:
        return <AccessTime />;
    }
  };

  if (loading) {
    return (
      <Box sx={{ mb: 4 }}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Checking processing status...
            </Typography>
            <LinearProgress />
          </CardContent>
        </Card>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 4 }}>
        {error}
      </Alert>
    );
  }

  if (!status) return null;

  return (
    <Box sx={{ mb: 4 }}>
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            {getStatusIcon(status.status)}
            <Typography variant="h6" sx={{ ml: 1 }}>
              Processing Status
            </Typography>
            <Chip
              label={status.status.toUpperCase()}
              color={getStatusColor(status.status)}
              sx={{ ml: 'auto' }}
            />
          </Box>

          <Typography variant="body2" color="text.secondary" gutterBottom>
            File ID: {status.file_id}
          </Typography>

          {status.status === 'processing' && (
            <>
              <LinearProgress sx={{ my: 2 }} />
              <Typography variant="body2" color="text.secondary">
                {status.current_task ? `Current task: ${status.current_task}` : 'Processing...'}
              </Typography>
            </>
          )}

          {status.status === 'error' && status.error_message && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {status.error_message}
            </Alert>
          )}

          {status.results && Object.keys(status.results).length > 0 && (
            <>
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle1" gutterBottom>
                Available Results:
              </Typography>
              <Grid container spacing={1}>
                {Object.keys(status.results).map((taskType) => (
                  <Grid item key={taskType}>
                    <Chip
                      icon={getTaskIcon(taskType)}
                      label={taskType.replace('_', ' ').toUpperCase()}
                      variant="outlined"
                      color="primary"
                      size="small"
                    />
                  </Grid>
                ))}
              </Grid>
            </>
          )}

          {status.status === 'completed' && (
            <Alert severity="success" sx={{ mt: 2 }}>
              Processing completed successfully! All analysis results are now available.
            </Alert>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default ProcessingStatus;