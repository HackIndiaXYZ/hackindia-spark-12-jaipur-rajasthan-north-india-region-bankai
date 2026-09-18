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
 * Synthesise a repeating alarm tone using Web Audio API.
 * Returns a cleanup function that stops all oscillators.
 */
function startAlarmTone(audioCtx: AudioContext): () => void {
  let stopped = false;
  const oscillators: OscillatorNode[] = [];

  // Two-tone siren: alternate between 880 Hz and 1100 Hz every 600 ms
  const tones = [880, 1100];
  let idx = 0;

  function playNextTone() {
    if (stopped) return;

    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();

    osc.type = "sine";
    osc.frequency.value = tones[idx % 2];
    idx++;

    gain.gain.setValueAtTime(0, audioCtx.currentTime);
    gain.gain.linearRampToValueAtTime(0.3, audioCtx.currentTime + 0.05);
    gain.gain.linearRampToValueAtTime(0.3, audioCtx.currentTime + 0.5);
    gain.gain.linearRampToValueAtTime(0, audioCtx.currentTime + 0.6);

    osc.connect(gain);
    gain.connect(audioCtx.destination);

    osc.start(audioCtx.currentTime);
    osc.stop(audioCtx.currentTime + 0.6);
    oscillators.push(osc);

    // Schedule the next tone
    setTimeout(playNextTone, 650);
  }

  playNextTone();

  return () => {
    stopped = true;
    oscillators.forEach((o) => {
      try { o.stop(); } catch { /* already stopped */ }
    });
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
