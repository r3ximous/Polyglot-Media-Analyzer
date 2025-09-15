import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Grid,
  MenuItem,
  Card,
  CardContent,
  Typography,
  Chip,
  Alert,
  CircularProgress,
  InputAdornment
} from '@mui/material';
import { Search as SearchIcon } from '@mui/icons-material';
import { searchContent } from '../services/api';

const SearchInterface = () => {
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState({
    file_type: '',
    language: '',
    sentiment: ''
  });
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fileTypes = [
    { value: '', label: 'All Types' },
    { value: 'video', label: 'Video' },
    { value: 'audio', label: 'Audio' }
  ];

  const languages = [
    { value: '', label: 'All Languages' },
    { value: 'en', label: 'English' },
    { value: 'es', label: 'Spanish' },
    { value: 'fr', label: 'French' },
    { value: 'de', label: 'German' },
    { value: 'it', label: 'Italian' },
    { value: 'pt', label: 'Portuguese' },
    { value: 'ru', label: 'Russian' },
    { value: 'ja', label: 'Japanese' },
    { value: 'ko', label: 'Korean' },
    { value: 'zh', label: 'Chinese' }
  ];

  const sentiments = [
    { value: '', label: 'All Sentiments' },
    { value: 'positive', label: 'Positive' },
    { value: 'negative', label: 'Negative' },
    { value: 'neutral', label: 'Neutral' }
  ];

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const cleanFilters = Object.fromEntries(
        Object.entries(filters).filter(([_, value]) => value !== '')
      );
      
      const searchResults = await searchContent(query, cleanFilters, 20);
      setResults(searchResults);
    } catch (err) {
      setError(err.response?.data?.detail || 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  const highlightText = (text, highlights) => {
    if (!highlights || highlights.length === 0) return text;
    
    // Simple highlighting - in a real app, you'd parse the ElasticSearch highlight response
    const queryWords = query.toLowerCase().split(' ');
    let highlightedText = text;
    
    queryWords.forEach(word => {
      if (word.length > 2) {
        const regex = new RegExp(`(${word})`, 'gi');
        highlightedText = highlightedText.replace(regex, '<mark>$1</mark>');
      }
    });
    
    return <span dangerouslySetInnerHTML={{ __html: highlightedText }} />;
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive':
        return 'success';
      case 'negative':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Search Media Content
      </Typography>

      <Box component="form" onSubmit={handleSearch} sx={{ mb: 4 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Search query"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search transcriptions, summaries, objects..."
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <TextField
              fullWidth
              select
              label="File Type"
              value={filters.file_type}
              onChange={(e) => setFilters({ ...filters, file_type: e.target.value })}
            >
              {fileTypes.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={12} md={2}>
            <TextField
              fullWidth
              select
              label="Language"
              value={filters.language}
              onChange={(e) => setFilters({ ...filters, language: e.target.value })}
            >
              {languages.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={12} md={2}>
            <TextField
              fullWidth
              select
              label="Sentiment"
              value={filters.sentiment}
              onChange={(e) => setFilters({ ...filters, sentiment: e.target.value })}
            >
              {sentiments.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={12}>
            <Button
              type="submit"
              variant="contained"
              size="large"
              disabled={!query.trim() || loading}
              fullWidth
            >
              {loading ? <CircularProgress size={24} /> : 'Search'}
            </Button>
          </Grid>
        </Grid>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {results && (
        <Box>
          <Typography variant="h6" gutterBottom>
            Search Results ({results.total} found)
          </Typography>
          
          {results.results.length === 0 ? (
            <Alert severity="info">
              No results found for your search query.
            </Alert>
          ) : (
            <Grid container spacing={2}>
              {results.results.map((result, index) => (
                <Grid item xs={12} key={index}>
                  <Card>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                        <Typography variant="h6" color="primary">
                          {result.source.filename}
                        </Typography>
                        <Chip
                          label={`Score: ${result.score.toFixed(2)}`}
                          size="small"
                          color="secondary"
                        />
                      </Box>

                      <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                        <Chip
                          label={result.source.file_type}
                          size="small"
                          variant="outlined"
                        />
                        {result.source.language && (
                          <Chip
                            label={result.source.language}
                            size="small"
                            variant="outlined"
                          />
                        )}
                        {result.source.sentiment && (
                          <Chip
                            label={result.source.sentiment}
                            size="small"
                            color={getSentimentColor(result.source.sentiment)}
                          />
                        )}
                        {result.source.duration && (
                          <Chip
                            label={`${result.source.duration.toFixed(1)}s`}
                            size="small"
                            variant="outlined"
                          />
                        )}
                      </Box>

                      {result.highlights.transcription_text && (
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            Transcription:
                          </Typography>
                          <Typography variant="body2" sx={{ fontStyle: 'italic' }}>
                            {highlightText(
                              result.highlights.transcription_text[0] || result.source.transcription_text?.substring(0, 200) + '...',
                              result.highlights.transcription_text
                            )}
                          </Typography>
                        </Box>
                      )}

                      {result.highlights.summary_text && (
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            Summary:
                          </Typography>
                          <Typography variant="body2" sx={{ fontStyle: 'italic' }}>
                            {highlightText(
                              result.highlights.summary_text[0] || result.source.summary_text?.substring(0, 200) + '...',
                              result.highlights.summary_text
                            )}
                          </Typography>
                        </Box>
                      )}

                      {result.source.objects_detected && result.source.objects_detected.length > 0 && (
                        <Box>
                          <Typography variant="subtitle2" gutterBottom>
                            Detected Objects:
                          </Typography>
                          <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                            {result.source.objects_detected.slice(0, 10).map((obj, objIndex) => (
                              <Chip
                                key={objIndex}
                                label={obj}
                                size="small"
                                variant="outlined"
                                color="info"
                              />
                            ))}
                            {result.source.objects_detected.length > 10 && (
                              <Chip
                                label={`+${result.source.objects_detected.length - 10} more`}
                                size="small"
                                variant="outlined"
                              />
                            )}
                          </Box>
                        </Box>
                      )}

                      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 2 }}>
                        File ID: {result.file_id} | Created: {result.source.created_at ? new Date(result.source.created_at).toLocaleDateString() : 'N/A'}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </Box>
      )}
    </Box>
  );
};

export default SearchInterface;