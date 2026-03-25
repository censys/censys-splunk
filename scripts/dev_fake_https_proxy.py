#!/usr/bin/env python3
"""Tiny HTTP forward proxy for local testing (CONNECT tunneling).

``requests`` to ``https://`` sends::

    CONNECT host:443 HTTP/1.1

We connect to ``host:port``, reply ``200 Connection established``, then relay
raw bytes both ways so TLS passes through to the real server (e.g. Censys).

Usage::

    python3 scripts/dev_fake_https_proxy.py           # default 127.0.0.1:8899
    python3 scripts/dev_fake_https_proxy.py 9999

Optional: only log and return 502 (no upstream)::

    python3 scripts/dev_fake_https_proxy.py --stub-502

In the Censys add-on **Configuration → Proxy**, enable proxy; host ``127.0.0.1``,
port ``8899`` (or your chosen port), type ``http``.
"""
import socket
import sys
import threading
from typing import Optional, Tuple


def _parse_connect_target(first_line: bytes) -> Optional[Tuple[str, int]]:
    # CONNECT app.censys.io:443 HTTP/1.1
    parts = first_line.split()
    if len(parts) < 2:
        return None
    target = parts[1].decode("utf-8", errors="replace")
    if ":" in target:
        host, port_s = target.rsplit(":", 1)
        try:
            return host, int(port_s)
        except ValueError:
            return None
    return target, 443


def _pipe(src: socket.socket, dst: socket.socket) -> None:
    try:
        while True:
            data = src.recv(65536)
            if not data:
                break
            dst.sendall(data)
    except OSError:
        pass
    try:
        dst.shutdown(socket.SHUT_WR)
    except OSError:
        pass


def _handle(client: socket.socket, addr: tuple, stub_502: bool) -> None:
    remote: Optional[socket.socket] = None
    try:
        buf = b""
        while b"\r\n\r\n" not in buf and len(buf) < 65536:
            chunk = client.recv(8192)
            if not chunk:
                return
            buf += chunk

        first_line = buf.split(b"\r\n", 1)[0]
        print(f"{addr[0]}:{addr[1]} {first_line.decode('utf-8', errors='replace')}", flush=True)

        if not first_line.upper().startswith(b"CONNECT"):
            client.sendall(
                b"HTTP/1.1 501 Not Implemented\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"
            )
            return

        if stub_502:
            client.sendall(
                b"HTTP/1.1 502 Bad Gateway\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"
            )
            return

        parsed = _parse_connect_target(first_line)
        if not parsed:
            client.sendall(
                b"HTTP/1.1 400 Bad Request\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"
            )
            return

        host, port = parsed
        try:
            remote = socket.create_connection((host, port), timeout=60)
        except OSError as e:
            print(f"  upstream connect failed {host}:{port} ({e})", flush=True)
            client.sendall(
                b"HTTP/1.1 502 Bad Gateway\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"
            )
            return

        client.sendall(b"HTTP/1.1 200 Connection established\r\n\r\n")

        header_end = buf.index(b"\r\n\r\n") + 4
        extra = buf[header_end:]
        if extra:
            remote.sendall(extra)

        t1 = threading.Thread(target=_pipe, args=(client, remote), daemon=True)
        t2 = threading.Thread(target=_pipe, args=(remote, client), daemon=True)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
    finally:
        try:
            client.close()
        except OSError:
            pass
        if remote is not None:
            try:
                remote.close()
            except OSError:
                pass


def main() -> None:
    args = [a for a in sys.argv[1:] if a]
    stub_502 = False
    if "--stub-502" in args:
        stub_502 = True
        args = [a for a in args if a != "--stub-502"]
    port = int(args[0]) if args else 8899
    host = "127.0.0.1"
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(32)
    mode = "CONNECT → tunnel to upstream" if not stub_502 else "CONNECT → 502 only"
    print(f"dev HTTPS proxy on http://{host}:{port} ({mode})", flush=True)
    while True:
        conn, addr = sock.accept()
        threading.Thread(
            target=_handle, args=(conn, addr, stub_502), daemon=True
        ).start()


if __name__ == "__main__":
    main()
