import React from "react";

export interface HoverEffectItem {
  title: string;
  description: string;
  link?: string;
}

export function HoverEffect({ items }: { items: HoverEffectItem[] }) {
  return (
    <div className="flex flex-wrap gap-6 justify-center w-full">
      {items.map((item, idx) => (
        <a
          key={idx}
          href={item.link || "#"}
          target={item.link ? "_blank" : undefined}
          rel="noopener noreferrer"
          className="group relative block w-80 h-56 bg-white dark:bg-neutral-900 rounded-2xl shadow-lg overflow-hidden transform transition-transform duration-300 hover:scale-105 hover:shadow-2xl"
        >
          <div className="p-6 h-full flex flex-col justify-between">
            <div>
              <h3 className="text-xl font-bold text-neutral-800 dark:text-white mb-2 group-hover:text-primary-600 transition-colors">
                {item.title}
              </h3>
              <p className="text-neutral-500 dark:text-neutral-300 text-sm">
                {item.description}
              </p>
            </div>
            {item.link && (
              <span className="mt-4 text-primary-600 dark:text-primary-400 font-semibold text-xs group-hover:underline">
                Learn more →
              </span>
            )}
          </div>
          <div className="absolute inset-0 pointer-events-none group-hover:bg-primary-50/30 transition-colors" />
        </a>
      ))}
    </div>
  );
} 