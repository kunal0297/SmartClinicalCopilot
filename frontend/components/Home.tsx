import React from 'react';
import ColourfulText from './ColourfulText';

const ColourfulText: React.FC<{ text: string }> = ({ text }) => {
  return <div style={{ color: 'blue' }}>{text}</div>;
};

export default ColourfulText;

// Use ColourfulText component
<ColourfulText text="Hello, World!" /> 