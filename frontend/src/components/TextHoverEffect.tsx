import React from 'react';

interface TextHoverEffectProps {
  text: string;
  className?: string;
  style?: React.CSSProperties;
}

const TextHoverEffect: React.FC<TextHoverEffectProps> = ({ text, className = '', style = {} }) => (
  <span
    className={`text-hover-effect ${className}`}
    style={{
      background: 'linear-gradient(90deg, #42a5f5, #7e57c2, #26c6da, #ff4081, #42a5f5)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
      transition: 'filter 0.3s, text-shadow 0.3s',
      cursor: 'pointer',
      ...style,
    }}
    onMouseOver={e => {
      (e.currentTarget as HTMLElement).style.filter = 'drop-shadow(0 0 8px #42a5f5) drop-shadow(0 0 16px #7e57c2)';
    }}
    onMouseOut={e => {
      (e.currentTarget as HTMLElement).style.filter = '';
    }}
  >
    {text}
  </span>
);

export default TextHoverEffect; 