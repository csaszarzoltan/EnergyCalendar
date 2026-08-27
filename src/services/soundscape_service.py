"""Web Audio neural soundscape synthesizer parameter generator."""
from __future__ import annotations

from src.models.market_circadian import (
    BrainwaveType,
    SoundscapeRequest,
    SoundscapeResponse,
)


class SoundscapeSynthService:
    """Generates real-time parameter matrices for binaural beats and colored noise synthesis."""

    @staticmethod
    def generate_config(request: SoundscapeRequest) -> SoundscapeResponse:
        """Map cognitive load and target brainwave into precise audio synthesizer values."""
        target = request.target_brainwave
        load = request.cognitive_load.upper()

        if target == BrainwaveType.GAMMA or (target is None and load == "DEEP_WORK"):
            return SoundscapeResponse(
                carrier_freq_hz=200.0,
                binaural_beat_hz=40.0,  # 40Hz Gamma for deep problem-solving
                noise_color="PINK",
                filter_cutoff_hz=500,
                brainwave_target="40Hz Gamma (Fókusz & Problémamegoldás)",
                usage_guidance="40Hz Gamma binaurális ritmus rózsaszín zajjal szűrt mély fókuszhoz.",
            )
        elif target == BrainwaveType.THETA or (target is None and load == "CREATIVE"):
            return SoundscapeResponse(
                carrier_freq_hz=180.0,
                binaural_beat_hz=6.0,  # 6Hz Theta for creative flow
                noise_color="PINK",
                filter_cutoff_hz=350,
                brainwave_target="6Hz Theta (Kreatív Flow & Ötletelés)",
                usage_guidance="6Hz Theta frekvencia asszociatív és tervezési feladatokhoz.",
            )
        elif target == BrainwaveType.DELTA or (target is None and load == "RECOVERY"):
            return SoundscapeResponse(
                carrier_freq_hz=140.0,
                binaural_beat_hz=2.5,  # 2.5Hz Delta for regeneration
                noise_color="BROWN",
                filter_cutoff_hz=250,
                brainwave_target="2.5Hz Delta (Mély Regeneráció)",
                usage_guidance="Barna zajjal kísért Delta hullám idegrendszeri lecsendesedéshez.",
            )
        else:
            return SoundscapeResponse(
                carrier_freq_hz=210.0,
                binaural_beat_hz=10.0,  # 10Hz Alpha standard
                noise_color="BROWN",
                filter_cutoff_hz=450,
                brainwave_target="10Hz Alfa (Nyugodt Éberség)",
                usage_guidance="10Hz Alfa frekvencia kiegyensúlyozott munkavégzéshez.",
            )
