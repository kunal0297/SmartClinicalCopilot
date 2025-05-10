"use client";
import { TextGenerateEffect } from "./ui/text-generate-effect";

const words = `The Future of Clinical Decision-Making.\nReal-time, AI-powered clinical intelligence that transforms patient care. Instantly analyze data, apply evidence-based insights, and deliver life-saving, transparent decisions — precisely when they matter most.\nDecide Smarter. Act Faster. Save Lives.`;

export default function TextGenerateEffectDemo() {
  return <TextGenerateEffect words={words} />;
} 