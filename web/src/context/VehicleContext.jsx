import React, { createContext, useContext, useState, useEffect } from 'react';

const VehicleContext = createContext();

export function VehicleProvider({ children }) {
  const [state, setState] = useState({
    speed: 65,
    setSpeed: 65,
    isCruiseSet: true,
    isOpenpilotEngaged: true,
    gear: 'D',
    battery: 69,
    rangeMiles: 284,
    powerKw: 18.5,
    rpm: 2400,
    coolantTemp: 192,
    leadCarDist: 42,
    leadCarSpeed: 64,
    followGap: 3,
    steeringTorque: 0.12,
    driverAttentive: true,
    leftTurnSignal: false,
    rightTurnSignal: false,
    headlights: true,
    highBeams: false,
    speedLimit: 65,
    isLocked: true,
    frunkOpen: false,
    trunkOpen: false,
    sentryActive: true,
    tpms: { fl: 35, fr: 35, rl: 34, rr: 35 },
    driverTemp: 72,
    passTemp: 70,
    fanSpeed: 3,
    seatHeaterDriver: 2, // 0, 1, 2, 3
    seatHeaterPass: 1,
    acOn: true,
    recircOn: true,
    hepaOn: true,
    defrostFront: false,
    defrostRear: false,
    airflow: { windshield: true, dash: true, floor: false },
    navInstruction: 'In 800 ft, Exit 432B',
    navDestination: 'Downtown SF',
    navRoute: 'US-101 North',
    navEtaMinutes: 14,
    navDistanceMiles: 12.4,
    canBus: { bitrate: '500 kbps', rateHz: 100, dropCount: 0, connected: true },
    media: {
      title: 'Los Angeles',
      artist: 'The Midnight',
      album: 'Endless Summer',
      source: 'Spotify',
      duration: 220,
      progress: 85,
      isPlaying: true,
      volume: 75,
      quality: 'FLAC 96kHz Lossless',
    }
  });

  // Connect to live Python CAN Bus WebSocket if available
  useEffect(() => {
    let ws;
    try {
      ws = new WebSocket(`ws://${window.location.hostname}:8765`);
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setState(prev => ({ ...prev, ...data }));
        } catch (e) {
          // ignore parsing error
        }
      };
      ws.onopen = () => console.log('Connected to OpenCar CAN Bus Bridge');
      ws.onerror = () => ws.close();
    } catch (err) {
      // Offline / standalone mode
    }

    // Realistic idle/drive physics simulation when running standalone
    const interval = setInterval(() => {
      setState(prev => {
        if (!prev.isOpenpilotEngaged) return prev;
        const delta = (Math.random() - 0.5) * 0.4;
        const newSpeed = Math.round((prev.speed + delta) * 10) / 10;
        const newDist = Math.max(20, Math.min(80, Math.round((prev.leadCarDist + (Math.random() - 0.5) * 0.8) * 10) / 10));
        const newProgress = prev.media.isPlaying ? (prev.media.progress + 1) % prev.media.duration : prev.media.progress;
        return {
          ...prev,
          speed: newSpeed,
          leadCarDist: newDist,
          rpm: Math.round(2300 + newSpeed * 2),
          media: {
            ...prev.media,
            progress: newProgress
          }
        };
      });
    }, 1000);

    return () => {
      if (ws) ws.close();
      clearInterval(interval);
    };
  }, []);

  const updateState = (updates) => {
    setState(prev => ({ ...prev, ...updates }));
  };

  return (
    <VehicleContext.Provider value={{ state, updateState }}>
      {children}
    </VehicleContext.Provider>
  );
}

export const useVehicle = () => useContext(VehicleContext);
