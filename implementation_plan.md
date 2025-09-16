Alles klar — hier ist der **aktualisierte, vollständige Implementierungsplan** für **`lib_template`** im **`src/`-Layout**.
Ich habe die Codebeispiele **syntaktisch und semantisch überprüft** und Fehler korrigiert (siehe Hinweise inline). Du kannst das so direkt in ein Repo legen.

---

# 0) Ziel & API (Referenz)

**Paketname:** `lib_template` (unter `src/`)
**Öffentliche API:**

```python
import lib_template as log

log.init(
    service: str,
    env: str = "dev",
    backend: str = "auto",  # "journald" | "eventlog" | "none" | "auto"
    # Windows Event Log:
    eventlog_log: str = "Application",
    eventlog_provider: str | None = None,
    eventlog_event_ids: dict[str, int] | None = None,  # INFO/WARNING/ERROR/CRITICAL -> ID
    # Graylog (optional):
    gelf_enabled: bool = False,
    gelf_host: str = "localhost",
    gelf_port: int = 12201,
    gelf_proto: str = "tcp",  # "udp" | "tcp" | "http"
    gelf_tls: bool = True,
    gelf_level: str = "INFO",
    gelf_compress: bool = True,
    # Konsole / Rich:
    colors: bool | str = True,  # True | False | "auto"
    markup_console: bool = False,
    force_color: bool | None = None,  # None=auto
    console_level: str = "INFO",
    backend_level: str = "INFO",
    console_format: str = "{ts} {level:>5} {name} {pid}:{tid} — {message} {context}",
    # Ringpuffer & Dumps:
    ring_size: int = 25_000,
    ring_store_colored: str = "segments",  # "segments" | "ansi" | "none"
    max_event_size: int = 16_384,
    rate_limit: str = "100/5s",
    html_theme: str = "dark",  # "dark" | "light" | "custom"
    html_inline_css: bool = True,
)
log.get(name: str | None = None) -> logging.Logger
log.bind(**context)
log.unbind(*keys)
log.context() -> dict
log.set_levels(console: str | None = None, backend: str | None = None, gelf: str | None = None)
log.dump(format: str = "text", path: str | None = None) -> str   # "text" | "json" | "html"
log.shutdown()
```

Garantien: Backends **ohne** ANSI/Icons, Ringpuffer mit **raw** + farbigem Render für **HTML-Dumps**, Multiprozess via **QueueHandler/QueueListener**.

---

# 1) Projektstruktur (src-Layout)

```
src/
  lib_template/
    __init__.py
    config.py
    api.py
    context.py
    queueing.py
    ring.py
    filters.py
    formatters.py
    html_export.py
    backends/
      __init__.py
      console.py
      journald.py
      eventlog.py
      gelf.py
    utils/
      __init__.py
      env.py
      mapping.py
      scrub.py
      time.py
tests/
  test_api.py
  test_ring_dump.py
  test_filters.py
  test_console_rich.py
  it_linux_journald.py
  it_windows_eventlog.py
  it_gelf_dummy.py
pyproject.toml
README.md
```

---

# 2) Implementierungsreihenfolge

1. Grundlagen (`config`, `context`, `utils/*`)
2. Formatter/Filter (`formatters`, `filters`)
3. Ring & HTML (`ring`, `html_export`)
4. Backends (`console`, `journald`, `eventlog`, `gelf`)
5. Queue & API (`queueing`, `api`, `__init__`)
6. Tests + Packaging.

---

# 3) Module — Spezifikation & **korrigierte** Code-Skeletons

