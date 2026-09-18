"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { Incident } from "@/types";

/**
 * Incidents that warrant an audible alarm.
 * BURST_EVENT is always critical.
 * LEAK_SUSPECTED only when severity is HIGH or CRITICAL.
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
 * Wailing police-siren using Web Audio API.
 *
 * Two oscillators sweep 480 Hz → 960 Hz → 480 Hz continuously
 * (fundamental + a harmonic fifth for richness).
 * One full wail cycle = 0.9 s up + 0.9 s down = 1.8 s.
 * Returns a cleanup function.
 */
function startAlarmTone(audioCtx: AudioContext): () => void {
  let stopped = false;
  const oscillators: OscillatorNode[] = [];
  const LOW  = 480;
  const HIGH = 960;
  const HALF = 0.9; // seconds for half-sweep (up or down)

  // Master gain (controls overall volume)
  const masterGain = audioCtx.createGain();
  masterGain.gain.setValueAtTime(0.35, audioCtx.currentTime);
  masterGain.connect(audioCtx.destination);

  // Fundamental oscillator
  const osc1 = audioCtx.createOscillator();
  osc1.type = "sawtooth"; // richer, more siren-like than sine
  osc1.frequency.setValueAtTime(LOW, audioCtx.currentTime);

  // Harmonic fifth (+7 semitones ≈ ×1.498) for a full, layered sound
  const osc2 = audioCtx.createOscillator();
  osc2.type = "sine";
  osc2.frequency.setValueAtTime(LOW * 1.5, audioCtx.currentTime);

  // Blend: osc1 at 70 %, osc2 at 30 %
  const g1 = audioCtx.createGain(); g1.gain.value = 0.7;
  const g2 = audioCtx.createGain(); g2.gain.value = 0.3;

  osc1.connect(g1); g1.connect(masterGain);
  osc2.connect(g2); g2.connect(masterGain);

  osc1.start();
  osc2.start();
  oscillators.push(osc1, osc2);

  // Schedule infinite sweep cycles
  function scheduleSweeps(startTime: number) {
    if (stopped) return;

    // UP sweep: LOW → HIGH over HALF seconds
    osc1.frequency.exponentialRampToValueAtTime(HIGH,        startTime + HALF);
    osc2.frequency.exponentialRampToValueAtTime(HIGH * 1.5,  startTime + HALF);

    // DOWN sweep: HIGH → LOW over next HALF seconds
    osc1.frequency.exponentialRampToValueAtTime(LOW,         startTime + HALF * 2);
    osc2.frequency.exponentialRampToValueAtTime(LOW  * 1.5,  startTime + HALF * 2);

    // Queue the next pair of sweeps just before the current one ends
    setTimeout(() => scheduleSweeps(audioCtx.currentTime), (HALF * 2 - 0.05) * 1000);
  }

  scheduleSweeps(audioCtx.currentTime);

  return () => {
    stopped = true;
    oscillators.forEach((o) => {
      try { o.stop(); } catch { /* already stopped */ }
    });
    try { masterGain.disconnect(); } catch { /* ignore */ }
  };
}

export interface AlarmState {
  isAlarming: boolean;
  criticalIncidents: Incident[];
  stopAlarm: () => void;
}

/**
 * Watches the incident list and fires an alarm whenever a NEW critical
 * incident appears that was not previously seen.
 * Alarm is silenced by calling stopAlarm().
 * The alarm does NOT auto-restart for an incident that was already silenced.
 */
export function useAlarm(incidents: Incident[]): AlarmState {
  const [isAlarming, setIsAlarming] = useState(false);
  const [criticalIncidents, setCriticalIncidents] = useState<Incident[]>([]);

  // IDs of incidents we've already alarmed for (or that were silenced)
  const seenIds = useRef<Set<string>>(new Set());
  // IDs the user explicitly stopped the alarm for
  const silencedIds = useRef<Set<string>>(new Set());

  const audioCtxRef = useRef<AudioContext | null>(null);
  const stopToneRef = useRef<(() => void) | null>(null);

  const stopAlarm = useCallback(() => {
    if (stopToneRef.current) {
      stopToneRef.current();
      stopToneRef.current = null;
    }
    // Mark all currently critical incidents as silenced
    criticalIncidents.forEach((inc) => silencedIds.current.add(inc.incident_id));
    setIsAlarming(false);
    setCriticalIncidents([]);
  }, [criticalIncidents]);

  useEffect(() => {
    const newCritical = incidents.filter(
      (inc) =>
        isCritical(inc) &&
        !silencedIds.current.has(inc.incident_id)
    );

    // Detect truly new (not-yet-alarmed) critical incidents
    const brandNew = newCritical.filter(
      (inc) => !seenIds.current.has(inc.incident_id)
    );

    // Track all critical we've evaluated so we don't re-trigger
    newCritical.forEach((inc) => seenIds.current.add(inc.incident_id));

    if (brandNew.length > 0) {
      // Start the alarm
      setCriticalIncidents(newCritical);
      setIsAlarming(true);

      // Lazy-init AudioContext (must be created after a user gesture has
      // happened; browsers allow it after the first interaction).
      if (!audioCtxRef.current) {
        audioCtxRef.current = new (window.AudioContext ||
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          (window as any).webkitAudioContext)();
      }

      // Stop any existing tone first
      if (stopToneRef.current) {
        stopToneRef.current();
      }

      stopToneRef.current = startAlarmTone(audioCtxRef.current);
    }

    // If all critical incidents have been resolved/acked externally, stop alarm
    if (isAlarming && newCritical.length === 0) {
      if (stopToneRef.current) {
        stopToneRef.current();
        stopToneRef.current = null;
      }
      setIsAlarming(false);
      setCriticalIncidents([]);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [incidents]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (stopToneRef.current) stopToneRef.current();
    };
  }, []);

  return { isAlarming, criticalIncidents, stopAlarm };
}
