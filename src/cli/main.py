from __future__ import annotations

import argparse
import asyncio
from collections.abc import Sequence
from pathlib import Path

from core.config import AppConfig, load_config
from providers import build_provider
from runtime.agent_loop import AgentLoop
from server.app import get_health
from storage.session_store import FileSessionStore
from tools.echo import EchoTool
from tools.registry import SimpleToolRegistry


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="newbeebot")
    subparsers = parser.add_subparsers(dest="command", required=True)

    demo_parser = subparsers.add_parser("demo", help="Run the MVP smoke flow.")
    demo_parser.add_argument(
        "--message",
        required=True,
        help="User message to send to the fake loop.",
    )
    demo_parser.add_argument(
        "--data-dir",
        default=None,
        help="Override the session persistence directory.",
    )
    demo_parser.add_argument(
        "--config",
        default=None,
        help="Path to a TOML config file.",
    )

    run_parser = subparsers.add_parser("run", help="Run one turn through the standard CLI entry.")
    run_parser.add_argument(
        "--message",
        required=True,
        help="User message to send to the runtime.",
    )
    run_parser.add_argument(
        "--data-dir",
        default=None,
        help="Override the session persistence directory.",
    )
    run_parser.add_argument(
        "--config",
        default=None,
        help="Path to a TOML config file.",
    )

    chat_parser = subparsers.add_parser("chat", help="Run a minimal interactive chat session.")
    chat_parser.add_argument(
        "--data-dir",
        default=None,
        help="Override the session persistence directory.",
    )
    chat_parser.add_argument(
        "--config",
        default=None,
        help="Path to a TOML config file.",
    )

    sessions_parser = subparsers.add_parser("sessions", help="Inspect stored sessions.")
    sessions_subparsers = sessions_parser.add_subparsers(dest="sessions_command", required=True)

    sessions_list_parser = sessions_subparsers.add_parser("list", help="List known sessions.")
    sessions_list_parser.add_argument(
        "--data-dir",
        default=None,
        help="Override the session persistence directory.",
    )

    sessions_show_parser = sessions_subparsers.add_parser("show", help="Show one session history.")
    sessions_show_parser.add_argument("session_id", help="Session identifier to inspect.")
    sessions_show_parser.add_argument(
        "--data-dir",
        default=None,
        help="Override the session persistence directory.",
    )

    doctor_parser = subparsers.add_parser("doctor", help="Print runtime diagnostics.")
    doctor_parser.add_argument(
        "--config",
        default=None,
        help="Path to a TOML config file.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command in {"demo", "run"}:
        return _run_demo(args)
    if args.command == "chat":
        return _run_chat(args)
    if args.command == "sessions":
        return _run_sessions(args)
    if args.command == "doctor":
        return _run_doctor(args)

    parser.error(f"Unsupported command: {args.command}")
    return 2


def _run_demo(args: argparse.Namespace) -> int:
    config = load_config(Path(args.config) if args.config is not None else None)
    runtime = _build_runtime(config=config, data_dir_arg=args.data_dir)

    result = asyncio.run(
        runtime.run_once(
            channel=config.runtime.default_channel,
            user_text=args.message,
        )
    )

    print(f"session_id={result.session.session_id}")
    print(f"user: {args.message}")
    print(f"assistant: {result.assistant_text}")
    return 0


def _run_chat(args: argparse.Namespace) -> int:
    config = load_config(Path(args.config) if args.config is not None else None)
    runtime = _build_runtime(config=config, data_dir_arg=args.data_dir)

    session_id: str | None = None
    while True:
        user_text = input("user> ").strip()
        if user_text == "/exit":
            return 0
        if not user_text:
            continue

        if session_id is None:
            result = asyncio.run(
                runtime.run_once(channel=config.runtime.default_channel, user_text=user_text)
            )
            session_id = result.session.session_id
            print(f"session_id={session_id}")
        else:
            result = asyncio.run(
                runtime.continue_session(session_id=session_id, user_text=user_text)
            )

        print(f"assistant: {result.assistant_text}")


def _run_sessions(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir) if args.data_dir is not None else Path(".newbeebot/state")
    store = FileSessionStore(data_dir)
    if args.sessions_command == "list":
        sessions = asyncio.run(store.list_sessions())
        for session in sessions:
            print(f"{session.session_id} channel={session.channel} updated_at={session.updated_at}")
        return 0

    if args.sessions_command == "show":
        loaded_session = asyncio.run(store.get_session(args.session_id))
        if loaded_session is None:
            raise SystemExit(f"Session not found: {args.session_id}")
        print(f"session_id={loaded_session.session_id}")
        print(f"channel={loaded_session.channel}")
        for event in loaded_session.events:
            text = str(event.payload.get("text", ""))
            print(f"{event.kind}: {text}")
        return 0

    raise SystemExit(f"Unsupported sessions command: {args.sessions_command}")


def _build_runtime(*, config: AppConfig, data_dir_arg: str | None) -> AgentLoop:
    data_dir = (
        Path(data_dir_arg)
        if data_dir_arg is not None
        else Path(config.storage.base_path)
    )
    return AgentLoop(
        provider=build_provider(config.runtime.provider, config.provider),
        session_store=FileSessionStore(data_dir),
        tool_registry=SimpleToolRegistry([EchoTool()]),
    )


def _run_doctor(args: argparse.Namespace) -> int:
    config = load_config(Path(args.config) if args.config is not None else None)
    tools = SimpleToolRegistry([EchoTool()]).list_tools()
    health = get_health()
    print(f"provider={config.runtime.provider}")
    print(f"storage_base_path={config.storage.base_path}")
    print(f"tools={','.join(tool.name for tool in tools)}")
    print(f"server_status={health['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
