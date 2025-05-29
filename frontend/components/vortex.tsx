// Remove unused import
// import React from 'react';

// Fix ctx parameter
const resize = (ctx: CanvasRenderingContext2D) => {
  // ... resize logic
};

// Add drawVortex call in animation loop
const animate = () => {
  drawVortex();
  requestAnimationFrame(animate);
}; 