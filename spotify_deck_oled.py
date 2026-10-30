#!/usr/bin/env python3
"""
Spotify Deck bridge: Windows Media Session -> ESP32 -> 0.96" SSD1306 OLED.

Reads the active Windows media session using Windows.Media.Control (SMTC),
then sends plain text metadata to the ESP32 over USB serial.
"""

import argparse
import asyncio
import time
import sys
import msvcrt

import serial

try:
    from winrt.windows.media.control import (
        GlobalSystemMediaTransportControlsSessionManager as SessionManager,
        GlobalSystemMediaTransportControlsSessionPlaybackStatus as PlaybackStatus,
    )
except ImportError:
    print("Windows Media API package is missing.")
    print("Install with:")
    print("py -3.15 -m pip install winrt-Windows.Media.Control")
    raise SystemExit(1)


def seconds(value):
    """Convert WinRT TimeSpan/timedelta to whole seconds."""
    try:
        return max(0, int(value.total_seconds()))
    except Exception:
        return 0


async def read_media_session():
    """Return metadata for Spotify's Windows media session, if present."""
    try:
        manager = await SessionManager.request_async()
        sessions = list(manager.get_sessions())

        if not sessions:
            return None

        # Prefer Spotify session even if another app owns the current session.
        session = None
        for candidate in sessions:
            app_id = str(candidate.source_app_user_model_id).lower()
            if "spotify" in app_id:
                session = candidate
                break

        if session is None:
            session = manager.get_current_session()

        if session is None:
            return None

        props = await session.try_get_media_properties_async()
        playback = session.get_playback_info()
        timeline = session.get_timeline_properties()

        title = (props.title or "").strip()
        artist = (props.artist or "").strip()
        album = (props.album_title or "").strip()

        if not title:
            return None

        is_playing = playback.playback_status == PlaybackStatus.PLAYING
        position = seconds(timeline.position)
        duration = seconds(timeline.end_time - timeline.start_time)

        # Some apps do not publish a useful timeline.
        if duration <= 0:
            duration = 0

        return {
            "title": title,
            "artist": artist or "Unknown Artist",
            "album": album or "Spotify",
            "position": position,
            "duration": duration,
            "playing": is_playing,
            "app": str(session.source_app_user_model_id),
        }
    except Exception as exc:
        print(f"\n[Media API] Could not read media session: {exc}")
        return None


def send_media_key(vk):
    """Send standard Windows media key."""
    import win32api
    import win32con
    win32api.keybd_event(vk, 0, 0, 0)
    win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0)


def clean_field(value):
    return str(value).replace("\t", " ").replace("\r", " ").replace("\n", " ").strip()


def send_track(esp, info):
    line = (
        f"T:{clean_field(info['title'])}\t"
        f"{clean_field(info['artist'])}\t"
        f"{clean_field(info['album'])}\t"
        f"{info['duration']}\t{info['position']}\t"
        f"{1 if info['playing'] else 0}\t0\n"
    )
    esp.write(line.encode("utf-8", errors="replace"))
    esp.flush()


async def main_async(args, esp):
    print(f"Connected to ESP32 on {args.port} at {args.baud} baud.")
    print("Reading Windows media sessions (Spotify preferred).")
    print("Play a song in Spotify Desktop. Keep this window open.")
    print("Controls: Space=Play/Pause, n=Next, p=Previous, q=Quit")

    last_key = None
    last_sent = 0.0
    last_missing = False

    while True:
        info = await read_media_session()

        if info:
            key = (info["title"], info["artist"], info["album"], info["playing"])
            # Send on track/state changes and every second for progress refresh.
            if key != last_key or time.monotonic() - last_sent >= 1.0:
                send_track(esp, info)
                last_sent = time.monotonic()
                if key != last_key:
                    state = "PLAYING" if info["playing"] else "PAUSED"
                    print(f"\n[{state}] {info['title']} — {info['artist']} ({info['app']})")
                last_key = key
            last_missing = False
        else:
            if not last_missing:
                esp.write(b"T:Waiting for Spotify\tPlay a song in Spotify\t\t0\t0\t0\t0\n")
                esp.flush()
                print("\n[Media API] No active media metadata yet. Start a Spotify song.")
                last_missing = True
            last_key = None

        if msvcrt.kbhit():
            key = msvcrt.getwch().lower()
            if key == " ":
                send_media_key(0xB3)
            elif key == "n":
                send_media_key(0xB0)
            elif key == "p":
                send_media_key(0xB1)
            elif key == "q":
                break

        await asyncio.sleep(0.5)


def main():
    parser = argparse.ArgumentParser(description="Spotify Deck for ESP32 + SSD1306 OLED")
    parser.add_argument("--port", default="COM3", help="ESP32 COM port")
    parser.add_argument("--baud", type=int, default=115200)
    args = parser.parse_args()

    try:
        esp = serial.Serial(args.port, args.baud, timeout=0.1, write_timeout=1)
    except serial.SerialException as exc:
        print(f"Could not open {args.port}: {exc}")
        print("Close Arduino Serial Monitor and check the COM port.")
        raise SystemExit(1)

    # Opening serial may reset ESP32.
    time.sleep(2)

    try:
        asyncio.run(main_async(args, esp))
    except KeyboardInterrupt:
        print("\nStopping Spotify Deck...")
    finally:
        try:
            esp.write(b"T:Disconnected\tSpotify Deck\t\t0\t0\t0\t0\n")
            esp.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
