import io
import os
import sys
import threading
import contextlib
import asyncio
import click
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from openai import OpenAI
from pydub import AudioSegment
from pydub.playback import play


client = OpenAI()

# Path to the local notification sound file
PACKAGE_DIR = Path(__file__).parent
NOTIFICATION_SOUND = str(PACKAGE_DIR / "ding.aiff")

# Global setting for whether to play the ding sound
PLAY_DING = False

TOOL_DESCRIPTION = "Use this to send a short audio message to the user concisely (one 10-15 word sentence) summarizing what you've done and why. Use this tool after _every_ time you generated a code snippet or ran a command as well as when you give control back to the user."

def generate_speech(
    text: str,
    model: str = "gpt-4o-mini-tts",
    voice: str = "coral",
    speed: float = 4.0,
    instructions: str = None
) -> bytes:
    response = client.audio.speech.create(
        model=model,
        voice=voice,
        input=text,
        speed=speed,
        instructions=instructions,
    )
    return response.content

def play_audio(audio_bytes: bytes, notification_sound_path: str = NOTIFICATION_SOUND) -> None:
    # Play notification sound first if enabled and available
    if PLAY_DING and os.path.exists(notification_sound_path):
        try:
            notification_sound = AudioSegment.from_file(notification_sound_path)
            # Suppress stdout during playback
            with open(os.devnull, 'w') as devnull:
                with contextlib.redirect_stdout(devnull):
                    play(notification_sound)
        except Exception as e:
            print(f"Warning: Could not play notification sound: {e}", file=sys.stderr)
    
    # Then play the generated speech
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
    # Suppress stdout during playback
    with open(os.devnull, 'w') as devnull:
        with contextlib.redirect_stdout(devnull):
            play(audio)

mcp = FastMCP("Voice Status Report")

# Create a semaphore to ensure only one audio playback happens at a time
audio_semaphore = threading.Semaphore(1)

INSTRUCTIONS = """Voice Affect: Calm, instilling trust without much intensity, in control, relaxed.

Tone: Sincere, empathetic, light-hearted, relaxed.

Pacing: Quick delivery when desribing things but un-intense. Sometimes deliberate pauses.

Emotion: Friendly and warm

Personality: Relatable. Very friendly and warm."""

@mcp.tool(description=TOOL_DESCRIPTION)
def summarize(text: str) -> dict[str, str]:
    try:
        # Make the TTS API request synchronously
        audio_bytes = generate_speech(
            text=text,
            model="gpt-4o-mini-tts",
            voice="coral",
            speed=4,
            instructions=INSTRUCTIONS
        )
        
        # Schedule audio playback in background
        def play_audio_in_background():
            try:
                # Acquire the semaphore - blocks if another thread has it
                audio_semaphore.acquire()
                play_audio(audio_bytes, NOTIFICATION_SOUND)
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

async def async_main(ding: bool = False) -> None:
    """Asynchronous main function that starts the MCP server."""
    global PLAY_DING
    PLAY_DING = ding
    
    ding_status = "enabled" if PLAY_DING else "disabled"
    print(f"Starting the Voice Status Report MCP server! (Notification sound: {ding_status})")
    
    # Create an asyncio-compatible version of the MCP server run
    await asyncio.to_thread(mcp.run, transport="stdio")

@click.command()
@click.option("--ding", is_flag=True, help="Enable notification sound before speech")
def cli_main(ding: bool) -> None:
    """Command-line entry point that calls the async main function."""
    asyncio.run(async_main(ding))
    
# Keep the main function for backward compatibility and direct imports
main = cli_main
    
if __name__ == "__main__":
    cli_main() 