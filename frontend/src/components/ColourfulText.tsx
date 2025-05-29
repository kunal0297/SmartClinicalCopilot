import React from 'react';

interface ColourfulTextProps {
  text: string;
}

const ColourfulText: React.FC<ColourfulTextProps> = ({ text }) => {
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
};

export default ColourfulText; 