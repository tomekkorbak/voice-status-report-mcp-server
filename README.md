# Voice Status Report MCP Server

![Python Package](https://github.com/tomekkorbak/voice-status-report-mcp-server/workflows/Python%20Package/badge.svg) [![PyPI version](https://badge.fury.io/py/voice-status-report-mcp-server.svg)](https://badge.fury.io/py/voice-status-report-mcp-server) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/) [![Install MCP Server](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/install-mcp?name=voice-status-report&config=eyJjb21tYW5kIjoidXZ4IHZvaWNlLXN0YXR1cy1yZXBvcnQtbWNwLXNlcnZlciIsImVudiI6eyJPUEVOQUlfQVBJX0tFWSI6IllPVVJfT1BFTkFJX0FQSV9LRVkifX0%3D)

A [Model Context Protocol](https://modelcontextprotocol.io/introduction) (MCP) server that provides voice status updates using [OpenAI's text-to-speech API](https://platform.openai.com/docs/guides/text-to-speech). This allows language models to communicate with users through short voice messages: reporting on the progress of a task, or confirming that a command has been executed. It's espesially useful when working with Cursor or Claude code: you can give the agent a task, go on to do something else but keep receiving status reports on agent's progess and when it's done with its task and needs your attention.

This MCP server is meant to be batteries included: the description of the `summarize` tool (prepended to system message by most MCP clients) asks the model to use this tool to report on the progress of a task.

## Available Tools

The server exposes the following tool:

- `summarize(text: str)`: Converts the provided text into speech using OpenAI's TTS API and plays it to the user. This is useful for providing status updates or confirmations after code changes or commands.

## Usage

You'll need an OpenAI API key to use this server.

### Claude for Desktop

Update your `claude_desktop_config.json` (located in `~/Library/Application\ Support/Claude/claude_desktop_config.json` on macOS and `%APPDATA%/Claude/claude_desktop_config.json` on Windows) to include the following:

```json
{
  "mcpServers": {
    "voice-status-report": {
      "command": "uvx",
      "args": [
        "voice-status-report-mcp-server"
      ],
      "env": {
        "OPENAI_API_KEY": "YOUR_OPENAI_API_KEY"
      }
    }
  }
}
```

## Command Line Options

The server accepts the following command line options:

- `--ding`: Enable the ding sound that plays before each voice message. By default, the ding sound is disabled.
- `--voice [VOICE]`: Choose the voice for speech generation. Available options: `alloy`, `ash`, `coral` (default), `echo`, `fable`, `onyx`, `nova`, `sage`, `shimmer`.
- `--speed SPEED`: Set the speech speed (0.5-4.0, where higher is faster). Default is 4.0.
- `--instructions TEXT`: Provide custom voice instructions for the TTS model. By default, the server uses a preset instruction for a calm, friendly voice.

### Examples

```bash
# Run with ding sound enabled and a different voice
voice-status-report-mcp-server --ding --voice nova

# Run with a slower speech speed
voice-status-report-mcp-server --speed 2.0

# Run with custom voice instructions
voice-status-report-mcp-server --instructions "Voice should be confident and authoritative"
```

### Claude for Desktop Configuration Examples

```json
{
  "mcpServers": {
    "voice-status-calm": {
      "command": "uvx",
      "args": [
        "voice-status-report-mcp-server",
      ],
      "env": {
        "OPENAI_API_KEY": "YOUR_OPENAI_API_KEY"
      }
    },
  }
}
```

When using non-default arguments, you can use the following configuration:

```json
{
  "mcpServers": {
    "voice-status-report-mcp-server": {
      "command": "uvx",
      "args": [
        "voice-status-report-mcp-server",
        "--ding",
        "--voice", "nova",
        "--speed", "3.0",
        "--instructions", "Voice should be confident and authoritative"
      ],
      "env": {
        "OPENAI_API_KEY": "YOUR_OPENAI_API_KEY"
      }
    }
  }
}
```

## Example Usage

Once connected, Claude can use the tool to provide audio feedback like:

- "Added a new function to handle user authentication"
- "Fixed the bug in the login form"
- "Created a new file for the API client"
- "Added OpenAI TTS documentation link"

## License

This project is licensed under the MIT License - see the LICENSE file for details.
