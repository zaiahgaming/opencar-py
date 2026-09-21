import React, { useState } from 'react';
import { useVehicle } from '../context/VehicleContext';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import L from 'leaflet';
import { 
  Lock, 
  Unlock, 
  Wind, 
  ChevronLeft, 
  ChevronRight, 
  Play, 
  Pause, 
  SkipBack, 
  SkipForward, 
  Volume2, 
  Volume1, 
  VolumeX, 
  Search, 
  Compass, 
  Layers, 
  Zap, 
  Thermometer, 
  Fan, 
  Radio, 
  Flame, 
  Snowflake, 
  ShieldCheck, 
  Bluetooth, 
  Check, 
  Trash2,
  Car,
  Music,
  Tv,
  Gamepad2,
  Camera,
  Settings,
  Phone,
  X
} from 'lucide-react';

// Custom vehicle marker icon for Leaflet
const carIcon = L.divIcon({
  className: 'custom-car-marker',
  html: `<div style="background-color: #00E676; width: 22px; height: 22px; border-radius: 50%; border: 3px solid #ffffff; box-shadow: 0 0 20px #00E676;"></div>`,
  iconSize: [22, 22],
  iconAnchor: [11, 11],
});

export function InfotainmentSurface({ isSplit = false }) {
  const { state, updateState } = useVehicle();
  const [activeModal, setActiveModal] = useState(null); // 'climate', 'apps', 'bluetooth'

  return (
    <div className="relative w-full h-[calc(100vh-3.5rem)] bg-obsidian flex flex-col justify-between overflow-hidden select-none">
      
      {/* Main Split View: Left Vehicle Pod (38%) + Right Interactive Map & Cards (62%) */}
      <div className="flex-1 flex w-full h-[calc(100%-4.5rem)] relative overflow-hidden">
        
        {/* LEFT POD: Tesla Model 3 / Y Vehicle Status & Media */}
        <div className="w-[38%] h-full bg-[#0d1017] border-r border-white/10 flex flex-col justify-between p-6 relative z-10 shadow-2xl">
          
          {/* Top Bar: Battery & Status */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="text-3xl font-black text-white font-mono">{state.speed}</span>
              <span className="text-xs text-neutral-400 font-bold tracking-wider">MPH</span>
            </div>

            <div className="flex items-center space-x-3 bg-black/40 px-3 py-1.5 rounded-full border border-white/10">
              <span className="text-sm font-bold text-white">{state.battery}%</span>
              <div className="w-12 h-3 bg-neutral-700 rounded-sm p-0.5 overflow-hidden flex items-center">
                <div 
                  className="h-full bg-comma-green rounded-xs shadow-glow-green transition-all"
                  style={{ width: `${state.battery}%` }}
                ></div>
              </div>
            </div>
          </div>

          {/* Center: 3D Vehicle Render with Interactive Hotspots */}
          <div className="relative flex-1 flex flex-col items-center justify-center my-2">
            {/* Frunk Toggle Hotspot */}
            <button
              onClick={() => updateState({ frunkOpen: !state.frunkOpen })}
              className={`absolute top-4 left-6 px-3.5 py-1.5 rounded-xl border text-xs font-bold transition-all shadow-glass ${
                state.frunkOpen 
                  ? 'bg-amber-500/20 border-amber-400 text-amber-300' 
                  : 'bg-white/5 border-white/10 text-neutral-300 hover:bg-white/10'
              }`}
            >
              {state.frunkOpen ? 'Close Frunk' : 'Open Frunk'}
            </button>

            {/* Lock Status Hotspot */}
            <button
              onClick={() => updateState({ isLocked: !state.isLocked })}
              className="absolute top-4 right-1/2 translate-x-1/2 p-2.5 rounded-full bg-black/60 border border-white/10 text-white shadow-glass hover:scale-105 transition-transform"
            >
              {state.isLocked ? <Lock className="w-4 h-4 text-emerald-400" /> : <Unlock className="w-4 h-4 text-amber-400" />}
            </button>

            {/* Trunk Toggle Hotspot */}
            <button
              onClick={() => updateState({ trunkOpen: !state.trunkOpen })}
              className={`absolute top-4 right-6 px-3.5 py-1.5 rounded-xl border text-xs font-bold transition-all shadow-glass ${
                state.trunkOpen 
                  ? 'bg-amber-500/20 border-amber-400 text-amber-300' 
                  : 'bg-white/5 border-white/10 text-neutral-300 hover:bg-white/10'
              }`}
            >
              {state.trunkOpen ? 'Close Trunk' : 'Open Trunk'}
            </button>

            {/* Authentic Clean 3D Car Render Image */}
            <div className="relative w-[340px] max-h-[220px] flex items-center justify-center my-4">
              <img 
                src="/car-models/Static-car-clean.png" 
                alt="Tesla Model 3 3D Render" 
                className="w-full object-contain filter drop-shadow-[0_20px_25px_rgba(0,0,0,0.9)]"
              />
            </div>

            {/* Tire Pressure (TPMS) 4 Corner Pills */}
            <div className="w-full grid grid-cols-2 gap-x-28 gap-y-2 mt-1 px-4">
              <div className="bg-black/50 border border-white/10 rounded-xl px-2.5 py-1.5 text-center shadow-glass">
                <div className="text-[9px] text-neutral-400 font-bold uppercase">Front Left</div>
                <div className="text-xs font-bold text-emerald-400 font-mono">{state.tpms.fl} PSI</div>
              </div>
              <div className="bg-black/50 border border-white/10 rounded-xl px-2.5 py-1.5 text-center shadow-glass">
                <div className="text-[9px] text-neutral-400 font-bold uppercase">Front Right</div>
                <div className="text-xs font-bold text-emerald-400 font-mono">{state.tpms.fr} PSI</div>
              </div>
              <div className="bg-black/50 border border-white/10 rounded-xl px-2.5 py-1.5 text-center shadow-glass">
                <div className="text-[9px] text-neutral-400 font-bold uppercase">Rear Left</div>
                <div className="text-xs font-bold text-emerald-400 font-mono">{state.tpms.rl} PSI</div>
              </div>
              <div className="bg-black/50 border border-white/10 rounded-xl px-2.5 py-1.5 text-center shadow-glass">
                <div className="text-[9px] text-neutral-400 font-bold uppercase">Rear Right</div>
                <div className="text-xs font-bold text-emerald-400 font-mono">{state.tpms.rr} PSI</div>
              </div>
            </div>
          </div>

          {/* Bottom Floating Now Playing Card */}
          <div className="glass-card rounded-2xl p-4 border border-white/10 shadow-glass flex flex-col space-y-3">
            <div className="flex items-center space-x-3.5">
              <div className="w-12 h-12 rounded-xl bg-neutral-800 overflow-hidden shadow-md flex items-center justify-center shrink-0 border border-white/10">
                <img src="/touchscreen/icons/Spotify.png" alt="Spotify" className="w-8 h-8 object-contain" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-bold text-white truncate">{state.media.title}</div>
                <div className="text-xs text-neutral-400 truncate">{state.media.artist}</div>
                <div className="text-[10px] text-emerald-400 font-mono">{state.media.quality}</div>
              </div>
            </div>

            {/* Scrubber */}
            <div className="w-full bg-white/10 h-1.5 rounded-full overflow-hidden">
              <div 
                className="bg-comma-green h-full rounded-full shadow-glow-green transition-all"
                style={{ width: `${(state.media.progress / state.media.duration) * 100}%` }}
              ></div>
            </div>

            {/* Media Buttons */}
            <div className="flex items-center justify-between pt-1">
              <div className="flex items-center space-x-2 text-neutral-400">
                <Volume2 className="w-4 h-4 text-neutral-300" />
                <span className="text-xs font-mono font-medium">{state.media.volume}%</span>
              </div>

              <div className="flex items-center space-x-3">
                <button 
                  onClick={() => updateState({ media: { ...state.media, progress: 0 } })}
                  className="p-2 rounded-full hover:bg-white/10 text-neutral-300"
                >
                  <SkipBack className="w-4 h-4" />
                </button>
                <button 
                  onClick={() => updateState({ media: { ...state.media, isPlaying: !state.media.isPlaying } })}
                  className="p-2.5 rounded-full bg-comma-green text-black font-bold shadow-glow-green hover:scale-105 transition-transform"
                >
                  {state.media.isPlaying ? <Pause className="w-4 h-4 fill-current" /> : <Play className="w-4 h-4 fill-current" />}
                </button>
                <button 
                  onClick={() => updateState({ media: { ...state.media, progress: 0 } })}
                  className="p-2 rounded-full hover:bg-white/10 text-neutral-300"
                >
                  <SkipForward className="w-4 h-4" />
                </button>
              </div>

              <button 
                onClick={() => setActiveModal(activeModal === 'bluetooth' ? null : 'bluetooth')}
                className="px-2.5 py-1 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-[11px] text-sky-400 font-medium flex items-center space-x-1"
              >
                <Bluetooth className="w-3 h-3" />
                <span>Audio</span>
              </button>
            </div>
          </div>

        </div>

        {/* RIGHT SECTION: Interactive Dark Map & Comma 4 Card Drawer */}
        <div className="w-[62%] h-full relative bg-[#090b10] overflow-hidden">
          
          {/* 100% Free OpenStreetMap Dark Tiles (ZERO API Key Watermarks!) */}
          <div className="absolute inset-0 z-0">
            <MapContainer
              center={[37.7749, -122.4194]}
              zoom={14}
              zoomControl={false}
              attributionControl={false}
              className="w-full h-full"
            >
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                maxZoom={19}
              />
              <Marker position={[37.7749, -122.4194]} icon={carIcon}>
                <Popup>Vehicle Active GPS Position</Popup>
              </Marker>
              <Polyline 
                positions={[
                  [37.7749, -122.4194],
                  [37.7800, -122.4150],
                  [37.7850, -122.4080],
                  [37.7900, -122.4000],
                ]}
                color="#00E676"
                weight={6}
                opacity={0.9}
              />
            </MapContainer>
          </div>

          {/* Top Floating Navigation Search Bar */}
          <div className={`absolute top-6 left-6 z-10 ${isSplit ? 'w-60' : 'w-96'}`}>
            <div className="glass-card rounded-2xl px-4 py-3 border border-white/10 shadow-glass flex items-center space-x-3">
              <Search className="w-5 h-5 text-neutral-400 shrink-0" />
              <input 
                type="text" 
                placeholder="Navigate to destination..." 
                defaultValue="Downtown SF - Exit 432B"
                className="bg-transparent border-none outline-none text-sm text-white placeholder-neutral-500 w-full font-medium"
              />
            </div>
          </div>

          {/* Top Right Floating Map Controls */}
          <div className="absolute top-6 right-6 z-10 flex flex-col space-y-2">
            {[
              { icon: Compass, title: 'Re-center Map' },
              { icon: Layers, title: 'Satellite Toggle' },
              { icon: Zap, title: 'Superchargers' },
            ].map((btn, idx) => {
              const Icon = btn.icon;
              return (
                <button
                  key={idx}
                  title={btn.title}
                  className="w-11 h-11 rounded-2xl glass-card border border-white/10 flex items-center justify-center text-neutral-300 hover:text-white hover:bg-white/10 shadow-glass transition-all"
                >
                  <Icon className="w-5 h-5" />
                </button>
              );
            })}
          </div>

          {/* Bottom Floating Cards Strip: COMMA 4 CARD DECK (Exact Match to User Reference Image!) */}
          <div className={`absolute bottom-6 left-4 right-4 z-10 flex items-center space-x-4 ${isSplit ? 'overflow-hidden' : 'overflow-x-auto'} pb-2 px-2`}>
            
            {/* The EXACT Card from User Image: feeling-blue-tooth-v0-cqfgtjy0xxph1.webp */}
            <div className={`${isSplit ? 'w-full max-w-[340px] p-4 rounded-[28px]' : 'w-[420px] p-6 rounded-[36px]'} bg-[#1a1c23] border border-white/10 shadow-[0_24px_48px_rgba(0,0,0,0.85)] relative flex items-center justify-between shrink-0`}>
              <div className="flex items-start space-x-3">
                <div className="flex flex-col items-center space-y-2 pt-1 text-white">
                  <Bluetooth className={`${isSplit ? 'w-6 h-6' : 'w-8 h-8'} stroke-[2.2]`} />
                  <Check className={`${isSplit ? 'w-5 h-5' : 'w-6 h-6'} text-neutral-400 stroke-[2.5]`} />
                </div>
                <div>
                  <div className={`${isSplit ? 'text-lg' : 'text-2xl'} font-bold text-white tracking-tight leading-snug`}>Bluetooth Speaker</div>
                  <div className={`${isSplit ? 'text-xs' : 'text-base'} font-medium text-neutral-300 mt-0.5`}>connected / audio</div>
                </div>
              </div>

              {/* Floating Crimson Circular Trash / Disconnect Button */}
              <button 
                title="Disconnect Device"
                className={`${isSplit ? 'w-11 h-11' : 'w-14 h-14'} rounded-full bg-[#E53935] hover:bg-[#FF1744] text-white flex items-center justify-center shadow-[0_6px_20px_rgba(229,57,53,0.6)] active:scale-95 transition-all shrink-0 ml-3`}
              >
                <Trash2 className={`${isSplit ? 'w-5 h-5' : 'w-7 h-7'} stroke-[2]`} />
              </button>
            </div>

            {/* Second Comma 4 Card: Driver Attentiveness Monitor */}
            {!isSplit && (
              <>
                <div className="w-84 bg-[#1a1c23] rounded-[36px] p-6 border border-white/10 shadow-[0_24px_48px_rgba(0,0,0,0.85)] flex items-center justify-between shrink-0">
                  <div>
                    <div className="text-xs uppercase font-bold text-comma-green tracking-wider">openpilot 0.9.7</div>
                    <div className="text-xl font-bold text-white mt-1">Driver Attentive</div>
                    <div className="text-xs text-neutral-400 mt-0.5">Model 3X · 100 Hz Loop</div>
                  </div>
                  <div className="w-12 h-12 rounded-full bg-comma-green/20 border border-comma-green/40 flex items-center justify-center text-comma-green shrink-0">
                    <Check className="w-6 h-6 stroke-[2.5]" />
                  </div>
                </div>

                {/* Third Comma 4 Card: WiFi Hotspot */}
                <div className="w-84 bg-[#1a1c23] rounded-[36px] p-6 border border-white/10 shadow-[0_24px_48px_rgba(0,0,0,0.85)] flex items-center justify-between shrink-0">
                  <div>
                    <div className="text-xs uppercase font-bold text-sky-400 tracking-wider">Tesla Connectivity</div>
                    <div className="text-xl font-bold text-white mt-1">5G Premium LTE</div>
                    <div className="text-xs text-neutral-400 mt-0.5">Lossless Audio & HD Video</div>
                  </div>
                  <div className="w-12 h-12 rounded-full bg-sky-500/20 border border-sky-400/40 flex items-center justify-center text-sky-400 shrink-0">
                    <Zap className="w-6 h-6 stroke-[2]" />
                  </div>
                </div>
              </>
            )}

          </div>

          {/* Full Screen Slide-Up Climate Drawer Modal */}
          {activeModal === 'climate' && (
            <div 
              id="climateModal"
              className="absolute inset-0 bg-[#0a0d13]/95 backdrop-blur-2xl border-t border-white/15 p-8 z-30 flex flex-col justify-between"
            >
              <div className="flex items-center justify-between border-b border-white/10 pb-4">
                <div className="flex items-center space-x-3">
                  <Fan className="w-7 h-7 text-comma-green animate-spin" style={{ animationDuration: '4s' }} />
                  <span className="text-2xl font-bold text-white tracking-tight">Dual-Zone Climate Control</span>
                </div>
                <button 
                  onClick={() => setActiveModal(null)}
                  className="p-2 rounded-full bg-white/10 hover:bg-white/20 text-white"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              {/* Dual Zone Adjustments */}
              <div className="grid grid-cols-2 gap-8 my-4">
                {/* Driver Zone */}
                <div className="bg-black/50 rounded-3xl p-6 border border-white/10 flex flex-col items-center space-y-4 shadow-glass">
                  <span className="text-xs font-bold uppercase tracking-wider text-neutral-400">Driver Climate Zone</span>
                  <div className="flex items-center space-x-6">
                    <button 
                      onClick={() => updateState({ driverTemp: Math.max(60, state.driverTemp - 1) })}
                      className="w-14 h-14 rounded-full bg-white/10 hover:bg-white/20 text-white text-2xl font-bold flex items-center justify-center shadow-glass"
                    >
                      -
                    </button>
                    <span className="text-7xl font-black text-white font-mono">{state.driverTemp}°</span>
                    <button 
                      onClick={() => updateState({ driverTemp: Math.min(85, state.driverTemp + 1) })}
                      className="w-14 h-14 rounded-full bg-white/10 hover:bg-white/20 text-white text-2xl font-bold flex items-center justify-center shadow-glass"
                    >
                      +
                    </button>
                  </div>
                  
                  {/* Airflow Direction Pills */}
                  <div className="flex space-x-2 pt-2">
                    {['WINDSHIELD', 'DASH VENTS', 'FOOTWELL'].map((vent) => (
                      <button 
                        key={vent}
                        className="px-4 py-2 rounded-xl bg-comma-green text-black text-xs font-extrabold shadow-glow-green"
                      >
                        {vent}
                      </button>
                    ))}
                  </div>

                  {/* Seat Heater Status */}
                  <div className="flex items-center space-x-2 text-xs text-neutral-400">
                    <Flame className="w-4 h-4 text-amber-400" />
                    <span>Seat Heating:</span>
                    <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 font-bold">Stage 2</span>
                  </div>
                </div>

                {/* Passenger Zone */}
                <div className="bg-black/50 rounded-3xl p-6 border border-white/10 flex flex-col items-center space-y-4 shadow-glass">
                  <span className="text-xs font-bold uppercase tracking-wider text-neutral-400">Passenger Climate Zone</span>
                  <div className="flex items-center space-x-6">
                    <button 
                      onClick={() => updateState({ passTemp: Math.max(60, state.passTemp - 1) })}
                      className="w-14 h-14 rounded-full bg-white/10 hover:bg-white/20 text-white text-2xl font-bold flex items-center justify-center shadow-glass"
                    >
                      -
                    </button>
                    <span className="text-7xl font-black text-white font-mono">{state.passTemp}°</span>
                    <button 
                      onClick={() => updateState({ passTemp: Math.min(85, state.passTemp + 1) })}
                      className="w-14 h-14 rounded-full bg-white/10 hover:bg-white/20 text-white text-2xl font-bold flex items-center justify-center shadow-glass"
                    >
                      +
                    </button>
                  </div>

                  <div className="flex space-x-2 pt-2">
                    {['DASH VENTS', 'FOOTWELL'].map((vent) => (
                      <button 
                        key={vent}
                        className="px-4 py-2 rounded-xl bg-comma-green text-black text-xs font-extrabold shadow-glow-green"
                      >
                        {vent}
                      </button>
                    ))}
                  </div>

                  <div className="flex items-center space-x-2 text-xs text-neutral-400">
                    <Flame className="w-4 h-4 text-amber-400" />
                    <span>Seat Heating:</span>
                    <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 font-bold">Stage 1</span>
                  </div>
                </div>
              </div>

              {/* Bottom Quick HVAC Modes */}
              <div className="grid grid-cols-6 gap-3">
                {['AUTO', 'A/C', 'HEAT', 'DEFROST', 'REAR DEF', 'SYNC'].map((mode) => (
                  <button
                    key={mode}
                    className="py-3.5 rounded-2xl bg-comma-green text-black font-extrabold text-sm shadow-glow-green"
                  >
                    {mode}
                  </button>
                ))}
              </div>
            </div>
          )}

        </div>

      </div>

      {/* BOTTOM OEM APP RAIL (Tesla Model 3/Y V12 Style) */}
      <footer className="h-18 w-full bg-[#080a0f] border-t border-white/10 px-6 flex items-center justify-between z-40 select-none">
        
        {/* Left: Car Controls Quick Icon */}
        <button 
          title="Vehicle Controls"
          className="p-3 rounded-2xl bg-white/5 hover:bg-white/10 text-white border border-white/10 transition-colors shadow-glass"
        >
          <Car className="w-6 h-6 text-white" />
        </button>

        {/* Left Temperature Stepper */}
        <div className="flex items-center space-x-2 bg-black/40 px-3 py-1.5 rounded-full border border-white/10">
          <button 
            onClick={() => updateState({ driverTemp: state.driverTemp - 1 })}
            className="text-neutral-400 hover:text-white px-2 py-0.5 text-lg font-bold"
          >
            ‹
          </button>
          <button 
            id="driverTempBtn"
            onClick={() => setActiveModal(activeModal === 'climate' ? null : 'climate')}
            className="text-sm font-black text-white font-mono px-1"
          >
            {state.driverTemp}°
          </button>
          <button 
            onClick={() => updateState({ driverTemp: state.driverTemp + 1 })}
            className="text-neutral-400 hover:text-white px-2 py-0.5 text-lg font-bold"
          >
            ›
          </button>
        </div>

        {/* Center: Authentic OEM Squircles */}
        <div className="flex items-center space-x-4">
          {[
            { id: 'climate', icon: Fan, label: 'Climate' },
            { id: 'music', icon: Music, label: 'Music' },
            { id: 'nav', icon: Compass, label: 'Nav' },
            { id: 'phone', icon: Phone, label: 'Phone' },
            { id: 'camera', icon: Camera, label: 'Camera' },
            { id: 'arcade', icon: Gamepad2, label: 'Arcade' },
            { id: 'settings', icon: Settings, label: 'Settings' },
          ].map((app) => {
            const Icon = app.icon;
            const isActive = activeModal === app.id;
            return (
              <button
                key={app.id}
                id={`appBtn_${app.id}`}
                onClick={() => setActiveModal(activeModal === app.id ? null : app.id)}
                className={`p-3 rounded-2xl transition-all ${
                  isActive 
                    ? 'bg-comma-green text-black scale-110 shadow-glow-green' 
                    : 'bg-white/5 hover:bg-white/10 text-neutral-300 border border-white/5'
                }`}
              >
                <Icon className="w-5 h-5" />
              </button>
            );
          })}
        </div>

        {/* Right Temperature Stepper */}
        <div className="flex items-center space-x-2 bg-black/40 px-3 py-1.5 rounded-full border border-white/10">
          <button 
            onClick={() => updateState({ passTemp: state.passTemp - 1 })}
            className="text-neutral-400 hover:text-white px-2 py-0.5 text-lg font-bold"
          >
            ‹
          </button>
          <button 
            id="passTempBtn"
            onClick={() => setActiveModal(activeModal === 'climate' ? null : 'climate')}
            className="text-sm font-black text-white font-mono px-1"
          >
            {state.passTemp}°
          </button>
          <button 
            onClick={() => updateState({ passTemp: state.passTemp + 1 })}
            className="text-neutral-400 hover:text-white px-2 py-0.5 text-lg font-bold"
          >
            ›
          </button>
        </div>

        {/* Right: Master Volume Stepper */}
        <div className="flex items-center space-x-2 bg-black/40 px-3 py-1.5 rounded-full border border-white/10">
          <button 
            onClick={() => updateState({ media: { ...state.media, volume: Math.max(0, state.media.volume - 5) } })}
            className="text-neutral-400 hover:text-white px-2 py-0.5 text-lg font-bold"
          >
            ‹
          </button>
          <Volume2 className="w-4 h-4 text-neutral-300" />
          <button 
            onClick={() => updateState({ media: { ...state.media, volume: Math.min(100, state.media.volume + 5) } })}
            className="text-neutral-400 hover:text-white px-2 py-0.5 text-lg font-bold"
          >
            ›
          </button>
        </div>

      </footer>

    </div>
  );
}
