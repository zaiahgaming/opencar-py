import React from 'react';
import { HudSurface } from './HudSurface';
import { InfotainmentSurface } from './InfotainmentSurface';

export function SplitCockpit() {
  return (
    <div className="w-full h-[calc(100vh-3.5rem)] flex overflow-hidden bg-obsidian">
      {/* Left: Driver Cluster / HUD */}
      <div className="w-1/2 h-full border-r border-white/10 relative overflow-hidden">
        <HudSurface isSplit={true} />
      </div>

      {/* Right: Infotainment Center Console */}
      <div className="w-1/2 h-full relative overflow-hidden">
        <InfotainmentSurface isSplit={true} />
      </div>
    </div>
  );
}