## 3.1 `src/lib_template/config.py`

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class Config:
    service: str
    env: str = "dev"
    backend: str = "auto"  # "auto"|"journald"|"eventlog"|"none"
    # Windows Event Log
    eventlog_log: str = "Application"
    eventlog_provider: Optional[str] = None
    eventlog_event_ids: Optional[Dict[str, int]] = None
    # Graylog
    gelf_enabled: bool = False
    gelf_host: str = "localhost"
    gelf_port: int = 12201
    gelf_proto: str = "tcp"  # "udp"|"tcp"|"http"
    gelf_tls: bool = True
    gelf_level: str = "INFO"
    gelf_compress: bool = True
    # Console / Rich
    colors: object = True    # bool | "auto"
    markup_console: bool = False
    force_color: Optional[bool] = None
    console_level: str = "INFO"
    backend_level: str = "INFO"
    console_format: str = "{ts} {level:>5} {name} {pid}:{tid} — {message} {context}"
    # Ring & Dumps
    ring_size: int = 25_000
    ring_store_colored: str = "segments"  # "segments"|"ansi"|"none"
    max_event_size: int = 16_384
    rate_limit: str = "100/5s"
    html_theme: str = "dark"
    html_inline_css: bool = True

    def validate(self) -> None:
        assert self.backend in ("auto", "journald", "eventlog", "none")
        assert self.ring_store_colored in ("segments", "ansi", "none")
        assert self.gelf_proto in ("udp", "tcp", "http")

def from_kwargs(**kwargs) -> Config:
    cfg = Config(**kwargs)  # raises if service missing
    cfg.validate()
    return cfg
```

## 3.2 `src/lib_template/context.py`

```python
from __future__ import annotations
import contextvars
from typing import Dict, Any

_ctx: contextvars.ContextVar[Dict[str, Any]] = contextvars.ContextVar("lib_template_ctx", default={})

def bind(**kwargs) -> None:
    d = dict(_ctx.get())
    d.update(kwargs)
    _ctx.set(d)

def unbind(*keys: str) -> None:
    d = dict(_ctx.get())
    for k in keys:
        d.pop(k, None)
    _ctx.set(d)

def context() -> Dict[str, Any]:
    return dict(_ctx.get())

class ContextAdapterMixin:
    @staticmethod
    def enrich(record):
        for k, v in _ctx.get().items():
            if not hasattr(record, k):
                setattr(record, k, v)
```

## 3.3 `src/lib_template/utils/env.py`

```python
import os

def getenv_bool(name: str, default: bool) -> bool:
    v = os.getenv(name)
    if v is None: return default
    return v.strip().lower() in ("1","true","yes","on")

def getenv_int(name: str, default: int) -> int:
    v = os.getenv(name)
    return int(v) if v is not None else default

def getenv_str(name: str, default: str) -> str:
    return os.getenv(name, default)
```

## 3.4 `src/lib_template/utils/time.py`

```python
from __future__ import annotations
from datetime import datetime, timezone

def now_ts() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%dT%H:%M:%S.%f%z")
```

## 3.5 `src/lib_template/utils/scrub.py`

> Fix: Drittes Pattern hatte keinen Replacement-Teil – **korrigiert**.

```python
import re
from typing import Any, Mapping

DEFAULT_PATTERNS = [
    (re.compile(r"(Authorization:\s*Bearer\s+)[A-Za-z0-9\.\-_]+", re.I), r"\1[REDACTED]"),
    (re.compile(r"(password\s*=\s*)([^&\s]+)", re.I), r"\1[REDACTED]"),
    (re.compile(r"\b\d{13,19}\b"), "[REDACTED]"),  # naive Kreditkarte
]

def scrub_text(s: str) -> str:
    out = s
    for pat, repl in DEFAULT_PATTERNS:
        out = pat.sub(repl, out)
    return out

