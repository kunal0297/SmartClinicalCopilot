import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import Grid from '@mui/material/Grid';
import ColourfulTextComponent from '../components/ColourfulText';

export default function Home() {
  return (
    <Box>
      <Container maxWidth="lg">
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Typography variant="h2" component="h1" gutterBottom>
              <ColourfulTextComponent text="Welcome to Smart Clinical Copilot" />
            </Typography>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
} 