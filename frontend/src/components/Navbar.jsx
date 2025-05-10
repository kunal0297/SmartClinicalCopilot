import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Box,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  Menu as MenuIcon,
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
  Person as PersonIcon,
  Brightness4 as Brightness4Icon,
  Brightness7 as Brightness7Icon
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { usePatient } from '../context/PatientContext';

function Navbar({ mode, toggleMode }) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const navigate = useNavigate();
  const location = useLocation();
  const { currentPatient } = usePatient();
  
  const [anchorEl, setAnchorEl] = React.useState(null);
  const [mobileMenuAnchor, setMobileMenuAnchor] = React.useState(null);
  const [notifAnchor, setNotifAnchor] = React.useState(null);
  const [settingsOpen, setSettingsOpen] = React.useState(false);

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleMobileMenuOpen = (event) => {
    setMobileMenuAnchor(event.currentTarget);
  };

  const handleMobileMenuClose = () => {
    setMobileMenuAnchor(null);
  };

  const handleNavigation = (path) => {
    navigate(path);
    handleMenuClose();
    handleMobileMenuClose();
  };

  const isActive = (path) => location.pathname === path;

  const navItems = [
    { label: 'Dashboard', path: '/' },
    { label: 'Patients', path: '/patients' },
    { label: 'Alerts', path: '/alerts' },
    { label: 'Metrics', path: '/metrics' },
    { label: 'Cohort Analytics', path: '/cohort-analytics' }
  ];

  // Notifications
  const handleNotifClick = (event) => setNotifAnchor(event.currentTarget);
  const handleNotifClose = () => setNotifAnchor(null);

  // Settings
  const handleSettingsClick = () => setSettingsOpen(true);
  const handleSettingsClose = () => setSettingsOpen(false);

  return (
    <AppBar position="static">
      <Toolbar>
        {isMobile ? (
          <>
            <IconButton
              edge="start"
              color="inherit"
              aria-label="menu"
              onClick={handleMobileMenuOpen}
            >
              <MenuIcon />
            </IconButton>
            <Menu
              anchorEl={mobileMenuAnchor}
              open={Boolean(mobileMenuAnchor)}
              onClose={handleMobileMenuClose}
            >
              {navItems.map((item) => (
                <MenuItem
                  key={item.path}
                  onClick={() => handleNavigation(item.path)}
                  selected={isActive(item.path)}
                >
                  {item.label}
                </MenuItem>
              ))}
            </Menu>
          </>
        ) : (
          <Box sx={{ display: 'flex', gap: 2 }}>
            {navItems.map((item) => (
              <Button
                key={item.path}
                color="inherit"
                onClick={() => handleNavigation(item.path)}
                sx={{
                  fontWeight: isActive(item.path) ? 'bold' : 'normal',
                  borderBottom: isActive(item.path) ? '2px solid white' : 'none'
                }}
              >
                {item.label}
              </Button>
            ))}
          </Box>
        )}

        <Box sx={{ flexGrow: 1 }} />

        <IconButton color="inherit" onClick={toggleMode} sx={{ mr: 2 }}>
          {mode === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />}
        </IconButton>

        {currentPatient && (
          <Typography variant="subtitle1" sx={{ mr: 2 }}>
            Patient: {currentPatient.name}
          </Typography>
        )}

        <Box sx={{ display: 'flex', gap: 1 }}>
          <IconButton color="inherit" onClick={handleNotifClick}>
            <NotificationsIcon />
          </IconButton>
          <IconButton color="inherit" onClick={handleSettingsClick}>
            <SettingsIcon />
          </IconButton>
          <IconButton
            color="inherit"
            onClick={handleMenuOpen}
          >
            <PersonIcon />
          </IconButton>
        </Box>

        {/* Notifications Popover */}
        <Menu
          anchorEl={notifAnchor}
          open={Boolean(notifAnchor)}
          onClose={handleNotifClose}
        >
          <MenuItem>No new notifications</MenuItem>
        </Menu>

        {/* Settings Dialog */}
        <Dialog open={settingsOpen} onClose={handleSettingsClose}>
          <DialogTitle>Settings</DialogTitle>
          <DialogContent>
            <Box sx={{ my: 2 }}>
              <Button
                variant="outlined"
                onClick={toggleMode}
                startIcon={mode === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />}
              >
                Toggle {mode === 'dark' ? 'Light' : 'Dark'} Mode
              </Button>
            </Box>
            {/* Add more settings here */}
          </DialogContent>
          <DialogActions>
            <Button onClick={handleSettingsClose}>Close</Button>
          </DialogActions>
        </Dialog>

        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
        >
          <MenuItem onClick={handleMenuClose}>Profile</MenuItem>
          <MenuItem onClick={handleMenuClose}>Settings</MenuItem>
          <MenuItem onClick={handleMenuClose}>Logout</MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
}

export default Navbar; 