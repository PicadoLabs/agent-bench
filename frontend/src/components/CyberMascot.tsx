import React from 'react';

export const CyberMascot: React.FC = () => {
  return (
    <div className="relative w-full max-w-md mx-auto lg:max-w-none flex items-center justify-center p-4 group select-none">
      {/* Ambient Orange Glow Behind Mascot */}
      <div className="absolute inset-0 bg-brand-orange/15 rounded-full blur-[80px] pointer-events-none group-hover:bg-brand-orange/25 transition-all duration-700" />

      {/* Outer Holographic Circuit Ring */}
      <div className="relative w-72 h-72 sm:w-80 sm:h-80 md:w-96 md:h-96 flex items-center justify-center">
        {/* Subtle Orbiting HUD Ring */}
        <div className="absolute inset-0 rounded-full border border-dashed border-border/80 group-hover:border-brand-orange/40 animate-[spin_40s_linear_infinite] transition-colors" />
        <div className="absolute inset-4 rounded-full border border-border/40" />

        {/* Sleek Cool Geometric Cyber Animal (Cheetah / Panther) SVG */}
        <svg
          viewBox="0 0 400 400"
          className="w-64 h-64 sm:w-72 sm:h-72 md:w-80 md:h-80 drop-shadow-[0_0_35px_rgba(255,90,31,0.25)] transition-transform duration-500 group-hover:scale-105"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Subtle Background Circuit Lines */}
          <path d="M 50 200 H 120 L 160 240" stroke="#252525" strokeWidth="1.5" strokeDasharray="4 4" />
          <path d="M 350 200 H 280 L 240 240" stroke="#252525" strokeWidth="1.5" strokeDasharray="4 4" />
          <path d="M 200 40 V 100" stroke="#FF5A1F" strokeWidth="1.5" strokeOpacity="0.5" />
          <path d="M 200 360 V 300" stroke="#252525" strokeWidth="1.5" />

          {/* Geometric Cyber Panther / Cheetah Head */}
          <g className="transition-all duration-300">
            {/* Outer Silhouette & Ears */}
            {/* Left Ear */}
            <polygon
              points="140,70 180,120 120,130"
              fill="#0D0D0D"
              stroke="#FF5A1F"
              strokeWidth="2"
              className="group-hover:stroke-brand-orange-hover"
            />
            <polygon points="145,85 170,120 130,125" fill="#1A1A1A" />

            {/* Right Ear */}
            <polygon
              points="260,70 220,120 280,130"
              fill="#0D0D0D"
              stroke="#FF5A1F"
              strokeWidth="2"
              className="group-hover:stroke-brand-orange-hover"
            />
            <polygon points="255,85 230,120 270,125" fill="#1A1A1A" />

            {/* Forehead & Brow Plate */}
            <polygon points="180,120 220,120 200,160" fill="#141414" stroke="#2D2D2D" strokeWidth="1.5" />
            <polygon points="180,120 200,160 150,160" fill="#0D0D0D" stroke="#252525" strokeWidth="1.5" />
            <polygon points="220,120 200,160 250,160" fill="#0D0D0D" stroke="#252525" strokeWidth="1.5" />

            {/* Temple Facets */}
            <polygon points="120,130 180,120 150,160 100,180" fill="#111111" stroke="#252525" strokeWidth="1.5" />
            <polygon points="280,130 220,120 250,160 300,180" fill="#111111" stroke="#252525" strokeWidth="1.5" />

            {/* Cheek Plates */}
            <polygon points="100,180 150,160 140,230 80,220" fill="#0A0A0A" stroke="#2D2D2D" strokeWidth="1.5" />
            <polygon points="300,180 250,160 260,230 320,220" fill="#0A0A0A" stroke="#2D2D2D" strokeWidth="1.5" />

            {/* Center Bridge & Nose */}
            <polygon points="150,160 200,160 185,240 155,220" fill="#171717" stroke="#252525" strokeWidth="1.5" />
            <polygon points="200,160 250,160 245,220 215,240" fill="#171717" stroke="#252525" strokeWidth="1.5" />
            <polygon points="185,240 215,240 200,270" fill="#FF5A1F" stroke="#FF7540" strokeWidth="1.5" />

            {/* Muzzle / Whiskers Zone */}
            <polygon points="155,220 185,240 200,270 160,290 130,260" fill="#0D0D0D" stroke="#252525" strokeWidth="1.5" />
            <polygon points="245,220 215,240 200,270 240,290 270,260" fill="#0D0D0D" stroke="#252525" strokeWidth="1.5" />

            {/* Chin / Jaw */}
            <polygon points="160,290 200,270 240,290 200,325" fill="#141414" stroke="#FF5A1F" strokeWidth="2" />

            {/* Glowing Orange Cyber Eyes */}
            {/* Left Eye */}
            <polygon
              points="145,175 180,180 160,195"
              fill="#FF5A1F"
              className="animate-pulse"
              filter="url(#glow-orange)"
            />
            {/* Right Eye */}
            <polygon
              points="255,175 220,180 240,195"
              fill="#FF5A1F"
              className="animate-pulse"
              filter="url(#glow-orange)"
            />

            {/* High-Tech Glowing Cheek Lines */}
            <line x1="90" y1="200" x2="135" y2="215" stroke="#FF5A1F" strokeWidth="2" strokeLinecap="round" />
            <line x1="85" y1="215" x2="130" y2="225" stroke="#FF5A1F" strokeWidth="1.5" strokeLinecap="round" />
            <line x1="310" y1="200" x2="265" y2="215" stroke="#FF5A1F" strokeWidth="2" strokeLinecap="round" />
            <line x1="315" y1="215" x2="270" y2="225" stroke="#FF5A1F" strokeWidth="1.5" strokeLinecap="round" />

            {/* Glowing Forehead Core Emblem */}
            <circle cx="200" cy="140" r="3.5" fill="#FF5A1F" />
            <line x1="200" y1="125" x2="200" y2="135" stroke="#FF5A1F" strokeWidth="1.5" />
          </g>

          {/* SVG Glow Filter Definition */}
          <defs>
            <filter id="glow-orange" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>
        </svg>
      </div>
    </div>
  );
};

