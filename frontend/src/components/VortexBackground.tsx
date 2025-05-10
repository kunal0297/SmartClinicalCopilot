import React from "react";
import { Vortex } from "./ui/vortex";

const VortexBackground: React.FC = () => (
  <div
    style={{
      position: "fixed",
      inset: 0,
      zIndex: 0,
      width: "100vw",
      height: "100vh",
      overflow: "hidden",
      pointerEvents: "none",
      background: "black",
    }}
  >
    <Vortex
      backgroundColor="black"
      className="w-full h-full"
      containerClassName="w-full h-full"
    />
  </div>
);

export default VortexBackground; 