# Voice Status Report MCP Server ![Python Package](https://github.com/tomekkorbak/voice-status-report-mcp-server/workflows/Python%20Package/badge.svg) [![PyPI version](https://badge.fury.io/py/voice-status-report-mcp-server.svg)](https://badge.fury.io/py/voice-status-report-mcp-server) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)

A [Model Context Protocol](https://modelcontextprotocol.io/introduction) (MCP) server that provides voice status updates using [OpenAI's text-to-speech API](https://platform.openai.com/docs/guides/text-to-speech). This allows language models to communicate with users through short voice messages: reporting on the progress of a task, or confirming that a command has been executed.

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

The server accepts the following command line option:

- `--ding`: Enable the notification sound that plays before each voice message. By default, the notification sound is disabled.

## Example Usage

Once connected, Claude can use the tool to provide audio feedback like:

- "Added a new function to handle user authentication"
- "Fixed the bug in the login form"
- "Created a new file for the API client"
- "Added OpenAI TTS documentation link"

## License

This project is licensed under the MIT License - see the LICENSE file for details.