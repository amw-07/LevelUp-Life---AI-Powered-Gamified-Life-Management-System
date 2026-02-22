import { useEffect, useState } from "react";

interface XpRollUpProps {
  xpGained: number;
  onComplete?: () => void;
}

export function XpRollUp({ xpGained, onComplete }: XpRollUpProps) {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(false);
      onComplete?.();
    }, 1200);
    return () => clearTimeout(timer);
  }, [onComplete]);

  if (!visible) return null;

  return (
    <div className="pointer-events-none fixed inset-0 flex items-center justify-center z-50">
      <div className="animate-xp-roll text-yellow-400 font-black text-4xl drop-shadow-lg select-none">
        +{xpGained} XP
      </div>
    </div>
  );
}
