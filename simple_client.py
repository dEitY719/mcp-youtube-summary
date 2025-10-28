"""Simple Direct MCP Client - No Async Required."""

import json
import subprocess
import sys
import time
from typing import Any


class SimpleMCPClient:
    """Simple MCP client that communicates via stdio."""

    def __init__(self, command: list[str]) -> None:
        """Initialize the client."""
        self.command = command
        self.process: subprocess.Popen[str] | None = None
        self.request_id = 1

    def start(self) -> None:
        """Start the server process."""
        print("🚀 Starting server...")
        self.process = subprocess.Popen(
            self.command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        # Wait for server to initialize
        time.sleep(2)
        print("✅ Server started")

        # Send initialize request
        print("🔧 Initializing MCP connection...")
        try:
            response = self.send_request(
                "initialize",
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "simple-client",
                        "version": "0.1.0",
                    },
                },
            )

            if "error" in response:
                print(f"⚠️  Initialize warning: {response['error']}")
            else:
                print("✅ MCP connection initialized")
        except Exception as e:
            print(f"⚠️  Initialize error: {e}")

    def send_request(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        """Send a JSON-RPC request and return the response."""
        if not self.process or not self.process.stdin or not self.process.stdout:
            raise RuntimeError("Server not started")

        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params,
        }

        self.request_id += 1

        # Send request
        request_json = json.dumps(request)
        print(f"\n📤 Request: {request_json}")
        self.process.stdin.write(request_json + "\n")
        self.process.stdin.flush()

        # Read response
        response_json = self.process.stdout.readline()
        if not response_json:
            raise RuntimeError("No response from server")

        response = json.loads(response_json)
        return response

    def list_tools(self) -> list[dict[str, Any]]:
        """List all available tools."""
        response = self.send_request("tools/list", {})

        if "error" in response:
            raise RuntimeError(f"Error: {response['error']}")

        tools = response.get("result", {}).get("tools", [])
        return tools

    def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> str:
        """Call a tool and return the result."""
        response = self.send_request(
            "tools/call",
            {
                "name": tool_name,
                "arguments": arguments,
            },
        )

        if "error" in response:
            raise RuntimeError(f"Error: {response['error']}")

        # Extract text from response
        result = response.get("result", {})
        content = result.get("content", [])

        if content and isinstance(content, list):
            return content[0].get("text", "No result")

        return json.dumps(result, indent=2)

    def close(self) -> None:
        """Close the server connection."""
        if self.process:
            self.process.terminate()
            print("\n✅ Server stopped")


def print_tools(client: SimpleMCPClient) -> None:
    """List and display all tools."""
    print("\n" + "=" * 60)
    print("📋 Available Tools")
    print("=" * 60)

    try:
        tools = client.list_tools()

        if not tools:
            print("No tools found")
            return

        for tool in tools:
            print(f"\n🔧 {tool['name']}")
            print(f"   Description: {tool.get('description', 'N/A')}")
            if "inputSchema" in tool:
                schema = tool["inputSchema"]
                props = schema.get("properties", {})
                required = schema.get("required", [])

                if props:
                    print("   Parameters:")
                    for name, info in props.items():
                        req = " (required)" if name in required else " (optional)"
                        print(f"     - {name}: {info.get('description', '')} {req}")

    except Exception as e:
        print(f"❌ Error listing tools: {e}")


def example_get_transcript(client: SimpleMCPClient) -> None:
    """Example: Get transcript."""
    print("\n" + "=" * 60)
    print("📝 Example 1: Get Transcript")
    print("=" * 60)

    try:
        result = client.call_tool(
            "get_transcript",
            {
                "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "language": "en",
            },
        )

        print("\n📄 Transcript (first 200 chars):")
        print(result[:200] + "..." if len(result) > 200 else result)

    except Exception as e:
        print(f"⚠️ Skipped: {e}")


def example_summarize(client: SimpleMCPClient) -> None:
    """Example: Summarize video."""
    print("\n" + "=" * 60)
    print("📊 Example 2: Summarize Video")
    print("=" * 60)

    try:
        result = client.call_tool(
            "summarize_video",
            {
                "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "summary_length": "short",
            },
        )

        print("\n📋 Summary:")
        print(result)

    except Exception as e:
        print(f"⚠️ Skipped: {e}")


