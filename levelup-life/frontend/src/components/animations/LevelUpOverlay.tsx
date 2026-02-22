import { useEffect, useState } from "react";
import { RANK_COLORS } from "../../utils/gameMechanics";
import type { Rank } from "../../types";

interface LevelUpOverlayProps {
  newLevel: number;
  newRank: Rank;
  rankedUp: boolean;
  onClose: () => void;
}

export function LevelUpOverlay({ newLevel, newRank, rankedUp, onClose }: LevelUpOverlayProps) {
  const [show, setShow] = useState(false);

  useEffect(() => {
    const t1 = setTimeout(() => setShow(true), 50);
    const t2 = setTimeout(() => {
      setShow(false);
      setTimeout(onClose, 400);
    }, 3500);
    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
    };
  }, [onClose]);

  return (
    <div
      className={`fixed inset-0 z-50 flex items-center justify-center bg-black/70 transition-opacity duration-400 ${
        show ? "opacity-100" : "opacity-0"
      }`}
      onClick={onClose}
    >
      <div className="animate-level-up bg-gradient-to-br from-purple-600 via-pink-600 to-yellow-500 rounded-2xl p-10 text-center shadow-2xl max-w-sm mx-4">
        <div className="text-6xl mb-4">⚡</div>
        <h2 className="text-4xl font-black text-white mb-2">LEVEL UP!</h2>
        <p className="text-2xl font-bold text-yellow-300 mb-4">Level {newLevel}</p>
        {rankedUp && (
          <div className="mt-4">
            <p className="text-white text-lg font-semibold">Rank Achieved!</p>
            <p className={`text-5xl font-black mt-1 ${RANK_COLORS[newRank]}`}>{newRank}</p>
          </div>
        )}
        <p className="text-purple-200 text-sm mt-6">Tap to continue</p>
      </div>
    </div>
  );
}
