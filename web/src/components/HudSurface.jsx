import React, { useRef, useEffect } from 'react';
import { useVehicle } from '../context/VehicleContext';
import { 
  ArrowUpRight, 
  Eye, 
  Radio, 
  Disc3, 
  Activity, 
  ShieldAlert, 
  CheckCircle2, 
  Compass,
  Volume2,
  Navigation
} from 'lucide-react';

export function HudSurface({ isSplit = false }) {
  const { state } = useVehicle();
  const canvasRef = useRef(null);

  // 3D Perspective Road Canvas Animation (Port of openpilot model_renderer.py)
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationFrameId;
    let offset = 0;

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const w = canvas.width;
      const h = canvas.height;

      const horizonY = h * 0.40;
      const vpX = w / 2;

      // Road background subtle depth gradient
      const bgGrad = ctx.createLinearGradient(0, horizonY, 0, h);
      bgGrad.addColorStop(0, 'rgba(8, 12, 18, 0.0)');
      bgGrad.addColorStop(1, 'rgba(8, 12, 18, 0.75)');
      ctx.fillStyle = bgGrad;
      ctx.fillRect(0, horizonY, w, h - horizonY);

      // Openpilot glowing corridor path (trapezoid polygon)
      const pathGrad = ctx.createLinearGradient(0, horizonY, 0, h);
      pathGrad.addColorStop(0, 'rgba(0, 230, 118, 0.0)');
      pathGrad.addColorStop(0.3, 'rgba(0, 230, 118, 0.18)');
      pathGrad.addColorStop(1, 'rgba(0, 230, 118, 0.48)');

      ctx.beginPath();
      ctx.moveTo(vpX - 24, horizonY);
      ctx.lineTo(vpX + 24, horizonY);
      ctx.lineTo(vpX + 185, h);
      ctx.lineTo(vpX - 185, h);
      ctx.closePath();
      ctx.fillStyle = pathGrad;
      ctx.fill();

      // Glowing corridor edges (mint neon)
      ctx.strokeStyle = '#00E676';
      ctx.lineWidth = 3.5;
      ctx.shadowColor = '#00E676';
      ctx.shadowBlur = 14;
      ctx.beginPath();
      ctx.moveTo(vpX - 24, horizonY);
      ctx.lineTo(vpX - 185, h);
      ctx.stroke();

      ctx.beginPath();
      ctx.moveTo(vpX + 24, horizonY);
      ctx.lineTo(vpX + 185, h);
      ctx.stroke();
      ctx.shadowBlur = 0; // reset shadow

      // Moving center dashes
      offset = (offset + (state.speed * 0.09)) % 44;
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.75)';
      ctx.lineWidth = 2.5;
      for (let y = horizonY + offset; y < h; y += 44) {
        const progress = (y - horizonY) / (h - horizonY);
        const dashLen = 10 + progress * 26;
        ctx.beginPath();
        ctx.moveTo(vpX, y);
        ctx.lineTo(vpX, y + dashLen);
        ctx.stroke();
      }

      // Outer highway lane lines
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.28)';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(vpX - 52, horizonY);
      ctx.lineTo(vpX - 360, h);
      ctx.stroke();

      ctx.beginPath();
      ctx.moveTo(vpX + 52, horizonY);
      ctx.lineTo(vpX + 360, h);
      ctx.stroke();

      // Lead Car Visualization (Model from openpilot model_renderer.py)
      const leadDist = Math.max(20, Math.min(80, state.leadCarDist));
      const leadProgress = 1 - ((leadDist - 20) / 60); // 0 at 80m, 1 at 20m
      const carY = horizonY + (h - horizonY) * (0.16 + leadProgress * 0.44);
      const carW = 46 + leadProgress * 38;
      const carH = 24 + leadProgress * 18;

      // Lead car wireframe silhouette
      ctx.fillStyle = 'rgba(16, 22, 32, 0.9)';
      ctx.strokeStyle = '#00E676';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.roundRect(vpX - carW / 2, carY - carH / 2, carW, carH, 6);
      ctx.fill();
      ctx.stroke();

      // Glowing taillights
      ctx.fillStyle = '#FF1744';
      ctx.shadowColor = '#FF1744';
      ctx.shadowBlur = 10;
      ctx.beginPath();
      ctx.arc(vpX - carW / 2 + 8, carY + carH / 2 - 6, 3.5, 0, Math.PI * 2);
      ctx.arc(vpX + carW / 2 - 8, carY + carH / 2 - 6, 3.5, 0, Math.PI * 2);
      ctx.fill();
      ctx.shadowBlur = 0;

      // Distance pill above lead vehicle
      ctx.fillStyle = '#00E676';
      ctx.beginPath();
      ctx.roundRect(vpX - 24, carY - carH / 2 - 20, 48, 16, 8);
      ctx.fill();

      ctx.fillStyle = '#06080b';
      ctx.font = 'bold 10.5px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(`${Math.round(state.leadCarDist)} m`, vpX, carY - carH / 2 - 8);

      animationFrameId = requestAnimationFrame(render);
    };

    render();
    return () => cancelAnimationFrame(animationFrameId);
  }, [state.speed, state.leadCarDist]);

  return (
    <div className="relative w-full h-[calc(100vh-3.5rem)] bg-obsidian overflow-hidden select-none flex">
      {/* 3D Road Perspective Background */}
      <canvas
        ref={canvasRef}
        width={1920}
        height={1080}
        className="absolute inset-0 w-full h-full object-cover pointer-events-none"
      />

      {/* Speedometer Triad (Comma 3X / 4 Reference Architecture) */}
      <div className={`absolute top-6 ${
        isSplit 
          ? 'right-6 flex items-center space-x-5' 
          : 'left-1/2 -translate-x-1/2 flex items-center space-x-10'
      } z-20 pointer-events-none transition-all`}>
        {/* openpilot MAX Set Speed Box */}
        <div className={`${isSplit ? 'w-20 h-24 rounded-xl' : 'w-24 h-28 rounded-2xl'} bg-black/60 backdrop-blur-md border-2 border-white/20 flex flex-col items-center justify-center shadow-glass`}>
          <span className="text-xs font-bold tracking-widest text-[#80D8A6]">MAX</span>
          <span className={`${isSplit ? 'text-2xl' : 'text-3xl'} font-extrabold text-white mt-0.5 font-mono`}>{state.setSpeed}</span>
          <span className="text-[10px] text-neutral-400 font-medium">MPH</span>
        </div>

        {/* Center Current Speedometer */}
        <div className="flex flex-col items-center justify-center">
          <div className={`${isSplit ? 'text-7xl' : 'text-9xl'} font-black text-white tracking-tighter leading-none font-mono drop-shadow-[0_20px_30px_rgba(0,0,0,0.9)]`}>
            {Math.round(state.speed)}
          </div>
          <div className="text-sm font-bold tracking-widest text-neutral-400 mt-1">MPH</div>
        </div>

        {/* US Speed Limit Shield (MUTCD 65) */}
        <div className={`${isSplit ? 'w-16 h-20' : 'w-18 h-22'} bg-white rounded-lg border-2 border-black p-1 shadow-glass flex flex-col items-center justify-between text-black`}>
          <div className="text-[8px] font-black leading-tight tracking-wider text-center">SPEED<br/>LIMIT</div>
          <div className={`${isSplit ? 'text-2xl' : 'text-3xl'} font-black font-mono leading-none`}>{state.speedLimit}</div>
          <div className="h-0.5"></div>
        </div>
      </div>

      {/* Left Glass Pod: Comma 3X & ADAS Telemetry */}
      <aside className={`${isSplit ? 'w-[330px] m-4 space-y-3' : 'w-[430px] m-6 space-y-4'} z-20 flex flex-col`}>
        {/* Comma 3X Status Card */}
        <div className={`glass-card ${isSplit ? 'rounded-2xl p-4 space-y-3' : 'rounded-3xl p-6 space-y-4'} shadow-glass-hi border border-white/10 flex flex-col`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <span className="w-3 h-3 rounded-full bg-comma-green animate-pulse shadow-glow-green"></span>
              <span className={`${isSplit ? 'text-[11px]' : 'text-xs'} font-bold tracking-wider text-comma-green uppercase`}>comma 3X · active</span>
            </div>
            <div className="flex items-center space-x-1.5 bg-white/5 px-2.5 py-1 rounded-full text-xs text-neutral-300">
              <span className="font-semibold">GAP 3</span>
              <div className="flex space-x-0.5 ml-1">
                <span className="w-1.5 h-3.5 rounded-sm bg-comma-green shadow-glow-green"></span>
                <span className="w-1.5 h-3.5 rounded-sm bg-comma-green shadow-glow-green"></span>
                <span className="w-1.5 h-3.5 rounded-sm bg-comma-green shadow-glow-green"></span>
              </div>
            </div>
          </div>

          <div className="flex items-baseline justify-between border-b border-white/10 pb-2.5">
            <div>
              <div className="text-[10px] uppercase tracking-wider text-neutral-400 font-medium">Radar Tracking</div>
              <div className={`${isSplit ? 'text-xl' : 'text-2xl'} font-bold text-white tracking-tight`}>LEAD CAR: {Math.round(state.leadCarDist)} m</div>
            </div>
            <div className="text-right">
              <div className="text-[10px] uppercase tracking-wider text-neutral-400 font-medium">Torque</div>
              <div className={`${isSplit ? 'text-base' : 'text-lg'} font-bold text-sky-400 font-mono`}>1.2 Nm</div>
            </div>
          </div>

          {/* Steering Actuator Torque Bar */}
          <div>
            <div className="flex justify-between text-[10px] text-neutral-400 mb-1">
              <span>Lateral Steering Actuator</span>
              <span className="text-emerald-400 font-medium">NOMINAL</span>
            </div>
            <div className="h-2 w-full bg-white/10 rounded-full overflow-hidden">
              <div className="h-full bg-comma-green rounded-full w-2/3 shadow-glow-green"></div>
            </div>
          </div>

          {/* Coolant and Tachometer */}
          <div className="grid grid-cols-2 gap-2 pt-0.5">
            <div className="bg-black/40 rounded-xl p-2.5 border border-white/5">
              <div className="text-[9px] text-neutral-400 uppercase tracking-wider font-semibold">Coolant</div>
              <div className={`${isSplit ? 'text-lg' : 'text-xl'} font-bold text-white font-mono mt-0.5`}>{state.coolantTemp}°F</div>
              <div className="text-[9px] text-emerald-400 font-medium">OPTIMAL</div>
            </div>
            <div className="bg-black/40 rounded-xl p-2.5 border border-white/5">
              <div className="text-[9px] text-neutral-400 uppercase tracking-wider font-semibold">Tachometer</div>
              <div className={`${isSplit ? 'text-lg' : 'text-xl'} font-bold text-white font-mono mt-0.5`}>{state.rpm.toLocaleString()}</div>
              <div className="text-[9px] text-neutral-400">RPM</div>
            </div>
          </div>

          {/* Driver Monitoring Pod (NCAP / Euro NCAP Compliance) */}
          <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-3 flex items-center justify-between shadow-glass">
            <div className="flex items-center space-x-2.5">
              <Eye className="w-4 h-4 text-comma-green" />
              <div>
                <div className="text-xs font-bold text-comma-green">DRIVER MONITOR: ATTENTIVE</div>
                <div className="text-[9px] text-neutral-400">500 kbps · 100 Hz · 0 Drops</div>
              </div>
            </div>
            <CheckCircle2 className="w-4 h-4 text-comma-green" />
          </div>
        </div>
      </aside>

      {/* Right Glass Pod: Navigation & Media (Hidden in Split Mode to eliminate occlusion & clutter) */}
      {!isSplit && (
        <aside className="w-[430px] ml-auto m-6 z-20 flex flex-col space-y-4">
        {/* Navigation Card */}
        <div className="glass-card rounded-3xl p-6 shadow-glass-hi border border-white/10 flex flex-col space-y-4">
          <div className="text-[11px] font-bold uppercase tracking-wider text-neutral-400">Navigation</div>
          
          <div className="flex items-start space-x-4">
            <div className="w-14 h-14 rounded-full bg-comma-green flex items-center justify-center text-black shadow-glow-green shrink-0">
              <ArrowUpRight className="w-8 h-8 stroke-[2.5]" />
            </div>
            <div>
              <div className="text-2xl font-bold text-white leading-tight">{state.navDestination}</div>
              <div className="text-sm font-bold text-emerald-400 mt-1">{state.navInstruction}</div>
              <div className="text-xs text-neutral-400">{state.navRoute}</div>
            </div>
          </div>

          {/* Lane Guidance */}
          <div className="flex items-center space-x-2 pt-2">
            <span className="text-[10px] text-neutral-400 uppercase font-bold mr-1">Lanes:</span>
            {['LEFT', 'THRU', 'THRU', 'EXIT'].map((lane, idx) => (
              <span
                key={idx}
                className={`px-3 py-1 rounded-lg text-[10px] font-extrabold ${
                  lane === 'EXIT' 
                    ? 'bg-comma-green text-black shadow-glow-green' 
                    : 'bg-white/10 text-neutral-400'
                }`}
              >
                {lane}
              </span>
            ))}
          </div>

          {/* ETA Pill */}
          <div className="bg-black/40 rounded-xl px-4 py-2.5 border border-white/5 flex items-center justify-between text-xs text-neutral-300 font-mono">
            <span>{state.navEtaMinutes} MIN</span>
            <span>·</span>
            <span>{state.navDistanceMiles} MI</span>
            <span>·</span>
            <span>ETA 5:42 PM</span>
          </div>
        </div>

        {/* Mini Now Playing Spotify Card */}
        <div className="glass-card rounded-3xl p-5 shadow-glass-hi border border-white/10 flex flex-col space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Disc3 className="w-5 h-5 text-comma-green animate-spin" style={{ animationDuration: '6s' }} />
              <span className="text-sm font-bold text-white truncate max-w-[200px]">{state.media.title}</span>
            </div>
            <span className="text-[10px] font-extrabold px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              SPOTIFY
            </span>
          </div>
          
          <div className="text-xs text-neutral-400 pl-8">{state.media.artist} · {state.media.quality}</div>

          {/* Audio Equalizer Visualizer */}
          <div className="flex items-center justify-between px-8 pt-2">
            {[14, 28, 42, 35, 48, 20, 36, 44, 18, 30, 40, 22].map((val, idx) => (
              <div 
                key={idx} 
                className="w-1 bg-comma-green rounded-full shadow-glow-green transition-all duration-300"
                style={{ height: `${val}px` }}
              ></div>
            ))}
          </div>
        </div>
      </aside>
      )}
    </div>
  );
}
