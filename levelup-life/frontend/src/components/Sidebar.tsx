import { useLocation, useNavigate } from "react-router-dom";
import { Home, BarChart3, User, LogOut } from "lucide-react";
import { useAuthStore } from "../store/authStore";

interface NavItem {
  path: string;
  icon: React.ElementType;
  label: string;
}

const navItems: NavItem[] = [
  { path: "/", icon: Home, label: "Dashboard" },
  { path: "/analytics", icon: BarChart3, label: "Analytics" },
  { path: "/profile", icon: User, label: "Profile" },
];

export default function Sidebar() {
  const location = useLocation();
  const navigate = useNavigate();
  const clearTokens = useAuthStore((s) => s.clearTokens);

  const handleLogout = () => {
    clearTokens();
    navigate("/login");
  };

  return (
    <aside className="w-64 bg-slate-800 border-r border-slate-700 min-h-screen flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-slate-700">
        <div className="flex items-center gap-2">
          <span className="text-2xl">⚔️</span>
          <h1 className="text-xl font-black text-white">LevelUp Life</h1>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <li key={item.path}>
                <button
                  onClick={() => navigate(item.path)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                    isActive
                      ? "bg-purple-600 text-white shadow-lg shadow-purple-500/30"
                      : "text-gray-400 hover:bg-slate-700 hover:text-white"
                  }`}
                >
                  <Icon size={20} />
                  <span className="font-medium">{item.label}</span>
                  {isActive && (
                    <div className="ml-auto w-1.5 h-1.5 bg-white rounded-full" />
                  )}
                </button>
              </li>
            );
          })}
        </ul>

        {/* Domain Quick Access */}
        <div className="mt-8 pt-6 border-t border-slate-700">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3 px-4">
            Quick Access
          </p>
          <ul className="space-y-1">
            {["fitness", "productivity", "learning"].map((domain) => (
              <li key={domain}>
                <button
                  onClick={() => navigate("/")}
                  className="w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-gray-400 hover:bg-slate-700 hover:text-white transition-all duration-200"
                >
                  <div
                    className={`w-2 h-2 rounded-full ${
                      domain === "fitness"
                        ? "bg-red-500"
                        : domain === "productivity"
                          ? "bg-blue-500"
                          : "bg-purple-500"
                    }`}
                  />
                  <span className="text-sm capitalize">{domain}</span>
                </button>
              </li>
            ))}
          </ul>
        </div>
      </nav>

      {/* Logout */}
      <div className="p-4 border-t border-slate-700">
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-gray-400 hover:bg-red-900/30 hover:text-red-400 transition-all duration-200"
        >
          <LogOut size={20} />
          <span className="font-medium">Logout</span>
        </button>
      </div>
    </aside>
  );
}
