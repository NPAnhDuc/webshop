import React, { useState, useEffect } from 'react';

interface CuteRobotAvatarProps {
  mode?: 'customer' | 'admin';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showSpeechBubble?: boolean;
  speechText?: string;
  isWaving?: boolean;
  onClick?: () => void;
  className?: string;
}

export const CuteRobotAvatar: React.FC<CuteRobotAvatarProps> = ({
  mode = 'customer',
  size = 'md',
  showSpeechBubble = false,
  speechText,
  isWaving = true,
  onClick,
  className = ''
}) => {
  const [bubbleVisible, setBubbleVisible] = useState(showSpeechBubble);
  const [isHappy, setIsHappy] = useState(false);

  // Auto toggle bubble greeting
  useEffect(() => {
    if (showSpeechBubble) {
      setBubbleVisible(true);
      const timer = setTimeout(() => {
        // keep bubble or fade
      }, 8000);
      return () => clearTimeout(timer);
    }
  }, [showSpeechBubble]);

  const sizeDimensions = {
    sm: { width: 40, height: 44, container: 'w-10 h-11' },
    md: { width: 56, height: 62, container: 'w-14 h-16' },
    lg: { width: 80, height: 88, container: 'w-20 h-22' },
    xl: { width: 110, height: 120, container: 'w-28 h-32' }
  }[size];

  const defaultGreeting = mode === 'customer' 
    ? 'Chào bạn! Cần tớ tư vấn máy tính không? 👋' 
    : 'Chào sếp! Em đã sẵn sàng phân tích dữ liệu 📊';

  const themeColors = mode === 'customer' ? {
    antennaGlow: '#34d399',
    earPads: '#059669',
    screenBg: '#022c22',
    eyeColor: '#10b981',
    bodyAccent: '#059669',
    chestBadge: '#34d399'
  } : {
    antennaGlow: '#f59e0b',
    earPads: '#d97706',
    screenBg: '#1e1b4b',
    eyeColor: '#fbbf24',
    bodyAccent: '#4f46e5',
    chestBadge: '#fbbf24'
  };

  return (
    <div 
      className={`relative inline-block cursor-pointer select-none group ${className}`}
      onClick={() => {
        setIsHappy(true);
        setTimeout(() => setIsHappy(false), 1200);
        if (onClick) onClick();
      }}
      onMouseEnter={() => setBubbleVisible(true)}
    >
      {/* Interactive Speech Bubble */}
      {bubbleVisible && (
        <div className="absolute -top-12 right-0 sm:-right-4 z-30 whitespace-nowrap bg-white text-slate-800 text-xs font-semibold px-3 py-1.5 rounded-2xl shadow-xl border border-slate-200 animate-in fade-in zoom-in-90 duration-200 pointer-events-none flex items-center space-x-1.5">
          <span>{speechText || defaultGreeting}</span>
          {/* Bubble tail */}
          <div className="absolute -bottom-1.5 right-6 w-3 h-3 bg-white border-b border-r border-slate-200 transform rotate-45" />
        </div>
      )}

      {/* Robot SVG Graphics */}
      <div className={`relative ${sizeDimensions.container} ${isHappy ? 'animate-bounce' : 'animate-robot-float'} transition-transform duration-300 group-hover:scale-105`}>
        <svg
          viewBox="0 0 100 110"
          width="100%"
          height="100%"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="overflow-visible filter drop-shadow-md"
        >
          {/* 1. Antenna */}
          <g>
            {/* Stalk */}
            <line x1="50" y1="20" x2="50" y2="9" stroke="#94a3b8" strokeWidth="3.5" strokeLinecap="round" />
            {/* Antenna Orb with pulse glow */}
            <circle
              cx="50"
              cy="8"
              r="6.5"
              fill={themeColors.antennaGlow}
              className="animate-robot-glow"
            />
            <circle cx="48" cy="6" r="2" fill="#ffffff" opacity="0.8" />
          </g>

          {/* 2. Side Ear Pads / Headphones */}
          <rect x="14" y="32" width="6" height="18" rx="3" fill={themeColors.earPads} />
          <rect x="80" y="32" width="6" height="18" rx="3" fill={themeColors.earPads} />

          {/* 3. Robot Head Chassis */}
          <rect
            x="18"
            y="18"
            width="64"
            height="46"
            rx="16"
            fill="#ffffff"
            stroke="#cbd5e1"
            strokeWidth="3"
          />

          {/* 4. Glossy Visor / Screen */}
          <rect
            x="24"
            y="24"
            width="52"
            height="34"
            rx="11"
            fill={themeColors.screenBg}
          />
          {/* Glass reflection streak */}
          <path
            d="M26 28 C 36 26, 64 26, 74 28"
            stroke="#ffffff"
            strokeWidth="1.5"
            strokeLinecap="round"
            opacity="0.3"
          />

          {/* 5. Expressive Cute Eyes */}
          <g className={isHappy ? '' : 'animate-robot-blink'}>
            {isHappy ? (
              // Happy Arc Eyes (^ ^)
              <>
                <path d="M33 40 Q 38 33 43 40" stroke={themeColors.eyeColor} strokeWidth="3.5" strokeLinecap="round" />
                <path d="M57 40 Q 62 33 67 40" stroke={themeColors.eyeColor} strokeWidth="3.5" strokeLinecap="round" />
              </>
            ) : (
              // Round Glowing LED Eyes
              <>
                <circle cx="38" cy="38" r="5" fill={themeColors.eyeColor} />
                <circle cx="36" cy="36" r="1.8" fill="#ffffff" />
                <circle cx="62" cy="38" r="5" fill={themeColors.eyeColor} />
                <circle cx="60" cy="36" r="1.8" fill="#ffffff" />
              </>
            )}
          </g>

          {/* 6. Cute Blushing Cheeks */}
          <ellipse cx="31" cy="48" rx="3.5" ry="2" fill="#f472b6" opacity="0.8" />
          <ellipse cx="69" cy="48" rx="3.5" ry="2" fill="#f472b6" opacity="0.8" />

          {/* 7. Cute Smile Mouth */}
          <path
            d={isHappy ? "M45 46 Q 50 51 55 46" : "M46 47 Q 50 50 54 47"}
            stroke={themeColors.eyeColor}
            strokeWidth="2"
            strokeLinecap="round"
            fill="none"
          />

          {/* Admin Mode Specialty: Smart Visor / Data Glasses */}
          {mode === 'admin' && (
            <g opacity="0.85">
              <rect x="29" y="32" width="18" height="13" rx="3" stroke="#fbbf24" strokeWidth="1.5" fill="none" />
              <rect x="53" y="32" width="18" height="13" rx="3" stroke="#fbbf24" strokeWidth="1.5" fill="none" />
              <line x1="47" y1="38" x2="53" y2="38" stroke="#fbbf24" strokeWidth="1.5" />
            </g>
          )}

          {/* 8. Neck Joint */}
          <rect x="44" y="64" width="12" height="4" rx="2" fill="#94a3b8" />

          {/* 9. Robot Body Chassis */}
          <path
            d="M28 68 C28 68, 30 96, 32 98 C33 99, 67 99, 68 98 C70 96, 72 68, 72 68 Z"
            fill="#ffffff"
            stroke="#cbd5e1"
            strokeWidth="3"
          />

          {/* Chest Core Badge */}
          <rect x="42" y="74" width="16" height="14" rx="4" fill={themeColors.bodyAccent} />
          {mode === 'customer' ? (
            // Heart or shopping bolt
            <path d="M47 80 L51 76 L51 81 L55 79 L49 85 L50 81 Z" fill="#ffffff" />
          ) : (
            // Mini Analytics Chart Bars
            <g fill="#fbbf24">
              <rect x="45" y="82" width="2" height="4" rx="0.5" />
              <rect x="49" y="79" width="2" height="7" rx="0.5" />
              <rect x="53" y="77" width="2" height="9" rx="0.5" />
            </g>
          )}

          {/* 10. Left Arm (Idle on hip) */}
          <path
            d="M28 72 C22 75, 20 84, 25 88"
            stroke="#94a3b8"
            strokeWidth="4"
            strokeLinecap="round"
            fill="none"
          />
          <circle cx="26" cy="88" r="3.5" fill="#ffffff" stroke="#cbd5e1" strokeWidth="2" />

          {/* 11. Right Waving Arm (Active Cute Wave Animation) */}
          <g className={isWaving ? 'animate-robot-wave' : ''}>
            <path
              d="M72 72 C78 68, 86 64, 88 56"
              stroke="#94a3b8"
              strokeWidth="4"
              strokeLinecap="round"
              fill="none"
            />
            {/* Waving Mitten Hand with fingers */}
            <circle cx="89" cy="54" r="5.5" fill="#ffffff" stroke="#cbd5e1" strokeWidth="2" />
            {/* Motion Wave Lines */}
            {isWaving && (
              <g stroke={themeColors.antennaGlow} strokeWidth="1.5" strokeLinecap="round" opacity="0.8">
                <path d="M96 48 C98 52, 98 56, 96 60" />
                <path d="M99 46 C102 52, 102 58, 99 62" />
              </g>
            )}
          </g>

          {/* 12. Feet / Base */}
          <rect x="36" y="99" width="10" height="5" rx="2.5" fill="#94a3b8" />
          <rect x="54" y="99" width="10" height="5" rx="2.5" fill="#94a3b8" />
        </svg>
      </div>
    </div>
  );
};
