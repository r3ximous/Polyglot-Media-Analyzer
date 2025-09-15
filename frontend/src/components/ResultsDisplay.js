import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  Alert,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Button,
  TextField,
  MenuItem,
  Divider
} from '@mui/material';
import {
  ExpandMore,
  Translate,
  Psychology,
  Summarize,
  Visibility,
  Movie
} from '@mui/icons-material';
import {
  getTranscription,
  getSummary,
  getSentimentAnalysis,
  getObjectDetection,
  translateContent,
  createHighlightReel
} from '../services/api';

const ResultsDisplay = ({ fileId, fileType }) => {
  const [transcription, setTranscription] = useState(null);
  const [summary, setSummary] = useState(null);
  const [sentiment, setSentiment] = useState(null);
  const [objects, setObjects] = useState(null);
  const [loading, setLoading] = useState({});
  const [errors, setErrors] = useState({});
  
  // Translation states
  const [translationText, setTranslationText] = useState('');
  const [targetLanguage, setTargetLanguage] = useState('es');
  const [translation, setTranslation] = useState(null);
  
  // Highlight reel states
  const [highlightSegments, setHighlightSegments] = useState([{ start: 0, end: 10 }]);
  const [highlightReel, setHighlightReel] = useState(null);

  const languages = [
    { code: 'es', name: 'Spanish' },
    { code: 'fr', name: 'French' },
    { code: 'de', name: 'German' },
    { code: 'it', name: 'Italian' },
    { code: 'pt', name: 'Portuguese' },
    { code: 'ru', name: 'Russian' },
    { code: 'ja', name: 'Japanese' },
    { code: 'ko', name: 'Korean' },
    { code: 'zh', name: 'Chinese' }
  ];

  const fetchData = async (fetchFunction, setter, key) => {
    setLoading(prev => ({ ...prev, [key]: true }));
    setErrors(prev => ({ ...prev, [key]: null }));
    
    try {
      const data = await fetchFunction(fileId);
      setter(data);
    } catch (err) {
      setErrors(prev => ({ ...prev, [key]: err.response?.data?.detail || `Failed to load ${key}` }));
    } finally {
      setLoading(prev => ({ ...prev, [key]: false }));
    }
  };

  useEffect(() => {
    if (!fileId) return;

    // Fetch all available data
    fetchData(getTranscription, setTranscription, 'transcription');
    fetchData(getSummary, setSummary, 'summary');
    fetchData(getSentimentAnalysis, setSentiment, 'sentiment');
    
    if (fileType === 'video') {
      fetchData(getObjectDetection, setObjects, 'objects');
    }
  }, [fileId, fileType]);

  const handleTranslate = async () => {
    if (!translationText.trim()) return;
    
    setLoading(prev => ({ ...prev, translation: true }));
    try {
      const result = await translateContent(fileId, {
        text: translationText,
        source_language: 'auto',
        target_language: targetLanguage
      });
      setTranslation(result);
    } catch (err) {
      setErrors(prev => ({ ...prev, translation: err.response?.data?.detail || 'Translation failed' }));
    } finally {
      setLoading(prev => ({ ...prev, translation: false }));
    }
  };

  const handleCreateHighlightReel = async () => {
    setLoading(prev => ({ ...prev, highlight: true }));
    try {
      const result = await createHighlightReel(fileId, highlightSegments);
      setHighlightReel(result);
    } catch (err) {
      setErrors(prev => ({ ...prev, highlight: err.response?.data?.detail || 'Highlight reel creation failed' }));
    } finally {
      setLoading(prev => ({ ...prev, highlight: false }));
    }
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment.toLowerCase()) {
      case 'positive':
        return 'success';
      case 'negative':
        return 'error';
      default:
        return 'default';
    }
  };

  const renderSection = (title, icon, content, isLoading, error, key) => (
    <Accordion key={key}>
      <AccordionSummary expandIcon={<ExpandMore />}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          {icon}
          <Typography variant="h6" sx={{ ml: 1 }}>
            {title}
          </Typography>
          {isLoading && <CircularProgress size={20} sx={{ ml: 2 }} />}
        </Box>
      </AccordionSummary>
      <AccordionDetails>
        {error ? (
          <Alert severity="error">{error}</Alert>
        ) : (
          content
        )}
      </AccordionDetails>
    </Accordion>
  );

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Analysis Results
      </Typography>

      {/* Transcription */}
      {renderSection(
        'Transcription',
        <Psychology color="primary" />,
        transcription && (
          <Box>
            <Box sx={{ mb: 2 }}>
              <Chip label={`Language: ${transcription.language}`} color="primary" size="small" />
              {transcription.confidence_score && (
                <Chip 
                  label={`Confidence: ${(transcription.confidence_score * 100).toFixed(1)}%`} 
                  color="secondary" 
                  size="small"
                  sx={{ ml: 1 }}
                />
              )}
            </Box>
            <Typography variant="body1" sx={{ textAlign: 'left', lineHeight: 1.6 }}>
              {transcription.text}
            </Typography>
            <Button
              variant="outlined"
              size="small"
              sx={{ mt: 2 }}
              onClick={() => setTranslationText(transcription.text)}
            >
              Use for Translation
            </Button>
          </Box>
        ),
        loading.transcription,
        errors.transcription,
        'transcription'
      )}

      {/* Summary */}
      {renderSection(
        'Summary',
        <Summarize color="primary" />,
        summary && (
          <Box>
            <Chip label={summary.summary_type} color="secondary" size="small" sx={{ mb: 2 }} />
            <Typography variant="body1" sx={{ textAlign: 'left', lineHeight: 1.6 }}>
              {summary.summary_text}
            </Typography>
          </Box>
        ),
        loading.summary,
        errors.summary,
        'summary'
      )}

      {/* Sentiment Analysis */}
      {renderSection(
        'Sentiment Analysis',
        <Psychology color="primary" />,
        sentiment && (
          <Box>
            <Box sx={{ mb: 2 }}>
              <Chip 
                label={`Overall: ${sentiment.overall_sentiment.toUpperCase()}`} 
                color={getSentimentColor(sentiment.overall_sentiment)}
                sx={{ mr: 1 }}
              />
              <Chip 
                label={`Confidence: ${(sentiment.overall_confidence * 100).toFixed(1)}%`} 
                color="secondary" 
                size="small"
              />
            </Box>
            {sentiment.segments && sentiment.segments.length > 0 && (
              <Box sx={{ maxHeight: 200, overflow: 'auto' }}>
                {sentiment.segments.map((segment, index) => (
                  <Box key={index} sx={{ mb: 1, p: 1, bgcolor: 'background.default', borderRadius: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Chip 
                        label={segment.sentiment} 
                        color={getSentimentColor(segment.sentiment)}
                        size="small"
                      />
                      <Typography variant="caption">
                        {(segment.confidence_score * 100).toFixed(1)}%
                      </Typography>
                    </Box>
                    <Typography variant="body2" sx={{ textAlign: 'left' }}>
                      {segment.segment.substring(0, 100)}...
                    </Typography>
                  </Box>
                ))}
              </Box>
            )}
          </Box>
        ),
        loading.sentiment,
        errors.sentiment,
        'sentiment'
      )}

      {/* Object Detection */}
      {fileType === 'video' && renderSection(
        'Object Detection',
        <Visibility color="primary" />,
        objects && (
          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Detected in {objects.total_frames} frames
            </Typography>
            <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
              {objects.detections.map((detection, index) => (
                <Box key={index} sx={{ mb: 2, p: 1, bgcolor: 'background.default', borderRadius: 1 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Frame at {detection.timestamp}s
                  </Typography>
                  <Grid container spacing={1}>
                    {detection.objects.map((obj, objIndex) => (
                      <Grid item key={objIndex}>
                        <Chip
                          label={`${obj.label} (${(obj.confidence * 100).toFixed(1)}%)`}
                          size="small"
                          variant="outlined"
                        />
                      </Grid>
                    ))}
                  </Grid>
                </Box>
              ))}
            </Box>
          </Box>
        ),
        loading.objects,
        errors.objects,
        'objects'
      )}

      {/* Translation Tool */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMore />}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Translate color="primary" />
            <Typography variant="h6" sx={{ ml: 1 }}>
              Translation Tool
            </Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={2}>
            <Grid item xs={12} md={8}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Text to translate"
                value={translationText}
                onChange={(e) => setTranslationText(e.target.value)}
                sx={{ mb: 2 }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                select
                label="Target Language"
                value={targetLanguage}
                onChange={(e) => setTargetLanguage(e.target.value)}
                sx={{ mb: 2 }}
              >
                {languages.map((lang) => (
                  <MenuItem key={lang.code} value={lang.code}>
                    {lang.name}
                  </MenuItem>
                ))}
              </TextField>
              <Button
                fullWidth
                variant="contained"
                onClick={handleTranslate}
                disabled={!translationText.trim() || loading.translation}
              >
                {loading.translation ? <CircularProgress size={20} /> : 'Translate'}
              </Button>
            </Grid>
            {errors.translation && (
              <Grid item xs={12}>
                <Alert severity="error">{errors.translation}</Alert>
              </Grid>
            )}
            {translation && (
              <Grid item xs={12}>
                <Divider sx={{ my: 2 }} />
                <Typography variant="subtitle2" gutterBottom>
                  Translation Result:
                </Typography>
                <Typography variant="body1" sx={{ textAlign: 'left', p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                  {translation.translated_text}
                </Typography>
              </Grid>
            )}
          </Grid>
        </AccordionDetails>
      </Accordion>

      {/* Highlight Reel Creator */}
      {fileType === 'video' && (
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Movie color="primary" />
              <Typography variant="h6" sx={{ ml: 1 }}>
                Create Highlight Reel
              </Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Box>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Define time segments (in seconds) to include in the highlight reel:
              </Typography>
              {highlightSegments.map((segment, index) => (
                <Grid container spacing={2} key={index} sx={{ mb: 1 }}>
                  <Grid item xs={5}>
                    <TextField
                      fullWidth
                      type="number"
                      label="Start (seconds)"
                      value={segment.start}
                      onChange={(e) => {
                        const newSegments = [...highlightSegments];
                        newSegments[index].start = parseFloat(e.target.value) || 0;
                        setHighlightSegments(newSegments);
                      }}
                    />
                  </Grid>
                  <Grid item xs={5}>
                    <TextField
                      fullWidth
                      type="number"
                      label="End (seconds)"
                      value={segment.end}
                      onChange={(e) => {
                        const newSegments = [...highlightSegments];
                        newSegments[index].end = parseFloat(e.target.value) || 0;
                        setHighlightSegments(newSegments);
                      }}
                    />
                  </Grid>
                  <Grid item xs={2}>
                    <Button
                      variant="outlined"
                      color="error"
                      onClick={() => {
                        if (highlightSegments.length > 1) {
                          setHighlightSegments(highlightSegments.filter((_, i) => i !== index));
                        }
                      }}
                      disabled={highlightSegments.length === 1}
                    >
                      Remove
                    </Button>
                  </Grid>
                </Grid>
              ))}
              <Box sx={{ mt: 2 }}>
                <Button
                  variant="outlined"
                  onClick={() => setHighlightSegments([...highlightSegments, { start: 0, end: 10 }])}
                  sx={{ mr: 2 }}
                >
                  Add Segment
                </Button>
                <Button
                  variant="contained"
                  onClick={handleCreateHighlightReel}
                  disabled={loading.highlight}
                >
                  {loading.highlight ? <CircularProgress size={20} /> : 'Create Highlight Reel'}
                </Button>
              </Box>
              {errors.highlight && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {errors.highlight}
                </Alert>
              )}
              {highlightReel && (
                <Alert severity="success" sx={{ mt: 2 }}>
                  Highlight reel created successfully! Duration: {highlightReel.total_duration.toFixed(1)}s
                </Alert>
              )}
            </Box>
          </AccordionDetails>
        </Accordion>
      )}
    </Box>
  );
};

export default ResultsDisplay;