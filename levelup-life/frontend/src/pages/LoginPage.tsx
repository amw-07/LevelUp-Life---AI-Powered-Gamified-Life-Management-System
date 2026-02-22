import { useState, FormEvent } from "react";
import { useAuthStore } from "../store/authStore";
import { login, register } from "../api/auth";

export default function LoginPage() {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const setTokens = useAuthStore((s) => s.setTokens);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (mode === "login") {
        const res = await login(email, password);
        setTokens(res.access_token, res.refresh_token);
      } else {
        const res = await register(email, username, password);
        setTokens(res.access_token, res.refresh_token);
      }
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      const detail = axiosErr?.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-black text-white">⚔️ LevelUp Life</h1>
          <p className="text-purple-300 mt-2">AI-Powered Life Management System</p>
        </div>

        <div className="bg-slate-800 rounded-2xl p-8 border border-purple-500/50">
          <div className="flex rounded-xl overflow-hidden mb-6 bg-slate-700">
            <button
              className={`flex-1 py-2.5 text-sm font-semibold transition-colors ${
                mode === "login" ? "bg-purple-600 text-white" : "text-gray-400"
              }`}
              onClick={() => setMode("login")}
            >
              Login
            </button>
            <button
              className={`flex-1 py-2.5 text-sm font-semibold transition-colors ${
                mode === "register" ? "bg-purple-600 text-white" : "text-gray-400"
              }`}
              onClick={() => setMode("register")}
            >
              Register
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-gray-300 text-sm font-medium block mb-1.5">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full bg-slate-700 border border-slate-600 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 transition-colors"
                placeholder="your@email.com"
              />
            </div>

            {mode === "register" && (
              <div>
                <label className="text-gray-300 text-sm font-medium block mb-1.5">Username</label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  className="w-full bg-slate-700 border border-slate-600 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 transition-colors"
                  placeholder="hero_name"
                />
              </div>
            )}

            <div>
              <label className="text-gray-300 text-sm font-medium block mb-1.5">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full bg-slate-700 border border-slate-600 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 transition-colors"
                placeholder="••••••••"
              />
            </div>

            {error && (
              <p className="text-red-400 text-sm bg-red-900/30 px-4 py-2 rounded-lg">{error}</p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white font-bold py-3 rounded-xl transition-colors"
            >
              {loading ? "Loading…" : mode === "login" ? "Enter the Arena" : "Begin Your Journey"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
