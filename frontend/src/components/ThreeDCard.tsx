import React, { useRef } from 'react';
import type { ReactNode } from 'react';
import { useTheme } from '@mui/material/styles';
import Box from '@mui/material/Box';

interface ThreeDCardProps {
  children: ReactNode;
  className?: string;
  sx?: object;
}

const ThreeDCard: React.FC<ThreeDCardProps> = ({ children, className = '', sx = {} }) => {
  const cardRef = useRef<HTMLDivElement>(null);
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement, MouseEvent>) => {
    const card = cardRef.current;
    if (!card) return;
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    const rotateX = ((y - centerY) / centerY) * 10;
    const rotateY = ((x - centerX) / centerX) * -10;
    card.style.transform = `perspective(800px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.04,1.04,1.04)`;
  };

  const handleMouseLeave = () => {
    const card = cardRef.current;
    if (!card) return;
    card.style.transform = 'perspective(800px) rotateX(0deg) rotateY(0deg) scale3d(1,1,1)';
  };

  return (
    <Box
      ref={cardRef}
      className={`three-d-card ${className}`}
      sx={{
        transition: 'transform 0.3s cubic-bezier(.03,.98,.52,.99), box-shadow 0.3s',
        boxShadow: isDark
          ? '0 2px 16px 0 #111'
          : '0 8px 32px rgba(25, 118, 210, 0.12)',
        borderRadius: 4,
        background: isDark ? '#23272f' : 'rgba(255,255,255,0.95)',
        color: isDark ? '#fff' : 'inherit',
        border: isDark ? '1px solid #333' : '1px solid #e3f2fd',
        padding: 4,
        minHeight: 320,
        minWidth: 280,
        maxWidth: 420,
        margin: 'auto',
        cursor: 'pointer',
        willChange: 'transform',
        ...sx,
      }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      {children}
    </Box>
  );
};

export default ThreeDCard; 