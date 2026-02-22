import { useEffect, useState } from "react";
import type { Achievement } from "../../types";

interface AchievementToastProps {
  achievement: Achievement;
  onDismiss: () => void;
}

export function AchievementToast({ achievement, onDismiss }: AchievementToastProps) {
  const [show, setShow] = useState(false);

  useEffect(() => {
    const t1 = setTimeout(() => setShow(true), 50);
    const t2 = setTimeout(() => {
      setShow(false);
      setTimeout(onDismiss, 500);
    }, 4000);
    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
    };
  }, [onDismiss]);

  return (
    <div
      className={`flex items-center gap-3 bg-slate-800 border border-yellow-500 rounded-xl p-4 shadow-2xl transition-all duration-500 ${
        show ? "translate-x-0 opacity-100" : "translate-x-full opacity-0"
      }`}
      style={{ minWidth: "280px" }}
    >
      <span className="text-3xl">{achievement.icon}</span>
      <div>
        <p className="text-yellow-400 font-bold text-sm">Achievement Unlocked!</p>
        <p className="text-white font-semibold">{achievement.name}</p>
        <p className="text-gray-400 text-xs">{achievement.description}</p>
      </div>
    </div>
  );
}

interface AchievementToastContainerProps {
  achievements: Achievement[];
  onDismiss: (id: string) => void;
}

export function AchievementToastContainer({
  achievements,
  onDismiss,
}: AchievementToastContainerProps) {
  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-3">
      {achievements.map((a) => (
        <AchievementToast key={a.id} achievement={a} onDismiss={() => onDismiss(a.id)} />
      ))}
    </div>
  );
}
