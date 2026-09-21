import React, { useState, useRef, useEffect } from 'react';
import { useVehicle } from '../context/VehicleContext';
import { 
  Play, 
  Pause, 
  SkipBack, 
  SkipForward, 
  Volume2, 
  Gamepad2, 
  Fan, 
  Compass, 
  Disc3,
  Flame,
  Snowflake,
  Tv
} from 'lucide-react';

export function RearSurface() {
  const { state, updateState } = useVehicle();
  const [activeTab, setActiveTab] = useState('home'); // 'home', 'media', 'arcade', 'climate'
  const canvasRef = useRef(null);

  // Retro Pong Arcade Game State & Loop
  useEffect(() => {
    if (activeTab !== 'arcade') return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationId;

    let p1Y = canvas.height / 2;
    let p2Y = canvas.height / 2;
    let ballX = canvas.width / 2;
    let ballY = canvas.height / 2;
    let ballVx = 6;
    let ballVy = 4;
    let p1Score = 3;
    let p2Score = 2;

    const padH = 90;
    const padW = 16;
    const ballR = 9;

    const handleMouseMove = (e) => {
      const rect = canvas.getBoundingClientRect();
      const scaleY = canvas.height / rect.height;
      p1Y = Math.max(padH / 2, Math.min(canvas.height - padH / 2, (e.clientY - rect.top) * scaleY));
    };

    const handleTouchMove = (e) => {
      if (e.touches.length > 0) {
        const rect = canvas.getBoundingClientRect();
        const scaleY = canvas.height / rect.height;
        p1Y = Math.max(padH / 2, Math.min(canvas.height - padH / 2, (e.touches[0].clientY - rect.top) * scaleY));
      }
    };

    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('touchmove', handleTouchMove);

    const loop = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Court background & border
      ctx.fillStyle = '#080b11';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
      ctx.lineWidth = 2;
      ctx.strokeRect(16, 16, canvas.width - 32, canvas.height - 32);

      // Center dashed net
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
      ctx.lineWidth = 2;
      ctx.setLineDash([8, 8]);
      ctx.beginPath();
      ctx.moveTo(canvas.width / 2, 20);
      ctx.lineTo(canvas.width / 2, canvas.height - 20);
      ctx.stroke();
      ctx.setLineDash([]);

      // Ball Physics
      ballX += ballVx;
      ballY += ballVy;

      if (ballY - ballR < 20 || ballY + ballR > canvas.height - 20) {
        ballVy = -ballVy;
      }

      // AI P2
      if (ballY > p2Y + 10) p2Y += 4.5;
      else if (ballY < p2Y - 10) p2Y -= 4.5;
      p2Y = Math.max(padH / 2 + 20, Math.min(canvas.height - padH / 2 - 20, p2Y));

      // P1 Paddle Collision
      if (ballX - ballR <= 40 + padW && ballY >= p1Y - padH / 2 && ballY <= p1Y + padH / 2) {
        ballVx = Math.abs(ballVx) * 1.05;
        ballVy += (ballY - p1Y) * 0.1;
      }

      // P2 Paddle Collision
      if (ballX + ballR >= canvas.width - 40 - padW && ballY >= p2Y - padH / 2 && ballY <= p2Y + padH / 2) {
        ballVx = -Math.abs(ballVx) * 1.05;
        ballVy += (ballY - p2Y) * 0.1;
      }

      // Score
      if (ballX < 0) {
        p2Score++;
        ballX = canvas.width / 2;
        ballY = canvas.height / 2;
        ballVx = 6;
      } else if (ballX > canvas.width) {
        p1Score++;
        ballX = canvas.width / 2;
        ballY = canvas.height / 2;
        ballVx = -6;
      }

      // Draw P1 Paddle (Green Glow)
      ctx.fillStyle = '#00E676';
      ctx.shadowColor = '#00E676';
      ctx.shadowBlur = 12;
      ctx.beginPath();
      ctx.roundRect(40, p1Y - padH / 2, padW, padH, 8);
      ctx.fill();

      // Draw P2 Paddle (Blue Glow)
      ctx.fillStyle = '#00B0FF';
      ctx.shadowColor = '#00B0FF';
      ctx.shadowBlur = 12;
      ctx.beginPath();
      ctx.roundRect(canvas.width - 40 - padW, p2Y - padH / 2, padW, padH, 8);
      ctx.fill();

      // Draw Ball (White with green glow)
      ctx.fillStyle = '#ffffff';
      ctx.shadowColor = '#00E676';
      ctx.shadowBlur = 16;
      ctx.beginPath();
      ctx.arc(ballX, ballY, ballR, 0, Math.PI * 2);
      ctx.fill();
      ctx.shadowBlur = 0;

      // Score HUD
      ctx.font = 'bold 28px Inter, monospace';
      ctx.fillStyle = '#00E676';
      ctx.textAlign = 'right';
      ctx.fillText(`P1: ${p1Score}`, canvas.width / 2 - 30, 60);

      ctx.fillStyle = '#00B0FF';
      ctx.textAlign = 'left';
      ctx.fillText(`P2: ${p2Score}`, canvas.width / 2 + 30, 60);

      animationId = requestAnimationFrame(loop);
    };

    loop();
    return () => {
      canvas.removeEventListener('mousemove', handleMouseMove);
      canvas.removeEventListener('touchmove', handleTouchMove);
      cancelAnimationFrame(animationId);
    };
  }, [activeTab]);

  return (
    <div className="relative w-full h-[calc(100vh-3.5rem)] bg-obsidian flex flex-col items-center justify-between p-8 select-none">
      
      {/* Top Capsule Navigation Dock */}
      <nav className="flex items-center bg-black/60 p-1.5 rounded-full border border-white/10 space-x-1.5 shadow-glass z-20">
        {[
          { id: 'home', label: 'Home' },
          { id: 'media', label: 'Media' },
          { id: 'arcade', label: 'Retro Pong' },
          { id: 'climate', label: 'Rear Climate' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-5 py-2 rounded-full text-xs font-extrabold tracking-wider uppercase transition-all ${
              activeTab === tab.id
                ? 'bg-comma-green text-black shadow-glow-green scale-100'
                : 'text-neutral-400 hover:text-white hover:bg-white/5'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      {/* Tab 1: Rear Home Grid (4 Glass Cards) */}
      {activeTab === 'home' && (
        <div className="flex-1 w-full max-w-6xl grid grid-cols-2 gap-6 my-6 items-center">
          
          {/* Card 1: Now Playing */}
          <div className="glass-card rounded-3xl p-6 border border-white/10 shadow-glass-hi flex flex-col justify-between h-72">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-neutral-400">Rear Audio</span>
              <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 text-[10px] font-bold">
                SPOTIFY
              </span>
            </div>

            <div className="flex items-center space-x-4 my-2">
              <div className="w-16 h-16 rounded-2xl bg-neutral-800 flex items-center justify-center border border-white/10 shrink-0">
                <Disc3 className="w-10 h-10 text-comma-green animate-spin" style={{ animationDuration: '8s' }} />
              </div>
              <div className="min-w-0">
                <div className="text-xl font-bold text-white truncate">{state.media.title}</div>
                <div className="text-sm text-neutral-400">{state.media.artist}</div>
                <div className="text-xs text-emerald-400 font-mono mt-0.5">{state.media.quality}</div>
              </div>
            </div>

            <div className="flex items-center justify-center space-x-4">
              <button 
                onClick={() => updateState({ media: { ...state.media, progress: 0 } })}
                className="p-3 rounded-full hover:bg-white/10 text-neutral-300"
              >
                <SkipBack className="w-5 h-5" />
              </button>
              <button 
                onClick={() => updateState({ media: { ...state.media, isPlaying: !state.media.isPlaying } })}
                className="p-3.5 rounded-full bg-comma-green text-black font-bold shadow-glow-green hover:scale-105 transition-transform"
              >
                {state.media.isPlaying ? <Pause className="w-5 h-5 fill-current" /> : <Play className="w-5 h-5 fill-current" />}
              </button>
              <button 
                onClick={() => updateState({ media: { ...state.media, progress: 0 } })}
                className="p-3 rounded-full hover:bg-white/10 text-neutral-300"
              >
                <SkipForward className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Card 2: Passenger Trip Monitor */}
          <div className="glass-card rounded-3xl p-6 border border-white/10 shadow-glass-hi flex flex-col justify-between h-72">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-neutral-400">Trip Monitor</span>
              <Compass className="w-4 h-4 text-sky-400" />
            </div>

            <div>
              <div className="text-3xl font-black text-white tracking-tight">{state.navDestination}</div>
              <div className="text-sm font-semibold text-emerald-400 mt-1">{state.navDistanceMiles} mi remaining · {state.navRoute}</div>
            </div>

            <div className="w-full bg-white/10 h-2 rounded-full overflow-hidden">
              <div className="bg-sky-400 h-full rounded-full shadow-glow-blue w-3/4"></div>
            </div>

            <div className="flex items-center justify-between bg-black/40 rounded-xl px-4 py-2 text-xs font-mono text-neutral-300">
              <span>{state.navEtaMinutes} MIN REMAINING</span>
              <span>·</span>
              <span>ETA 5:42 PM</span>
            </div>
          </div>

          {/* Card 3: Rear Dual Climate Steppers */}
          <div className="glass-card rounded-3xl p-6 border border-white/10 shadow-glass-hi flex flex-col justify-between h-72">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-neutral-400">Rear Climate</span>
              <Fan className="w-4 h-4 text-comma-green" />
            </div>

            <div className="flex items-center justify-center space-x-8 my-2">
              <button 
                onClick={() => updateState({ passTemp: Math.max(60, state.passTemp - 1) })}
                className="w-14 h-14 rounded-full bg-white/10 hover:bg-white/20 text-white text-2xl font-bold flex items-center justify-center shadow-glass"
              >
                -
              </button>
              <span className="text-6xl font-black text-white font-mono">{state.passTemp}°</span>
              <button 
                onClick={() => updateState({ passTemp: Math.min(85, state.passTemp + 1) })}
                className="w-14 h-14 rounded-full bg-white/10 hover:bg-white/20 text-white text-2xl font-bold flex items-center justify-center shadow-glass"
              >
                +
              </button>
            </div>

            <div className="text-center text-xs text-neutral-400">
              Rear Comfort Auto Mode · Low Airflow
            </div>
          </div>

          {/* Card 4: Entertainment Launcher */}
          <div className="glass-card rounded-3xl p-6 border border-white/10 shadow-glass-hi flex flex-col justify-between h-72">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-neutral-400">Arcade & Media</span>
              <Gamepad2 className="w-4 h-4 text-purple-400" />
            </div>

            <button 
              onClick={() => setActiveTab('arcade')}
              className="w-full py-4 rounded-2xl bg-comma-green text-black font-black text-lg shadow-glow-green hover:scale-102 transition-transform flex items-center justify-center space-x-2"
            >
              <Gamepad2 className="w-6 h-6" />
              <span>PLAY RETRO PONG</span>
            </button>

            <button 
              onClick={() => setActiveTab('media')}
              className="w-full py-3.5 rounded-2xl bg-white/10 hover:bg-white/15 text-white font-bold text-sm transition-colors flex items-center justify-center space-x-2"
            >
              <Tv className="w-4 h-4" />
              <span>OPEN AUDIO PLAYER</span>
            </button>
          </div>

        </div>
      )}

      {/* Tab 2: Retro Pong Arcade Screen */}
      {activeTab === 'arcade' && (
        <div className="flex-1 w-full max-w-5xl my-4 relative flex flex-col items-center justify-center">
          <canvas
            ref={canvasRef}
            width={960}
            height={540}
            className="w-full h-full rounded-3xl border border-white/15 shadow-glass-hi cursor-pointer"
          />
          <div className="mt-3 text-xs text-neutral-400 font-mono">
            Touch or drag left paddle up/down to play against AI
          </div>
        </div>
      )}

      {/* Tab 3: Media Screen */}
      {activeTab === 'media' && (
        <div className="flex-1 w-full max-w-4xl glass-card rounded-3xl p-8 border border-white/10 my-6 flex flex-col justify-between">
          <div className="flex items-center space-x-6">
            <div className="w-32 h-32 rounded-3xl bg-neutral-800 border border-white/10 flex items-center justify-center shrink-0">
              <Disc3 className="w-20 h-20 text-comma-green animate-spin" style={{ animationDuration: '8s' }} />
            </div>
            <div>
              <div className="text-3xl font-extrabold text-white">{state.media.title}</div>
              <div className="text-lg text-neutral-400 mt-1">{state.media.artist}</div>
              <div className="text-xs text-emerald-400 font-mono mt-2">{state.media.quality}</div>
            </div>
          </div>

          <div className="space-y-2">
            <div className="w-full bg-white/10 h-2 rounded-full overflow-hidden">
              <div 
                className="bg-comma-green h-full rounded-full shadow-glow-green transition-all"
                style={{ width: `${(state.media.progress / state.media.duration) * 100}%` }}
              ></div>
            </div>
            <div className="flex justify-between text-xs text-neutral-400 font-mono">
              <span>1:25</span>
              <span>-2:20</span>
            </div>
          </div>

          <div className="flex items-center justify-center space-x-6">
            <button className="p-4 rounded-full hover:bg-white/10 text-neutral-300">
              <SkipBack className="w-6 h-6" />
            </button>
            <button 
              onClick={() => updateState({ media: { ...state.media, isPlaying: !state.media.isPlaying } })}
              className="p-5 rounded-full bg-comma-green text-black font-bold shadow-glow-green hover:scale-105 transition-transform"
            >
              {state.media.isPlaying ? <Pause className="w-6 h-6 fill-current" /> : <Play className="w-6 h-6 fill-current" />}
            </button>
            <button className="p-4 rounded-full hover:bg-white/10 text-neutral-300">
              <SkipForward className="w-6 h-6" />
            </button>
          </div>
        </div>
      )}

      {/* Tab 4: Rear Climate Screen */}
      {activeTab === 'climate' && (
        <div className="flex-1 w-full max-w-4xl glass-card rounded-3xl p-8 border border-white/10 my-6 flex flex-col justify-between items-center">
          <div className="text-center">
            <div className="text-xs font-bold uppercase tracking-wider text-neutral-400">Rear Passenger Climate</div>
            <div className="text-3xl font-bold text-white mt-1">Independent Dual HVAC</div>
          </div>

          <div className="flex items-center space-x-12">
            <button 
              onClick={() => updateState({ passTemp: Math.max(60, state.passTemp - 1) })}
              className="w-16 h-16 rounded-full bg-white/10 hover:bg-white/20 text-white text-3xl font-bold flex items-center justify-center shadow-glass"
            >
              -
            </button>
            <span className="text-8xl font-black text-white font-mono">{state.passTemp}°</span>
            <button 
              onClick={() => updateState({ passTemp: Math.min(85, state.passTemp + 1) })}
              className="w-16 h-16 rounded-full bg-white/10 hover:bg-white/20 text-white text-3xl font-bold flex items-center justify-center shadow-glass"
            >
              +
            </button>
          </div>

          <div className="flex space-x-3">
            {['REAR AUTO', 'LOW FAN', 'MED FAN', 'HIGH FAN'].map((mode) => (
              <button
                key={mode}
                className="px-6 py-3 rounded-2xl bg-comma-green text-black font-extrabold text-sm shadow-glow-green"
              >
                {mode}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Bottom Status Bar */}
      <div className="text-xs font-mono text-neutral-500">
        OpenCar Rear System · Tesla Model 3/Y Passenger Experience
      </div>

    </div>
  );
}