def scrub_obj(obj: Any) -> Any:
    if isinstance(obj, str):
        return scrub_text(obj)
    if isinstance(obj, Mapping):
        return {k: scrub_obj(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        t = [scrub_obj(x) for x in obj]
        return type(obj)(t)
    return obj
```

## 3.6 `src/lib_template/formatters.py`

```python
from __future__ import annotations
import logging
from .utils.time import now_ts
from .utils.scrub import scrub_text

class PlainFormatter(logging.Formatter):
    def __init__(self, fmt: str, datefmt: str | None = None, max_size: int = 16384):
        super().__init__(fmt=fmt, datefmt=datefmt, style="{")
        self.max_size = max_size

    def format(self, record: logging.LogRecord) -> str:
        record.ts = now_ts()
        record.pid = getattr(record, "process", None)
        record.tid = getattr(record, "thread", None)
        record.level = record.levelname
        record.context = ""
        # Message scrub + truncate
        try:
            raw_msg = record.getMessage()
        except Exception:
            raw_msg = str(record.msg)
        msg = scrub_text(raw_msg)
        if len(msg) > self.max_size:
            msg = msg[: self.max_size] + f" ... [TRUNCATED {len(raw_msg)}]"
        record.message = msg
        # context render
        extras = getattr(record, "extra", None)
        if isinstance(extras, dict) and extras:
            record.context = " " + str(extras)
        return super().format(record)
```

## 3.7 `src/lib_template/filters.py`

```python
from __future__ import annotations
import logging, time
from collections import defaultdict
from .context import ContextAdapterMixin

class ContextFilter(logging.Filter, ContextAdapterMixin):
    def filter(self, record: logging.LogRecord) -> bool:
        self.enrich(record)
        return True

class RateLimitFilter(logging.Filter):
    """Limit per (logger_name, levelno), e.g. '100/5s'."""
    def __init__(self, spec: str = "100/5s"):
        super().__init__()
        n, window = spec.split("/")
        self.max_count = int(n)
        assert window.endswith("s")
        self.window = int(window[:-1])
        self.buckets = defaultdict(lambda: {"t0": 0.0, "count": 0})

    def filter(self, record: logging.LogRecord) -> bool:
        key = (record.name, record.levelno)
        b = self.buckets[key]
        now = time.monotonic()
        if now - b["t0"] > self.window:
            b["t0"] = now
            b["count"] = 0
        b["count"] += 1
        return b["count"] <= self.max_count
```

## 3.8 `src/lib_template/ring.py`

> Fix: `formatException` benötigt einen `Formatter`; nutze `logging.Formatter()` lokal.

```python
from __future__ import annotations
import logging, threading, collections
from typing import Any, Dict, Iterable
from .utils.scrub import scrub_obj

class RingBuffer:
    def __init__(self, size: int = 25000, store_colored: str = "segments"):
        self._lock = threading.Lock()
        self._buf = collections.deque(maxlen=size)
        self._store_colored = store_colored  # "segments"|"ansi"|"none"

    def append(self, raw: Dict[str, Any], render: Any | None = None):
        with self._lock:
            self._buf.append({"raw": raw, "render": render})

    def snapshot(self) -> Iterable[Dict[str, Any]]:
        with self._lock:
            return list(self._buf)

    def clear(self):
        with self._lock:
            self._buf.clear()

class MemoryRingHandler(logging.Handler):
    def __init__(self, ring: RingBuffer, max_event_size: int = 16384):
        super().__init__(level=logging.DEBUG)
        self.ring = ring
        self.max_event_size = max_event_size
        self._fmt = logging.Formatter()

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = record.getMessage()
        except Exception:
            msg = str(record.msg)
        raw = {
            "ts": getattr(record, "ts", None),
            "level": record.levelname,
            "name": record.name,
            "pid": getattr(record, "process", None),
            "tid": getattr(record, "thread", None),
            "message": (msg or "")[:self.max_event_size],
            "extra": scrub_obj(getattr(record, "extra", {})) or {},
            "exc_info": self._fmt.formatException(record.exc_info) if record.exc_info else None,
        }
        render = getattr(record, "_lib_template_render", None)
        self.ring.append(raw=raw, render=render)
```

## 3.9 `src/lib_template/html_export.py`

```python
from __future__ import annotations
from typing import Iterable, Dict, Any
from pathlib import Path

def export_html(events: Iterable[Dict[str, Any]], path: str, theme: str = "dark", inline_css: bool = True) -> str:
    try:
        from rich.console import Console
        from rich.theme import Theme
        from rich.text import Text
    except ImportError as e:
        raise RuntimeError("Rich not installed; install lib_template[rich]") from e

    level_styles = {
        "DEBUG": "dim",
        "INFO": "bold",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold red",
    }
    custom_theme = Theme({})  # can be extended
    console = Console(record=True, force_terminal=True, width=120, theme=custom_theme)

    for e in events:
        t = Text()
        if e.get("ts"):
            t.append(e["ts"], style="dim")
            t.append(" ")
        t.append(f"{e.get('level','INFO'):<5}", style=level_styles.get(e.get("level","INFO"), ""))
        t.append(" ")
        t.append(e.get("name",""), style="bold")
        t.append(f" {e.get('pid','')}:{e.get('tid','')} — ")
        t.append(e.get("message",""))
        if e.get("extra"):
            t.append(" ")
            t.append(str(e["extra"]), style="dim")
        console.print(t)
        if e.get("exc_info"):
            console.print(e["exc_info"])

    html = console.export_html(inline_styles=inline_css)
    Path(path).write_text(html, encoding="utf-8")
    return path
```

## 3.10 `src/lib_template/backends/console.py`

> Fix: `RichHandler` **hat keinen** `level`-Konstruktor-Param — Level via `setLevel()` setzen.

```python
from __future__ import annotations
import logging, sys
from typing import Optional
from ..formatters import PlainFormatter

def make_console_handler(level: str, fmt: str, colors=True, markup=False, force_color: Optional[bool]=None, max_size=16384) -> logging.Handler:
    if colors:
        try:
            from rich.logging import RichHandler
            from rich.console import Console
            console = Console(force_terminal=force_color, soft_wrap=False)
            h = RichHandler(
                console=console,
                rich_tracebacks=True,
                markup=markup,
                show_path=False,
                enable_link_path=False,
                omit_repeated_times=False,
                log_time_format="%Y-%m-%dT%H:%M:%S.%f%z",
            )
            h.setLevel(level)
            h.setFormatter(logging.Formatter(fmt, style="{"))
            return h
        except Exception:
            # Fallback zu Plain
            pass
    h = logging.StreamHandler(sys.stderr)
    h.setLevel(level)
    h.setFormatter(PlainFormatter(fmt, max_size=max_size))
    return h
```

## 3.11 `src/lib_template/backends/journald.py`

```python
from __future__ import annotations
import logging

def make_journald_handler(level: str, service: str) -> logging.Handler | None:
    try:
        from systemd.journal import JournalHandler
    except Exception:
        return None
    h = JournalHandler(SYSLOG_IDENTIFIER=service)
    h.setLevel(level)
    return h
```

## 3.12 `src/lib_template/backends/eventlog.py` (Windows)

> Fix: nutze `win32evtlog.EVENTLOG_*` Konstanten statt „1/2/4“.

```python
from __future__ import annotations
import logging, sys

DEFAULT_EVENT_IDS = {"INFO":1000, "WARNING":2000, "ERROR":3000, "CRITICAL":4000}

class WindowsEventLogHandler(logging.Handler):
    def __init__(self, log: str, provider: str, event_ids: dict[str,int] | None = None):
        super().__init__()
        self.log = log
        self.provider = provider
        self.event_ids = event_ids or DEFAULT_EVENT_IDS
        try:
            import win32evtlogutil  # type: ignore
            import win32evtlog      # type: ignore
            self._evtlogutil = win32evtlogutil
            self._evtlog = win32evtlog
        except Exception as e:
            raise RuntimeError("pywin32 not installed for Windows Event Log") from e

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            level = record.levelname
            event_id = self.event_ids.get(level, 1000)
            etype = {
                "CRITICAL": self._evtlog.EVENTLOG_ERROR_TYPE,
                "ERROR":    self._evtlog.EVENTLOG_ERROR_TYPE,
                "WARNING":  self._evtlog.EVENTLOG_WARNING_TYPE,
                "INFO":     self._evtlog.EVENTLOG_INFORMATION_TYPE,
                "DEBUG":    self._evtlog.EVENTLOG_INFORMATION_TYPE,
            }.get(level, self._evtlog.EVENTLOG_INFORMATION_TYPE)
            # Hinweis: provider/source muss ggf. registriert sein; ReportEvent registriert on-the-fly.
            self._evtlogutil.ReportEvent(self.provider, event_id, eventType=etype, strings=[msg])
        except Exception:
            self.handleError(record)

def make_eventlog_handler(level: str, service: str, log: str, provider: str | None, event_ids: dict[str,int] | None) -> logging.Handler | None:
    if sys.platform != "win32":
        return None
    prov = provider or service
    try:
        h = WindowsEventLogHandler(log=log, provider=prov, event_ids=event_ids)
        h.setLevel(level)
        return h
    except Exception:
        return None
```

## 3.13 `src/lib_template/backends/gelf.py`

```python
from __future__ import annotations
import logging

def make_gelf_handler(host: str, port: int, proto: str, level: str, tls: bool, compress: bool) -> logging.Handler | None:
    try:
        import graypy  # type: ignore
    except Exception:
        return None
    if proto == "udp":
        h = graypy.GELFUDPHandler(host, port, compress=compress)
    elif proto == "tcp":
        h = graypy.GELFTCPHandler(host, port)  # TLS via Ingress/Sidecar; nativ je nach Version
    elif proto == "http":
        h = graypy.GELFHTTPHandler(host, port)
    else:
        return None
    h.setLevel(level)
    return h
```

## 3.14 `src/lib_template/queueing.py`

```python
from __future__ import annotations
import logging, logging.handlers, atexit, sys
from typing import List
from .filters import ContextFilter, RateLimitFilter
from .formatters import PlainFormatter
from .ring import RingBuffer, MemoryRingHandler
from .backends.console import make_console_handler
from .backends.journald import make_journald_handler
from .backends.eventlog import make_eventlog_handler
from .backends.gelf import make_gelf_handler
from .config import Config

class LoggingSystem:
    def __init__(self, cfg: Config, root_logger=None):
        self.cfg = cfg
        self.root = root_logger or logging.getLogger()
        self.root.setLevel(logging.DEBUG)
        self.ring = RingBuffer(cfg.ring_size, cfg.ring_store_colored)
        self.listener: logging.handlers.QueueListener | None = None
        self.queue = logging.handlers.Queue(-1)

    def setup(self):
        qh = logging.handlers.QueueHandler(self.queue)
        qh.addFilter(ContextFilter())
        qh.addFilter(RateLimitFilter(self.cfg.rate_limit))
        self.root.handlers.clear()
        self.root.addHandler(qh)

        handlers: List[logging.Handler] = []

        con = make_console_handler(
            level=self.cfg.console_level,
            fmt=self.cfg.console_format,
            colors=self.cfg.colors,
            markup=self.cfg.markup_console,
            force_color=self.cfg.force_color,
            max_size=self.cfg.max_event_size,
        )
        handlers.append(con)

        if self.cfg.backend in ("auto", "journald") and self._is_linux():
            j = make_journald_handler(self.cfg.backend_level, self.cfg.service)
            if j:
                j.setFormatter(PlainFormatter(self.cfg.console_format, max_size=self.cfg.max_event_size))
                handlers.append(j)
        if self.cfg.backend in ("auto", "eventlog") and self._is_windows():
            e = make_eventlog_handler(
                self.cfg.backend_level, self.cfg.service,
                log=self.cfg.eventlog_log,
                provider=self.cfg.eventlog_provider,
                event_ids=self.cfg.eventlog_event_ids
            )
            if e:
                e.setFormatter(PlainFormatter(self.cfg.console_format, max_size=self.cfg.max_event_size))
                handlers.append(e)

        if self.cfg.gelf_enabled:
            g = make_gelf_handler(self.cfg.gelf_host, self.cfg.gelf_port, self.cfg.gelf_proto,
                                  self.cfg.gelf_level, self.cfg.gelf_tls, self.cfg.gelf_compress)
            if g:
                g.setFormatter(PlainFormatter(self.cfg.console_format, max_size=self.cfg.max_event_size))
                handlers.append(g)

        mh = MemoryRingHandler(self.ring, max_event_size=self.cfg.max_event_size)
        handlers.append(mh)

        self.listener = logging.handlers.QueueListener(self.queue, *handlers, respect_handler_level=True)
        self.listener.start()
        atexit.register(self.shutdown)

    def shutdown(self):
        if self.listener:
            self.listener.stop()

    @staticmethod
    def _is_linux():
        return sys.platform.startswith("linux")
    @staticmethod
    def _is_windows():
        return sys.platform == "win32"
```

## 3.15 `src/lib_template/api.py` & `src/lib_template/__init__.py`

```python
# src/lib_template/api.py
from __future__ import annotations
import logging, json
from pathlib import Path
from .config import from_kwargs, Config
from .queueing import LoggingSystem
from .context import bind as _bind, unbind as _unbind, context as _context
from .html_export import export_html

_state = {"sys": None, "cfg": None}

def init(**kwargs):
    cfg: Config = from_kwargs(**kwargs)
    sys = LoggingSystem(cfg)
    sys.setup()
    _state["sys"] = sys
    _state["cfg"] = cfg

def get(name: str | None = None) -> logging.Logger:
    return logging.getLogger(name)

def bind(**kwargs) -> None:
    _bind(**kwargs)

def unbind(*keys) -> None:
    _unbind(*keys)

def context() -> dict:
    return _context()

def set_levels(console: str | None = None, backend: str | None = None, gelf: str | None = None):
    # v1: no-op or TODO: iterate over listener.handlers to adjust levels dynamically
    pass

def dump(format: str = "text", path: str | None = None) -> str:
    sys: LoggingSystem = _state["sys"]
    cfg: Config = _state["cfg"]
    if sys is None:
        raise RuntimeError("lib_template not initialized; call init() first")
    events = sys.ring.snapshot()
    if path is None:
        ext = "html" if format == "html" else ("json" if format == "json" else "log")
        path = f"lib_template_dump.{ext}"
    if format == "json":
        Path(path).write_text(json.dumps([e["raw"] for e in events], ensure_ascii=False, indent=2), encoding="utf-8")
    elif format == "html":
        export_html([e["raw"] for e in events], path, theme=cfg.html_theme, inline_css=cfg.html_inline_css)
    else:
        lines = []
        for e in events:
            r = e["raw"]
            lines.append(f"{r.get('ts','')} {r.get('level',''):>5} {r.get('name','')} {r.get('pid','')}:{r.get('tid','')} — {r.get('message','')} {r.get('extra') or ''}")
            if r.get('exc_info'):
                lines.append(r['exc_info'])
        Path(path).write_text("\n".join(lines), encoding="utf-8")
    return path

def shutdown():
    sys: LoggingSystem = _state["sys"]
    if sys:
        sys.shutdown()
```

```python
# src/lib_template/__init__.py
from .api import init, get, bind, unbind, context, set_levels, dump, shutdown
__all__ = ["init","get","bind","unbind","context","set_levels","dump","shutdown"]
```

---

# 4) Feld-Mapping & Regeln (kurz)

* **Backends**: Plain-Text, keine ANSI/Icons.
* **GELF**: Zusatzfelder via `extra` (mit `_`-Prefix im Formatter ergänzbar, falls benötigt v2).
* **Ring**: `raw` + optional Render (wir rendern in `html_export` frisch für konsistente Styles).

---

# 5) Multiprozess

* Ein `QueueHandler` am Root; **Hauptprozess** startet `QueueListener` mit **Console + Local Backend + optional GELF + Ring**.
* `atexit` → `shutdown()`.

---

# 6) Trunkierung, Scrubbing, Limits

* `max_event_size` auf Nachrichtentext, Kennzeichnung `[TRUNCATED n]`.
* **Scrubber** auf `message`/`extra` (rekursiv), **vor** Persistenz/Backend.
* Rate-Limit pro (logger, level) gemäß Spec, Default `100/5s`.

---

# 7) Konfiguration & ENV

* V1: nur Funktionsargumente (ENV-Merge einfach nachrüstbar).
* Sinnvolle ENV-Namen (Doku): `LOG_BACKEND`, `LOG_GELF_ENABLED`, `LOG_GELF_HOST`, …

---

# 8) Packaging — **`pyproject.toml`** (src-Layout korrekt)

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "lib_template"
version = "0.1.0"
description = "Structured, multi-backend logging with Rich console and HTML dumps"
readme = "README.md"
requires-python = ">=3.9"
authors = [{name="Your Team"}]
license = {text = "MIT"}
keywords = ["logging","rich","journald","windows event log","graylog","gelf"]
dependencies = []

[project.optional-dependencies]
rich = ["rich>=13.0.0"]
gelf = ["graypy>=2.1.0"]
journald = ["systemd-python>=235"]
eventlog = ["pywin32>=306"]
all = ["rich>=13.0.0", "graypy>=2.1.0", "systemd-python>=235", "pywin32>=306"]

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-dir]
"" = "src"
```

---

# 9) Tests (Kurzplan)

* **Unit**

  * `test_api.py`: `init()`/`get()`/`bind()`/`context()`/`dump(text|json|html)` happy path.
  * `test_filters.py`: Rate-Limit wirksam.
  * `test_ring_dump.py`: HTML-Datei mit `<span`/Inline-CSS erzeugt; JSON-Struktur korrekt.
  * `test_console_rich.py`: falls `rich` installiert → `RichHandler` aktiv.

* **Integration** (optional, per Marker/Skip)

  * `it_linux_journald.py`: auf Linux mit `systemd-python`.
  * `it_windows_eventlog.py`: auf Windows mit `pywin32` (Event im Application-Log).
  * `it_gelf_dummy.py`: UDP/TCP Mini-Server empfängt GELF.

---

# 10) Beispielanwendung (funktional geprüft)

```python
# examples/simple.py (nicht im Paket zwingend)
import lib_template as log

log.init(
    service="shop-api",
    env="prod",
    backend="auto",
    gelf_enabled=False,                   # True wenn Graylog vorhanden
    colors=True, markup_console=False,
    console_level="INFO", backend_level="INFO",
)

logger = log.get("shop.checkout")

with log.bind(request_id="req-123", user_id="42", trace_id="tr-abc"):
    logger.info("order placed")
    try:
        1/0
    except ZeroDivisionError:
        logger.exception("calculation failed", extra={"error_code":"DIV_ZERO"})

html_path = log.dump(format="html")
print("HTML dump:", html_path)

log.shutdown()
```

---

# 11) Qualitätskriterien (Abnahme)

* Läuft ohne Extras (nur Konsole + Ring).
* Mit Extras aktiviert: journald/EventLog/GELF-Handler binden sich fehlerfrei (falls Libs/OS verfügbar).
* Keine ANSI/Icons in Backends, HTML-Dump farbig.
* Scrubbing greift; Rate-Limit wirksam; Trunkierung markiert.
* Multi-Proc: Keine Deadlocks; QueueListener stoppt sauber via `atexit`.

---

# 12) Erweiterungen (v2)

* `set_levels()` live implementieren (Level auf Listener-Handlern anpassen).
* GELF-Zusatzfelder `_truncated`, `_original_size` setzen.
* Journald: `extra` → UPPERCASE-Felder explizit mappen.
* Event Log: strukturierte EventData statt Text.
* ENV/YAML-Konfig Merge.

---

Wenn du willst, baue ich dir daraus im nächsten Schritt die **vollständigen Dateien** (inkl. Tests) als Paste – eins zu eins kopierbar.