def example_key_points(client: SimpleMCPClient) -> None:
    """Example: Extract key points."""
    print("\n" + "=" * 60)
    print("🎯 Example 3: Extract Key Points")
    print("=" * 60)

    try:
        result = client.call_tool(
            "extract_key_points",
            {
                "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "num_points": 3,
            },
        )

        print("\n✨ Key Points:")
        print(result)

    except Exception as e:
        print(f"⚠️ Skipped: {e}")


def example_metadata(client: SimpleMCPClient) -> None:
    """Example: Get metadata."""
    print("\n" + "=" * 60)
    print("📹 Example 4: Get Video Metadata")
    print("=" * 60)

    try:
        result = client.call_tool(
            "get_video_metadata",
            {
                "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            },
        )

        print("\n📊 Metadata:")
        print(result)

    except Exception as e:
        print(f"⚠️ Skipped: {e}")


def interactive_mode(client: SimpleMCPClient) -> None:
    """Interactive mode."""
    print("\n" + "=" * 60)
    print("🎯 Interactive Mode")
    print("=" * 60)
    print("Commands:")
    print("  help                                    - Show this help")
    print("  list                                    - List tools")
    print("  get_transcript <url> [lang]            - Get transcript")
    print("  summarize <url> [short|medium|long]    - Summarize")
    print("  key_points <url> [num]                 - Extract key points")
    print("  metadata <url>                         - Get metadata")
    print("  quit                                   - Exit")

    while True:
        try:
            user_input = input("\n> ").strip()

            if not user_input:
                continue

            if user_input.lower() == "quit":
                print("Goodbye!")
                break

            if user_input.lower() in ["help", "?"]:
                print("Commands:")
                print("  list - List all tools")
                print("  get_transcript <url> [lang] - Get transcript")
                print("  summarize <url> [length] - Summarize (short/medium/long)")
                print("  key_points <url> [num] - Extract key points")
                print("  metadata <url> - Get metadata")
                print("  quit - Exit")
                continue

            if user_input.lower() == "list":
                print_tools(client)
                continue

            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            if command == "get_transcript":
                url_parts = args.split()
                if url_parts:
                    url = url_parts[0]
                    lang = url_parts[1] if len(url_parts) > 1 else "en"
                    result = client.call_tool("get_transcript", {
                        "video_url": url,
                        "language": lang,
                    })
                    print("\n📄 Result:")
                    print(result[:500] + "..." if len(result) > 500 else result)
                else:
                    print("❌ Usage: get_transcript <url> [language]")

            elif command == "summarize":
                url_parts = args.split()
                if url_parts:
                    url = url_parts[0]
                    length = url_parts[1] if len(url_parts) > 1 else "medium"
                    result = client.call_tool("summarize_video", {
                        "video_url": url,
                        "summary_length": length,
                    })
                    print("\n📊 Result:")
                    print(result)
                else:
                    print("❌ Usage: summarize <url> [short|medium|long]")

            elif command == "key_points":
                url_parts = args.split()
                if url_parts:
                    url = url_parts[0]
                    num = int(url_parts[1]) if len(url_parts) > 1 else 5
                    result = client.call_tool("extract_key_points", {
                        "video_url": url,
                        "num_points": num,
                    })
                    print("\n🎯 Result:")
                    print(result)
                else:
                    print("❌ Usage: key_points <url> [num_points]")

            elif command == "metadata":
                if args:
                    result = client.call_tool("get_video_metadata", {
                        "video_url": args,
                    })
                    print("\n📹 Result:")
                    print(result)
                else:
                    print("❌ Usage: metadata <url>")

            else:
                print(f"❌ Unknown command: {command}")
                print("Type 'help' for available commands")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def main() -> None:
    """Main function."""
    print("\n" + "=" * 60)
    print("  🎬 YouTube Summary MCP - Simple Client")
    print("=" * 60)

    client = SimpleMCPClient(["uv", "run", "youtube-summary-mcp"])

    try:
        client.start()

        # List tools
        print_tools(client)

        if "--interactive" in sys.argv:
            # Interactive mode
            interactive_mode(client)
        else:
            # Run examples
            print("\n" + "=" * 60)
            print("Running Examples (--interactive for interactive mode)")
            print("=" * 60)

            example_get_transcript(client)
            example_summarize(client)
            example_key_points(client)
            example_metadata(client)

            print("\n" + "=" * 60)
            print("Examples completed!")
            print("Run with --interactive for interactive mode")
            print("=" * 60)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        client.close()


if __name__ == "__main__":
    main()
