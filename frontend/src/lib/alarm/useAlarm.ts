"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { Incident } from "@/types";

/**
 * Incidents that warrant an audible alarm in simulation mode.
 */
function isCritical(incident: Incident): boolean {
  if (incident.status !== "OPEN") return false;
  if (incident.incident_type === "BURST_SUSPECTED") return true;
  if (
    incident.incident_type === "LEAK_SUSPECTED" &&
    (incident.severity === "HIGH" || incident.severity === "CRITICAL")
  ) {
    return true;
  }
  return false;
}

/**
 * Synthesizes repeating alarm tone using Web Audio API.
 * Pattern: 2500 Hz tone for 200 ms, 100 ms silence, repeat while ALERT remains active.
 */
function startAlarmTone(audioCtx: AudioContext): () => void {
  let stopped = false;
  let timerId: any = null;

  function playPulse() {
    if (stopped) return;

    try {
      if (audioCtx.state === "suspended") {
        audioCtx.resume();
      }

      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();

      osc.type = "sine";
      osc.frequency.setValueAtTime(2500, audioCtx.currentTime); // 2500 Hz tone

      // Envelope: sharp start for 200 ms
      gain.gain.setValueAtTime(0, audioCtx.currentTime);
      gain.gain.linearRampToValueAtTime(0.3, audioCtx.currentTime + 0.02);
      gain.gain.setValueAtTime(0.3, audioCtx.currentTime + 0.18);
      gain.gain.linearRampToValueAtTime(0, audioCtx.currentTime + 0.20);

      osc.connect(gain);
      gain.connect(audioCtx.destination);

      osc.start(audioCtx.currentTime);
      osc.stop(audioCtx.currentTime + 0.20); // 200 ms tone

      // Schedule next pulse: 200 ms tone + 100 ms silence = 300 ms cycle
      timerId = setTimeout(playPulse, 300);
    } catch (err) {
      console.warn("[AUDIO] Web Audio playback warning:", err);
    }
  }

  playPulse();

  return () => {
    stopped = true;
    if (timerId) clearTimeout(timerId);
  };
}

export interface AlarmState {
  isAlarming: boolean;
  isAudioUnlocked: boolean;
  isHardwareAlertActive: boolean;
  criticalIncidents: Incident[];
  stopAlarm: () => void;
  unlockAudio: () => void;
}

/**
 * Custom hook to manage laptop Web Audio alarm for both live ESP32 hardware telemetry and simulation incidents.
 */
export function useAlarm(
  incidents: Incident[] = [],
  isHardwareLive: boolean = false,
  hardwareStatus: string = "NORMAL",
  rawValue: number = 0,
  threshold: number = 50
): AlarmState {
  const [isAlarming, setIsAlarming] = useState(false);
  const [isAudioUnlocked, setIsAudioUnlocked] = useState(false);
  const [criticalIncidents, setCriticalIncidents] = useState<Incident[]>([]);

  // User mute tracking
  const userMutedHardwareRef = useRef(false);
  const silencedIncidentIds = useRef<Set<string>>(new Set());

  const audioCtxRef = useRef<AudioContext | null>(null);
  const stopToneRef = useRef<(() => void) | null>(null);

  // Initialize & Unlock AudioContext
  const unlockAudio = useCallback(() => {
    if (!audioCtxRef.current) {
      const AudioContextClass =
        window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      audioCtxRef.current = new AudioContextClass();
    }

    if (audioCtxRef.current && audioCtxRef.current.state === "suspended") {
      audioCtxRef.current.resume().then(() => {
        setIsAudioUnlocked(true);
      });
    } else {
      setIsAudioUnlocked(true);
    }
  }, []);

  // Listen for initial user interaction to unlock audio automatically
  useEffect(() => {
    const handleFirstInteraction = () => {
      unlockAudio();
      window.removeEventListener("click", handleFirstInteraction);
      window.removeEventListener("keydown", handleFirstInteraction);
    };

    window.addEventListener("click", handleFirstInteraction);
    window.addEventListener("keydown", handleFirstInteraction);

    return () => {
      window.removeEventListener("click", handleFirstInteraction);
      window.removeEventListener("keydown", handleFirstInteraction);
    };
  }, [unlockAudio]);

  // Stop alarm callback (Mute laptop audio only — does not touch physical ESP32 buzzer)
  const stopAlarm = useCallback(() => {
    if (stopToneRef.current) {
      stopToneRef.current();
      stopToneRef.current = null;
    }

    if (isHardwareLive && hardwareStatus === "ALERT") {
      userMutedHardwareRef.current = true;
    }

    criticalIncidents.forEach((inc) => silencedIncidentIds.current.add(inc.incident_id));

    setIsAlarming(false);
  }, [isHardwareLive, hardwareStatus, criticalIncidents]);

  // Main evaluation effect
  useEffect(() => {
    const isHardwareAlert =
      isHardwareLive && hardwareStatus === "ALERT" && rawValue >= threshold;

    // Reset user mute when hardware alert ends
    if (!isHardwareAlert) {
      userMutedHardwareRef.current = false;
    }

    const unMutedHardware = isHardwareAlert && !userMutedHardwareRef.current;

    const newCriticalIncidents = incidents.filter(
      (inc) => isCritical(inc) && !silencedIncidentIds.current.has(inc.incident_id)
    );

    const shouldAlarmBeActive = unMutedHardware || newCriticalIncidents.length > 0;

    if (shouldAlarmBeActive) {
      setCriticalIncidents(newCriticalIncidents);
      setIsAlarming(true);

      // Lazy-init AudioContext if needed
      if (!audioCtxRef.current) {
        unlockAudio();
      }

      // Ensure single active oscillator loop
      if (!stopToneRef.current && audioCtxRef.current) {
        stopToneRef.current = startAlarmTone(audioCtxRef.current);
      }
    } else {
      // Stop tone when status returns to NORMAL or hardware disconnects
      if (stopToneRef.current) {
        stopToneRef.current();
        stopToneRef.current = null;
      }
      setIsAlarming(false);
      setCriticalIncidents([]);
    }
  }, [incidents, isHardwareLive, hardwareStatus, rawValue, threshold, unlockAudio]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (stopToneRef.current) {
        stopToneRef.current();
        stopToneRef.current = null;
      }
    };
  }, []);

  return {
    isAlarming,
    isAudioUnlocked,
    isHardwareAlertActive: isHardwareLive && hardwareStatus === "ALERT",
    criticalIncidents,
    stopAlarm,
    unlockAudio,
  };
}
