import React, { useState } from 'react';
import { VehicleProvider } from './context/VehicleContext';
import { TopSurfaceBar } from './components/TopSurfaceBar';
import { HudSurface } from './components/HudSurface';
import { InfotainmentSurface } from './components/InfotainmentSurface';
import { RearSurface } from './components/RearSurface';
import { SplitCockpit } from './components/SplitCockpit';

export default function App() {
  const [activeSurface, setActiveSurface] = useState('infotainment');

  return (
    <VehicleProvider>
      <div className="w-screen h-screen bg-obsidian text-white flex flex-col overflow-hidden select-none">
        {/* Top Permanent System Navigation Bar */}
        <TopSurfaceBar activeSurface={activeSurface} setActiveSurface={setActiveSurface} />

        {/* Active Surface Screen */}
        <main className="flex-1 w-full h-[calc(100vh-3.5rem)] relative overflow-hidden">
          {activeSurface === 'hud' && <HudSurface />}
          {activeSurface === 'infotainment' && <InfotainmentSurface />}
          {activeSurface === 'rear' && <RearSurface />}
          {activeSurface === 'split' && <SplitCockpit />}
        </main>
      </div>
    </VehicleProvider>
  );
}
