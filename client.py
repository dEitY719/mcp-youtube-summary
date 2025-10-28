"""Simple MCP Client for YouTube Summary Server."""

import asyncio
import json
import sys
from typing import Any

from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.client.session import ClientSession


async def list_tools(session: ClientSession) -> None:
    """List all available tools."""
    print("\n📋 Available Tools:")
    print("=" * 60)

    tools = await session.list_tools()
    for tool in tools.tools:
        print(f"\n🔧 {tool.name}")
        print(f"   Description: {tool.description}")
        if tool.inputSchema:
            print(f"   Input Schema:")
            for prop_name, prop_info in tool.inputSchema.get("properties", {}).items():
                required = prop_name in tool.inputSchema.get("required", [])
                req_str = "(required)" if required else "(optional)"
                print(f"     - {prop_name}: {req_str}")


async def call_tool(
    session: ClientSession,
    tool_name: str,
    arguments: dict[str, Any],
) -> str:
    """Call a tool and return the result."""
    print(f"\n🚀 Calling: {tool_name}")
    print(f"   Arguments: {json.dumps(arguments, indent=2)}")
    print("=" * 60)

    result = await session.call_tool(tool_name, arguments)

    # Extract text from result
    if result.content:
        text_content = result.content[0]
        return text_content.text
    return "No result"


async def get_transcript_example(session: ClientSession) -> None:
    """Example: Get transcript from a video."""
    print("\n\n📝 EXAMPLE 1: Get Transcript")
    print("=" * 60)

    # YouTube Rickroll video (famous example)
    video_url = "https://www.youtube.com/watch?v=HQU2vbsbXkU"

    result = await call_tool(
        session,
        "get_transcript",
        {
            "video_url": video_url,
            "language": "en",
        },
    )

    # Print first 200 characters
    print("\n📄 Transcript (first 200 chars):")
    print(result[:200] + "..." if len(result) > 200 else result)


async def summarize_video_example(session: ClientSession) -> None:
    """Example: Summarize a video."""
    print("\n\n📊 EXAMPLE 2: Summarize Video")
    print("=" * 60)

    video_url = "https://www.youtube.com/watch?v=HQU2vbsbXkU"

    result = await call_tool(
        session,
        "summarize_video",
        {
            "video_url": video_url,
            "summary_length": "short",
            "language": "en",
        },
    )

    print("\n📋 Summary (short):")
    print(result)


async def extract_key_points_example(session: ClientSession) -> None:
    """Example: Extract key points from a video."""
    print("\n\n🎯 EXAMPLE 3: Extract Key Points")
    print("=" * 60)

    video_url = "https://www.youtube.com/watch?v=HQU2vbsbXkU"

    result = await call_tool(
        session,
        "extract_key_points",
        {
            "video_url": video_url,
            "num_points": 3,
            "language": "en",
        },
    )

    print("\n✨ Key Points:")
    print(result)


async def get_metadata_example(session: ClientSession) -> None:
    """Example: Get video metadata."""
    print("\n\n📹 EXAMPLE 4: Get Video Metadata")
    print("=" * 60)

    video_url = "https://www.youtube.com/watch?v=HQU2vbsbXkU"

    result = await call_tool(
        session,
        "get_video_metadata",
        {
            "video_url": video_url,
        },
    )

    print("\n📊 Metadata:")
    print(result)


async def interactive_mode(session: ClientSession) -> None:
    """Interactive mode for testing tools."""
    print("\n\n🎯 Interactive Mode")
    print("=" * 60)
    print("Commands:")
    print("  1. get_transcript <url> [language]")
    print("  2. summarize_video <url> [length] [language]")
    print("  3. extract_key_points <url> [num_points] [language]")
    print("  4. get_video_metadata <url>")
    print("  5. list - List all tools")
    print("  6. quit - Exit")

    while True:
        try:
            user_input = input("\n> ").strip()

            if not user_input:
                continue

            if user_input.lower() == "quit":
                print("Goodbye!")
                break

            if user_input.lower() == "list":
                await list_tools(session)
                continue

            parts = user_input.split()
            command = parts[0].lower()

            if command == "get_transcript" and len(parts) >= 2:
                url = parts[1]
                language = parts[2] if len(parts) > 2 else "en"
                result = await call_tool(session, "get_transcript", {
                    "video_url": url,
                    "language": language,
                })
                print("\n📄 Result:")
                print(result[:500] + "..." if len(result) > 500 else result)

            elif command == "summarize_video" and len(parts) >= 2:
                url = parts[1]
                length = parts[2] if len(parts) > 2 else "medium"
                language = parts[3] if len(parts) > 3 else "en"
                result = await call_tool(session, "summarize_video", {
                    "video_url": url,
                    "summary_length": length,
                    "language": language,
                })
                print("\n📊 Result:")
                print(result)

            elif command == "extract_key_points" and len(parts) >= 2:
                url = parts[1]
                num_points = int(parts[2]) if len(parts) > 2 else 5
                language = parts[3] if len(parts) > 3 else "en"
                result = await call_tool(session, "extract_key_points", {
                    "video_url": url,
                    "num_points": num_points,
                    "language": language,
                })
                print("\n🎯 Result:")
                print(result)

            elif command == "get_video_metadata" and len(parts) >= 2:
                url = parts[1]
                result = await call_tool(session, "get_video_metadata", {
                    "video_url": url,
                })
                print("\n📹 Result:")
                print(result)

            else:
                print("❌ Invalid command. Type 'list' to see available tools or 'quit' to exit.")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")


async def main() -> None:
    """Main client function."""
    print("\n" + "=" * 60)
    print("  🎬 YouTube Summary MCP Client")
    print("=" * 60)

    # Setup server parameters for stdio connection
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "youtube-summary-mcp"],
    )

    # Create a session
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            try:
                # List available tools
                await list_tools(session)

                # Run examples
                if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
                    # Interactive mode
                    await interactive_mode(session)
                else:
                    # Run examples
                    print("\n\n" + "=" * 60)
                    print("Running Examples (add --interactive for interactive mode)")
                    print("=" * 60)

                    try:
                        await get_transcript_example(session)
                    except Exception as e:
                        print(f"⚠️ Example 1 skipped: {e}")

                    try:
                        await summarize_video_example(session)
                    except Exception as e:
                        print(f"⚠️ Example 2 skipped: {e}")

                    try:
                        await extract_key_points_example(session)
                    except Exception as e:
                        print(f"⚠️ Example 3 skipped: {e}")

                    try:
                        await get_metadata_example(session)
                    except Exception as e:
                        print(f"⚠️ Example 4 skipped: {e}")

                    print("\n\n" + "=" * 60)
                    print("Examples completed!")
                    print("Run with --interactive for interactive mode")
                    print("=" * 60)

            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback

                traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
