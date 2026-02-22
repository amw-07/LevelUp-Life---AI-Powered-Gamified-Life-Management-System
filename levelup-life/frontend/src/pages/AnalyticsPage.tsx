import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { TrendingUp, Calendar, Award, BarChart3 } from "lucide-react";
import { ErrorBoundary } from "../components/ErrorBoundary";
import WeeklyChart from "../components/charts/WeeklyChart";
import DomainPieChart from "../components/charts/DomainPieChart";
import StreakCalendar from "../components/charts/StreakCalendar";
import {
  getSummary,
  getWeeklyReport,
  getStreaks,
  getPatterns,
} from "../api/analytics";
import { DOMAIN_TEXT_COLORS } from "../utils/gameMechanics";

export default function AnalyticsPage() {
  const { data: summary } = useQuery({
    queryKey: ["analytics-summary"],
    queryFn: getSummary,
  });

  const { data: weeklyReport } = useQuery({
    queryKey: ["analytics-weekly"],
    queryFn: () => getWeeklyReport(),
  });

  const { data: streaks } = useQuery({
    queryKey: ["analytics-streaks"],
    queryFn: getStreaks,
  });

  const { data: patterns } = useQuery({
    queryKey: ["analytics-patterns"],
    queryFn: getPatterns,
  });

  const weeklyChartData = useMemo(() => {
    if (!weeklyReport?.metrics) return [];
    const domains = ["fitness", "productivity", "learning"] as const;
    const totals = { completed: 0, xp: 0 };
    for (const d of domains) {
      const m = weeklyReport.metrics[d];
      if (m) {
        totals.completed += m.completed;
        totals.xp += m.xp;
      }
    }
    const weekStart = weeklyReport.week_start
      ? new Date(weeklyReport.week_start)
      : new Date();
    const dayNames = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
    return dayNames.map((day, i) => {
      const d = new Date(weekStart);
      d.setDate(weekStart.getDate() + i);
      const isToday = d.toDateString() === new Date().toDateString();
      return {
        day,
        completed: isToday ? totals.completed : 0,
        xp: isToday ? totals.xp : 0,
      };
    });
  }, [weeklyReport]);

  const domainChartData = useMemo(() => {
    if (!summary?.domain_distribution) return [];
    return Object.entries(summary.domain_distribution).map(([domain, value]) => ({
      domain,
      value: value as number,
      color: DOMAIN_TEXT_COLORS[domain as keyof typeof DOMAIN_TEXT_COLORS],
    }));
  }, [summary]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="max-w-7xl mx-auto px-4 py-6">
        <h1 className="text-3xl font-black text-white mb-6 flex items-center gap-3">
          <BarChart3 className="text-purple-400" size={32} />
          Analytics
        </h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Summary Section */}
          <div className="lg:col-span-2">
            <ErrorBoundary>
              <div className="bg-slate-800 rounded-xl p-6 border border-purple-500/50 mb-6">
                <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                  <TrendingUp className="text-purple-400" size={20} />
                  Performance Summary
                </h2>
                {summary ? (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <p className="text-gray-400 text-sm">This Week</p>
                      <p className="text-2xl font-bold text-white">
                        {summary.this_week.quests_completed}
                      </p>
                      <p className="text-purple-300 text-xs">
                        {summary.this_week.xp_earned} XP
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-400 text-sm">All Time</p>
                      <p className="text-2xl font-bold text-white">
                        {summary.all_time.quests_completed}
                      </p>
                      <p className="text-purple-300 text-xs">
                        {summary.all_time.xp_earned} XP
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="text-gray-400">Loading summary...</div>
                )}
              </div>
            </ErrorBoundary>

            {/* Weekly Chart */}
            <ErrorBoundary>
              <div className="bg-slate-800 rounded-xl p-6 border border-purple-500/50 mb-6">
                <h2 className="text-xl font-bold text-white mb-4">Weekly Quests</h2>
                <WeeklyChart data={weeklyChartData} />
              </div>
            </ErrorBoundary>

            {/* Streak Calendar */}
            <ErrorBoundary>
              <div className="bg-slate-800 rounded-xl p-6 border border-purple-500/50 mb-6">
                <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                  <Calendar className="text-purple-400" size={20} />
                  90-Day Activity Heatmap
                </h2>
                {streaks ? (
                  <StreakCalendar data={streaks} />
                ) : (
                  <div className="text-gray-400">Loading streak data...</div>
                )}
              </div>
            </ErrorBoundary>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Domain Distribution */}
            <ErrorBoundary>
              <div className="bg-slate-800 rounded-xl p-6 border border-purple-500/50">
                <h2 className="text-lg font-bold text-white mb-4">Domain Breakdown</h2>
                {summary?.domain_distribution &&
                Object.keys(summary.domain_distribution).length > 0 ? (
                  <DomainPieChart data={domainChartData} />
                ) : (
                  <div className="text-gray-400 text-sm text-center py-8">
                    No quest data yet
                  </div>
                )}
              </div>
            </ErrorBoundary>

            {/* Patterns */}
            <ErrorBoundary>
              <div className="bg-slate-800 rounded-xl p-6 border border-purple-500/50">
                <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <Award className="text-purple-400" size={18} />
                  Patterns
                </h2>
                {patterns ? (
                  <div className="space-y-3">
                    {patterns.best_day && (
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-400">Best Day</span>
                        <span className="text-white font-semibold">{patterns.best_day}</span>
                      </div>
                    )}
                    {patterns.top_domain && (
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-400">Top Domain</span>
                        <span
                          className={`font-semibold capitalize ${
                            DOMAIN_TEXT_COLORS[
                              patterns.top_domain as keyof typeof DOMAIN_TEXT_COLORS
                            ]
                          }`}
                        >
                          {patterns.top_domain}
                        </span>
                      </div>
                    )}
                    {patterns.completion_rate_trend !== null && (
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-400">Rate Trend</span>
                        <span
                          className={`font-semibold ${
                            patterns.completion_rate_trend >= 0 ? "text-green-400" : "text-red-400"
                          }`}
                        >
                          {patterns.completion_rate_trend >= 0 ? "+" : ""}
                          {patterns.completion_rate_trend}%
                        </span>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-gray-400 text-sm">Loading patterns...</div>
                )}
              </div>
            </ErrorBoundary>

            {/* Weekly Insights */}
            <ErrorBoundary>
              <div className="bg-gradient-to-br from-purple-700 to-pink-700 rounded-xl p-6">
                <h2 className="text-lg font-bold text-white mb-3">Weekly Insights</h2>
                {weeklyReport ? (
                  <p className="text-purple-100 text-sm leading-relaxed">
                    {weeklyReport.insights}
                  </p>
                ) : (
                  <div className="text-purple-200 text-sm">Loading insights...</div>
                )}
              </div>
            </ErrorBoundary>
          </div>
        </div>
      </div>
    </div>
  );
}
