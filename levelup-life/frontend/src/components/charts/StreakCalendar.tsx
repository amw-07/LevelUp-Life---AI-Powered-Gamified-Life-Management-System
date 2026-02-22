import { useMemo } from "react";
import { StreakDataPoint } from "../../api/analytics";

interface StreakCalendarProps {
  data: StreakDataPoint[];
}

export default function StreakCalendar({ data }: StreakCalendarProps) {
  const weeks = useMemo(() => {
    const result: Array<Array<{ date: string; count: number; dayIndex: number }>> = [];
    const today = new Date();

    for (let i = 89; i >= 0; i -= 7) {
      const week: Array<{ date: string; count: number; dayIndex: number }> = [];
      for (let j = 0; j < 7; j++) {
        const dayOffset = i - j;
        if (dayOffset < 0) continue;

        const date = new Date(today);
        date.setDate(date.getDate() - dayOffset);
        const dateStr = date.toISOString().split("T")[0];

        const dayData = data.find((d) => d.date === dateStr);
        week.unshift({
          date: dateStr,
          count: dayData?.completed_count || 0,
          dayIndex: date.getDay(),
        });
      }
      result.push(week);
    }

    return result.reverse();
  }, [data]);

  const getIntensityColor = (count: number): string => {
    if (count === 0) return "bg-slate-700";
    if (count === 1) return "bg-green-900";
    if (count === 2) return "bg-green-700";
    if (count === 3) return "bg-green-500";
    return "bg-green-400";
  };

  const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  return (
    <div className="overflow-x-auto">
      <div className="flex gap-1">
        <div className="flex flex-col gap-1 text-xs text-gray-400 mr-2">
          {dayNames.map((day) => (
            <div key={day} className="h-3 flex items-center justify-end pr-1">
              {day}
            </div>
          ))}
        </div>

        <div className="flex gap-1">
          {weeks.map((week, weekIdx) => (
            <div key={weekIdx} className="flex flex-col gap-1">
              {week.map((day) => (
                <div
                  key={day.date}
                  className={`w-3 h-3 rounded-sm ${getIntensityColor(day.count)} cursor-pointer`}
                  title={`${day.date}: ${day.count} quests completed`}
                />
              ))}
            </div>
          ))}
        </div>
      </div>

      <div className="flex items-center gap-2 mt-3 text-xs text-gray-400 justify-end">
        <span>Less</span>
        <div className="w-3 h-3 rounded-sm bg-slate-700" />
        <div className="w-3 h-3 rounded-sm bg-green-900" />
        <div className="w-3 h-3 rounded-sm bg-green-700" />
        <div className="w-3 h-3 rounded-sm bg-green-500" />
        <div className="w-3 h-3 rounded-sm bg-green-400" />
        <span>More</span>
      </div>
    </div>
  );
}
