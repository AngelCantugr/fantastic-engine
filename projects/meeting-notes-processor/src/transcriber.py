"""
Audio transcription using OpenAI Whisper API
"""
import os
import logging
from pathlib import Path
from typing import Dict
import yaml

from openai import OpenAI
from pydub import AudioSegment


logger = logging.getLogger(__name__)


class Transcriber:
    """Handles audio transcription using Whisper API"""

    def __init__(self, settings_path: Path = None):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")

        self.client = OpenAI(api_key=self.api_key)
        self.model = os.getenv('WHISPER_MODEL', 'whisper-1')

        # Load settings
        self.settings = self._load_settings(settings_path)

    def _load_settings(self, settings_path: Path = None) -> dict:
        """Load processing settings"""
        if settings_path is None:
            settings_path = Path(__file__).parent.parent / 'config' / 'settings.yaml'

        with open(settings_path) as f:
            return yaml.safe_load(f)

    def transcribe(self, audio_path: Path) -> Dict:
        """
        Transcribe audio file

        Returns:
            Dict with 'text', 'duration', 'timestamps', etc.
        """
        logger.info(f"Transcribing {audio_path}")

        # Validate file
        self._validate_audio(audio_path)

        # Get audio info
        duration = self._get_duration(audio_path)
        logger.info(f"Audio duration: {duration}")

        # Chunk if needed
        if self._needs_chunking(audio_path):
            return self._transcribe_chunked(audio_path)
        else:
            return self._transcribe_single(audio_path)

    def _transcribe_single(self, audio_path: Path) -> Dict:
        """Transcribe single audio file"""
        with open(audio_path, 'rb') as audio_file:
            response = self.client.audio.transcriptions.create(
                model=self.model,
                file=audio_file,
                response_format='verbose_json',
                timestamp_granularities=['segment']
            )

        # Parse response
        result = {
            'text': response.text,
            'duration': response.duration,
            'language': response.language,
            'segments': []
        }

        # Extract segments with timestamps
        if hasattr(response, 'segments'):
            for segment in response.segments:
                result['segments'].append({
                    'text': segment['text'],
                    'start': segment['start'],
                    'end': segment['end']
                })

        return result

    def _transcribe_chunked(self, audio_path: Path) -> Dict:
        """Transcribe large file in chunks"""
        logger.info("File is large, processing in chunks...")

        chunk_duration = self.settings['audio']['chunk_duration_minutes'] * 60 * 1000  # ms
        overlap = self.settings['audio']['chunk_overlap_seconds'] * 1000  # ms

        # Load audio
        audio = AudioSegment.from_file(audio_path)

        # Split into chunks
        chunks = []
        for i in range(0, len(audio), chunk_duration - overlap):
            chunk = audio[i:i + chunk_duration]
            chunks.append(chunk)

        logger.info(f"Split into {len(chunks)} chunks")

        # Transcribe each chunk
        full_text = []
        all_segments = []

        for i, chunk in enumerate(chunks):
            logger.info(f"Transcribing chunk {i+1}/{len(chunks)}")

            # Save chunk temporarily
            cache_dir = Path(os.getenv('AUDIO_CACHE_DIR', 'audio_cache'))
            cache_dir.mkdir(exist_ok=True)
            chunk_path = cache_dir / f"chunk_{i}.mp3"

            chunk.export(chunk_path, format='mp3')

            # Transcribe
            result = self._transcribe_single(chunk_path)
            full_text.append(result['text'])

            # Adjust timestamps for chunk offset
            offset = i * (chunk_duration - overlap) / 1000  # seconds
            for segment in result.get('segments', []):
                segment['start'] += offset
                segment['end'] += offset
                all_segments.append(segment)

            # Cleanup
            chunk_path.unlink()

        return {
            'text': ' '.join(full_text),
            'duration': len(audio) / 1000,  # seconds
            'segments': all_segments,
            'chunked': True
        }

    def _validate_audio(self, audio_path: Path):
        """Validate audio file"""
        # Check format
        suffix = audio_path.suffix.lstrip('.')
        supported = self.settings['audio']['supported_formats']

        if suffix not in supported:
            raise ValueError(f"Unsupported format: {suffix}. Supported: {supported}")

        # Check size
        max_size_mb = self.settings['audio']['max_size_mb']
        size_mb = audio_path.stat().st_size / (1024 * 1024)

        if not self.settings['audio']['enable_chunking'] and size_mb > max_size_mb:
            raise ValueError(f"File too large: {size_mb:.1f}MB (max: {max_size_mb}MB)")

    def _needs_chunking(self, audio_path: Path) -> bool:
        """Check if file needs to be chunked"""
        if not self.settings['audio']['enable_chunking']:
            return False

        max_size_mb = self.settings['audio']['max_size_mb']
        size_mb = audio_path.stat().st_size / (1024 * 1024)

        return size_mb > max_size_mb

    def _get_duration(self, audio_path: Path) -> str:
        """Get audio duration as string"""
        try:
            audio = AudioSegment.from_file(audio_path)
            duration_sec = len(audio) / 1000
            minutes = int(duration_sec // 60)
            seconds = int(duration_sec % 60)
            return f"{minutes}m {seconds}s"
        except Exception as e:
            logger.warning(f"Could not get duration: {e}")
            return "Unknown"

    def estimate_cost(self, audio_path: Path) -> Dict:
        """Estimate transcription cost"""
        # Get duration in minutes
        try:
            audio = AudioSegment.from_file(audio_path)
            duration_min = len(audio) / 1000 / 60
        except Exception:
            # Estimate from file size
            size_mb = audio_path.stat().st_size / (1024 * 1024)
            duration_min = size_mb  # Rough estimate: 1 MB ≈ 1 minute

        # Whisper cost
        whisper_cost = duration_min * self.settings['cost_estimation']['whisper_per_minute']

        # GPT-4 analysis cost (estimate)
        tokens_per_min = self.settings['cost_estimation']['avg_transcript_tokens_per_minute']
        total_tokens = duration_min * tokens_per_min
        output_tokens = self.settings['cost_estimation']['avg_analysis_output_tokens']

        gpt_input_cost = (total_tokens / 1000) * self.settings['cost_estimation']['gpt4_per_1k_input_tokens']
        gpt_output_cost = (output_tokens / 1000) * self.settings['cost_estimation']['gpt4_per_1k_output_tokens']

        return {
            'transcription': whisper_cost,
            'analysis': gpt_input_cost + gpt_output_cost,
            'total': whisper_cost + gpt_input_cost + gpt_output_cost,
            'duration_minutes': duration_min
        }


if __name__ == '__main__':
    # Test transcriber
    transcriber = Transcriber()

    audio_file = Path('test_audio.mp3')
    if audio_file.exists():
        # Estimate cost
        cost = transcriber.estimate_cost(audio_file)
        print(f"Estimated cost: ${cost['total']:.2f}")

        # Transcribe
        result = transcriber.transcribe(audio_file)
        print(f"\nTranscript:\n{result['text'][:500]}...")
