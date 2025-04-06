import io
import os
import sys
import threading
import contextlib
import asyncio
import click
from pathlib import Path
from typing import Literal

from mcp.server.fastmcp import FastMCP
from openai import OpenAI
from pydub import AudioSegment  # type: ignore
from pydub.playback import play  # type: ignore


client = OpenAI()

# Path to the ding sound file
PACKAGE_DIR = Path(__file__).parent
DING_SOUND = str(PACKAGE_DIR / "ding.aiff")

# OpenAI TTS supported voices
VoiceType = Literal["alloy", "ash", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer"]

# Global settings
PLAY_DING = False
TTS_VOICE: VoiceType = "coral"
TTS_SPEED = 4.0
TTS_INSTRUCTIONS = """Voice Affect: Calm, instilling trust without much intensity, in control, relaxed.

Tone: Sincere, empathetic, light-hearted, relaxed.

Pacing: Quick delivery when desribing things but un-intense. Sometimes deliberate pauses.

Emotion: Friendly and warm

Personality: Relatable. Very friendly and warm."""

TOOL_DESCRIPTION = "Use this to send a short audio message to the user concisely (one 10-15 word sentence) summarizing what you've done and why. Use this tool after _every_ time you generated a code snippet or ran a command as well as when you give control back to the user."

def generate_speech(
    text: str,
    model: str = "gpt-4o-mini-tts",
    voice: VoiceType = "coral",
    speed: float = 4.0,
    instructions: str | None = None
) -> bytes:
    # Ignore type checking for the OpenAI API call as it's complex to satisfy mypy
    response = client.audio.speech.create(  # type: ignore
        model=model,
        voice=voice,
        input=text,
        speed=speed,
        instructions=instructions,  # type: ignore
    )
    return response.content

def play_audio(audio_bytes: bytes, ding_sound_path: str = DING_SOUND) -> None:
    # Play ding sound first if enabled and available
    if PLAY_DING and os.path.exists(ding_sound_path):
        try:
            ding_sound = AudioSegment.from_file(ding_sound_path)
            # Suppress stdout during playback
            with open(os.devnull, 'w') as devnull:
                with contextlib.redirect_stdout(devnull):
                    play(ding_sound)
        except Exception as e:
            print(f"Warning: Could not play ding sound: {e}", file=sys.stderr)
    
    # Then play the generated speech
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
    # Suppress stdout during playback
    with open(os.devnull, 'w') as devnull:
        with contextlib.redirect_stdout(devnull):
            play(audio)

mcp = FastMCP("Voice Status Report")

# Create a semaphore to ensure only one audio playback happens at a time
audio_semaphore = threading.Semaphore(1)

@mcp.tool(description=TOOL_DESCRIPTION)
def summarize(text: str) -> dict[str, str]:
    try:
        # Make the TTS API request synchronously
        audio_bytes = generate_speech(
            text=text,
            model="gpt-4o-mini-tts",
            voice=TTS_VOICE,  # Use global setting
            speed=TTS_SPEED,  # Use global setting
            instructions=TTS_INSTRUCTIONS  # Use global setting
        )
        
        # Schedule audio playback in background
        def play_audio_in_background() -> None:
            try:
                # Acquire the semaphore - blocks if another thread has it
                audio_semaphore.acquire()
                play_audio(audio_bytes, DING_SOUND)
            except Exception as e:
                # Report exceptions while avoiding stdout pollution
                print(f"Error in background audio playback: {e}", file=sys.stderr)
            finally:
                # Always release the semaphore
                audio_semaphore.release()
        
        # Start only the audio playback in a background thread
        threading.Thread(target=play_audio_in_background, daemon=True).start()
        
        return {"status": "success", "message": "Audio generated and playback scheduled! Please move on to the next task."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def async_main(
    ding: bool = False,
    voice: VoiceType = "coral",
    speed: float = 4.0,
    instructions: str | None = None
) -> None:
    """Asynchronous main function that starts the MCP server."""
    global PLAY_DING, TTS_VOICE, TTS_SPEED, TTS_INSTRUCTIONS
    
    # Set global settings
    PLAY_DING = ding
    TTS_VOICE = voice
    TTS_SPEED = speed
    if instructions:
        TTS_INSTRUCTIONS = instructions
    
    # Print status
    ding_status = "enabled" if PLAY_DING else "disabled"
    print("Starting the Voice Status Report MCP server!")
    print(f"- Ding sound: {ding_status}")
    print(f"- Voice: {TTS_VOICE}")
    print(f"- Speed: {TTS_SPEED}")
    
    # Create an asyncio-compatible version of the MCP server run
    await asyncio.to_thread(mcp.run, transport="stdio")

@click.command()
@click.option("--ding", is_flag=True, help="Enable ding sound before speech")
@click.option(
    "--voice", 
    type=click.Choice(["alloy", "ash", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer"]),
    default="coral",
    help="Voice to use for speech generation"
)
@click.option(
    "--speed", 
    type=float,
    default=4.0,
    help="Speech speed (0.5-4.0, where higher is faster)"
)
@click.option(
    "--instructions", 
    type=str,
    help="Custom voice instructions for the TTS model"
)
def cli_main(ding: bool, voice: VoiceType, speed: float, instructions: str | None) -> None:
    """Command-line entry point that calls the async main function."""
    asyncio.run(async_main(ding, voice, speed, instructions))
    
# Keep the main function for backward compatibility and direct imports
main = cli_main
    
if __name__ == "__main__":
    cli_main() 