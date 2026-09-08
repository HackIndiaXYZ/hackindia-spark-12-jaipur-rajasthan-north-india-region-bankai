import json
import os
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.logging import logger
from app.schemas.ai_analysis import AIAnalysisResult, AIAnalysisResponse


class AIAnalysisService:
    """
    Server-side Grounded Gemini AI Analysis & Response Intelligence Service.
    Explains pre-computed AquaSentinel incident evidence and generates structured operator guidance.
    Gemini is NOT the primary detection engine; deterministic facts are computed upstream.
    """

    def __init__(self):
        self._analysis_cache: Dict[str, AIAnalysisResponse] = {}
        self.api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
        self.model_name = settings.GEMINI_MODEL or "gemini-2.5-flash"
        self._client = None
        self._initialize_client()

    def _initialize_client(self):
        if self.api_key and self.api_key.strip():
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
                logger.info(f"Initialized Gemini AI client with model '{self.model_name}'")
            except Exception as e:
                logger.warning(f"Failed to initialize google.genai Client: {e}. Will use fallback.")
                self._client = None
        else:
            logger.info("GEMINI_API_KEY not configured. AIAnalysisService running in deterministic fallback mode.")

    def analyze_incident(self, incident_data: Dict[str, Any], force_refresh: bool = False) -> AIAnalysisResponse:
        """
        Generates or retrieves cached grounded AI analysis for a persisted incident.
        """
        incident_id = incident_data.get("incident_id", "UNKNOWN")

        # Cache check to avoid duplicate API calls
        if not force_refresh and incident_id in self._analysis_cache:
            logger.info(f"Returning cached AI analysis for incident {incident_id}")
            return self._analysis_cache[incident_id]

        # Attempt Gemini AI generation if client is available
        if self._client:
            try:
                response = self._generate_gemini_analysis(incident_data)
                if response:
                  self._analysis_cache[incident_id] = response
                  return response
            except Exception as e:
                logger.error(f"Gemini API request failed for incident {incident_id}: {e}. Falling back.")

        # Fallback analysis
        fallback = self._generate_fallback_analysis(incident_data)
        self._analysis_cache[incident_id] = fallback
        return fallback

    def _generate_gemini_analysis(self, data: Dict[str, Any]) -> Optional[AIAnalysisResponse]:
        """Calls Gemini API with structured incident facts and strict grounding constraints."""
        incident_id = data.get("incident_id", "INC-UNKNOWN")
        incident_type = data.get("incident_type", "LEAK_SUSPECTED")
        affected_segment = data.get("affected_segment", "UNKNOWN")
        confidence = data.get("confidence", 0.8)
        observability = data.get("observability_score", 0.85)
        flow_loss = data.get("estimated_flow_loss_lpm", 0.0)
        vol_loss = data.get("estimated_volume_loss_liters", 0.0)
        evidence = data.get("evidence", [])
        candidates = data.get("candidate_segments", [])
        responsive = data.get("responsive_sensors", [])

        prompt = f"""
You are AquaSentinel AI, an infrastructure intelligence explainability system.
Explain ONLY the supplied AquaSentinel evidence. Never invent sensor readings, measurements, affected segments, or hydraulic predictions.

SUPPLIED AQUASENTINEL INCIDENT FACTS:
- Incident ID: {incident_id}
- Incident Type: {incident_type}
- Severity: {data.get('severity', 'HIGH')}
- Affected Segment: {affected_segment}
- Affected Zone: {data.get('affected_zone', 'Zone_B')}
- Detection Delay: {data.get('detection_delay_min', 15.0)} minutes
- Confidence Score: {confidence * 100:.1f}%
- Observability Score: {observability * 100:.1f}%
- Estimated Flow Loss: {flow_loss} LPM (Model-derived simulation estimate)
- Estimated Volume Loss: {vol_loss} Liters (Model-derived simulation estimate)
- Responsive Sensors: {responsive}
- Candidate Segments: {candidates}
- Evidence Strings: {evidence}

STRICT INSTRUCTIONS:
1. Explain only the supplied facts above.
2. For SENSOR_FAULT: Explain that the anomaly is isolated to the target sensor while neighboring sensors remain normal, preventing a false leak alarm.
3. For LEAK_SUSPECTED / BURST_EVENT: Explain the pressure/flow variance and topology evidence supporting localization to {affected_segment}.
4. Provide 2-3 practical operator action steps.
5. Clearly label loss figures as model-derived simulation estimates.
6. Output MUST be valid JSON with exact keys: "summary", "why_detected", "recommended_actions", "confidence_note", "limitations".
"""

        try:
            from google.genai import types
            res = self._client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=AIAnalysisResult
                )
            )

            if res.text:
                parsed_json = json.loads(res.text)
                validated_result = AIAnalysisResult(**parsed_json)
                return AIAnalysisResponse(
                    incident_id=incident_id,
                    analysis=validated_result,
                    provider="gemini"
                )
        except Exception as err:
            logger.warning(f"Failed to generate structured Gemini response: {err}")

        return None

    def _generate_fallback_analysis(self, data: Dict[str, Any]) -> AIAnalysisResponse:
        """Generates a deterministic fallback analysis grounded entirely in existing AquaSentinel facts."""
        incident_id = data.get("incident_id", "INC-UNKNOWN")
        incident_type = data.get("incident_type", "LEAK_SUSPECTED")
        affected_segment = data.get("affected_segment", "B2-B3")
        affected_zone = data.get("affected_zone", "Zone_B")
        confidence = data.get("confidence", 0.879)
        observability = data.get("observability_score", 0.897)
        flow_loss = data.get("estimated_flow_loss_lpm", 30.94)
        vol_loss = data.get("estimated_volume_loss_liters", 1082.8)
        evidence = data.get("evidence", [])
        responsive = data.get("responsive_sensors", ["B1", "B2", "B3", "B4"])

        is_sensor_fault = incident_type == "SENSOR_FAULT" or "SENSOR_FAULT" in str(data.get("evidence", []))

        if is_sensor_fault:
            summary = f"Sensor fault classified on telemetry node. Spatial correlation confirms pipeline {affected_segment} remains healthy."
            why_detected = [
                "Telemetry anomaly is isolated to a single sensor node without spatial pressure propagation.",
                "Neighboring upstream and downstream sensors report completely normal pressure baselines.",
                "Topology graph agreement confirms zero correlated flow discrepancy across pipeline network."
            ]
            recommended_actions = [
                "Do NOT declare a pipeline leak or dispatch excavation crews.",
                "Inspect, recalibrate, or replace telemetry sensor transducer electronics.",
                "Verify sensor health status in operational dashboard."
            ]
            confidence_note = f"High-confidence sensor fault isolation ({confidence * 100:.1f}%) based on spatial neighbor agreement."
            limitations = "Zero estimated water loss. Anomaly confined to sensor electronics."
        elif incident_type in ("BURST_EVENT", "BURST_SUSPECTED"):
            summary = f"Severe burst event detected on primary trunk segment {affected_segment} in {affected_zone}."
            why_detected = [
                f"Catastrophic pressure drop and high rate-of-change flow surge detected on segment {affected_segment}.",
                f"Correlated node agreement across responsive sensors {', '.join(responsive)}.",
                f"Sustained flow discrepancy resulting in model-derived loss rate of {flow_loss} LPM."
            ]
            recommended_actions = [
                f"IMMEDIATE ACTION: Close isolation valves upstream and downstream of segment {affected_segment}.",
                f"Dispatch emergency repair crew to {affected_zone}.",
                "Reroute distribution flow via secondary feeder trunk if pressure drops below target thresholds."
            ]
            confidence_note = f"Critical confidence ({confidence * 100:.1f}%) supported by rapid transient pressure propagation."
            limitations = f"Estimated loss rate ({flow_loss} LPM) is a model-derived simulation estimate."
        else:
            # Default LEAK_SUSPECTED
            summary = f"Suspected water leak localized to pipeline segment {affected_segment} in {affected_zone}."
            why_detected = evidence if evidence else [
                f"Correlated pressure deviation detected across responsive sensors {', '.join(responsive)}.",
                f"Net flow variance of {flow_loss} LPM measured between boundary nodes of segment {affected_segment}.",
                f"Topology observability score of {observability * 100:.1f}% supports candidate localization."
            ]
            recommended_actions = [
                f"Dispatch field maintenance team to inspect pipeline segment {affected_segment} in {affected_zone}.",
                "Verify relevant downstream pressure conditions and check isolation valve positioning.",
                "Acknowledge incident in control console to log field dispatch."
            ]
            confidence_note = f"{confidence * 100:.1f}% confidence score based on topology correlation and persistence."
            limitations = f"Loss estimates ({flow_loss} LPM / {vol_loss} L) are model-derived simulation estimates intended for system evaluation."

        analysis_result = AIAnalysisResult(
            summary=summary,
            why_detected=why_detected,
            recommended_actions=recommended_actions,
            confidence_note=confidence_note,
            limitations=limitations
        )

        return AIAnalysisResponse(
            incident_id=incident_id,
            analysis=analysis_result,
            provider="deterministic_fallback"
        )
