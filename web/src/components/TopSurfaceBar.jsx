import React, { useState, useEffect } from 'react';
import { useVehicle } from '../context/VehicleContext';
import { 
  Gauge, 
  Tv2, 
  Gamepad2, 
  Columns, 
  Wifi, 
  Lock, 
  Unlock, 
  ShieldCheck, 
  BatteryCharging,
  SlidersHorizontal
} from 'lucide-react';

export function TopSurfaceBar({ activeSurface, setActiveSurface }) {
  const { state, updateState } = useVehicle();
  const [timeStr, setTimeStr] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const d = new Date();
      setTimeStr(d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="h-14 w-full bg-obsidian/90 backdrop-blur-xl border-b border-white/10 px-4 flex items-center justify-between z-50 select-none">
      {/* Left: PRNDL and Lock Status */}
      <div className="flex items-center space-x-3">
        <div className="flex items-center bg-black/40 rounded-full px-3 py-1 border border-white/10 space-x-2 text-sm font-semibold tracking-wider">
          {['P', 'R', 'N', 'D'].map((g) => (
            <button
              key={g}
              onClick={() => updateState({ gear: g })}
              className={`px-2 py-0.5 rounded-full transition-all ${
                state.gear === g 
                  ? 'bg-comma-green text-black font-bold shadow-glow-green scale-105' 
                  : 'text-neutral-400 hover:text-white'
              }`}
            >
              {g}
            </button>
          ))}
        </div>

        <button 
          onClick={() => updateState({ isLocked: !state.isLocked })}
          className="p-1.5 rounded-full bg-white/5 hover:bg-white/10 text-neutral-300 transition-colors border border-white/5"
        >
          {state.isLocked ? <Lock className="w-4 h-4 text-emerald-400" /> : <Unlock className="w-4 h-4 text-amber-400" />}
        </button>

        <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-xs font-medium text-emerald-400">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>openpilot 0.9.7</span>
        </div>
      </div>

      {/* Center: Surface Switcher Capsules */}
      <nav className="flex items-center bg-black/50 p-1 rounded-full border border-white/10 space-x-1 shadow-inner">
        {[
          { id: 'hud', label: 'Cluster / HUD', icon: Gauge },
          { id: 'infotainment', label: 'Infotainment', icon: Tv2 },
          { id: 'rear', label: 'Rear Display', icon: Gamepad2 },
          { id: 'split', label: 'Split Cockpit', icon: Columns },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeSurface === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveSurface(tab.id)}
              className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all duration-200 ${
                isActive
                  ? 'bg-comma-green text-black shadow-glow-green scale-100'
                  : 'text-neutral-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Right: Driver profile, Wi-Fi, Battery, Clock */}
      <div className="flex items-center space-x-4 text-xs text-neutral-300">
        <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-white/5 border border-white/10">
          <ShieldCheck className="w-3.5 h-3.5 text-sky-400" />
          <span className="font-medium text-neutral-200">Sentry Mode</span>
        </div>

        <div className="flex items-center space-x-1.5">
          <BatteryCharging className="w-4 h-4 text-emerald-400" />
          <span className="font-bold text-white text-sm">{state.battery}%</span>
          <span className="text-neutral-500 font-mono">({state.rangeMiles} mi)</span>
        </div>

        <div className="flex items-center space-x-1 text-neutral-400">
          <Wifi className="w-3.5 h-3.5 text-neutral-300" />
        </div>

        <div className="text-sm font-semibold text-white tracking-wide font-mono">
          {timeStr || '10:55 AM'}
        </div>
      </div>
    </header>
  );
}
