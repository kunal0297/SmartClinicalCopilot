import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid';
import { useNavigate } from 'react-router-dom';
import ThreeDCard from '../components/ThreeDCard';
import { useTheme } from '@mui/material/styles';
import TextHoverEffect from '../components/TextHoverEffect';
import TextGenerateEffectDemo from '../components/text-generate-effect-demo';

// ColourfulText component for glowing animated text (no extra background)
function ColourfulText({ text }: { text: string }) {
  return (
    <span
      style={{
        background: 'linear-gradient(90deg, #42a5f5, #7e57c2, #26c6da, #ff4081, #42a5f5)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        filter: 'drop-shadow(0 0 8px #42a5f5) drop-shadow(0 0 16px #7e57c2)',
        fontWeight: 900,
        letterSpacing: 1,
        transition: 'filter 0.4s',
      }}
    >
      {text}
    </span>
  );
}

export default function Home() {
  const navigate = useNavigate();
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';

  // Card style for dark mode
  const cardSx = isDark
    ? {
        bgcolor: '#23272f',
        color: '#fff',
        boxShadow: '0 2px 16px 0 #111',
        border: '1px solid #333',
        transition: 'background 0.4s, color 0.4s',
      }
    : {
        bgcolor: '#f5f5f5',
        color: 'inherit',
        boxShadow: 2,
        border: 'none',
        transition: 'background 0.4s, color 0.4s',
      };

  return (
    <Box sx={{ flexGrow: 1, width: '100vw', minHeight: 'calc(100vh - 64px - 64px)', px: 0, py: 4, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
      <Typography
        variant="h3"
        component="h1"
        gutterBottom
        sx={{
          fontWeight: 'bold',
          letterSpacing: 1,
          color: isDark ? undefined : 'primary.main',
          textShadow: isDark ? undefined : '1px 2px 8px #e3f2fd',
          mb: 2,
          transition: 'color 0.4s, text-shadow 0.4s',
        }}
      >
        <TextHoverEffect text="Smart Clinical Copilot" />
      </Typography>
      <Box sx={{ mb: 4, maxWidth: 900, width: '100%' }}>
        <TextGenerateEffectDemo />
      </Box>

      <Grid container spacing={4} sx={{ width: '100%', maxWidth: 1400, mx: 'auto', justifyContent: 'center' }}>
        <Grid item xs={12} md={4} sx={{ display: 'flex', justifyContent: 'center' }}>
          <ThreeDCard sx={cardSx}>
            <Typography variant="h6" component="h2" sx={{ fontWeight: 600, color: isDark ? '#fff' : undefined }}>
              <TextHoverEffect text="Patient Management" />
            </Typography>
            <Typography variant="body2" sx={{ mb: 2, color: isDark ? 'rgba(255,255,255,0.8)' : 'text.secondary' }}>
              View and manage patient records, analyze conditions, and get real-time alerts.
            </Typography>
            <Button size="large" color="primary" variant="contained" onClick={() => navigate('/patients')} sx={{ fontWeight: 600, borderRadius: 2, boxShadow: 2 }}>
              <TextHoverEffect text="View Patients" />
            </Button>
          </ThreeDCard>
        </Grid>

        <Grid item xs={12} md={4} sx={{ display: 'flex', justifyContent: 'center' }}>
          <ThreeDCard sx={cardSx}>
            <Typography variant="h6" component="h2" sx={{ fontWeight: 600, color: isDark ? '#fff' : undefined }}>
              <TextHoverEffect text="Clinical Rules" />
            </Typography>
            <Typography variant="body2" sx={{ mb: 2, color: isDark ? 'rgba(255,255,255,0.8)' : 'text.secondary' }}>
              Browse and manage clinical rules that drive the decision support system.
            </Typography>
            <Button size="large" color="secondary" variant="contained" onClick={() => navigate('/rules')} sx={{ fontWeight: 600, borderRadius: 2, boxShadow: 2 }}>
              <TextHoverEffect text="View Rules" />
            </Button>
          </ThreeDCard>
        </Grid>

        <Grid item xs={12} md={4} sx={{ display: 'flex', justifyContent: 'center' }}>
          <ThreeDCard sx={cardSx}>
            <Typography variant="h6" component="h2" sx={{ fontWeight: 600, color: isDark ? '#fff' : undefined }}>
              <TextHoverEffect text="Cohort Analytics" />
            </Typography>
            <Typography variant="body2" sx={{ mb: 2, color: isDark ? 'rgba(255,255,255,0.8)' : 'text.secondary' }}>
              Analyze patient cohorts, view distributions, and track key metrics.
            </Typography>
            <Button size="large" color="success" variant="contained" onClick={() => navigate('/cohort-analytics')} sx={{ fontWeight: 600, borderRadius: 2, boxShadow: 2 }}>
              <TextHoverEffect text="View Analytics" />
            </Button>
          </ThreeDCard>
        </Grid>
      </Grid>
    </Box>
  );
} 