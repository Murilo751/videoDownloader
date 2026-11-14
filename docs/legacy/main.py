import argparse
import os
import shutil
import sys
import time
from pathlib import Path


BANNER = r"""
       _     _           ____                      _                 _
__   _(_) __| | ___  ___|  _ \  _____      ___ __ | | ___   __ _  __| | ___ _ __
\ \ / / |/ _` |/ _ \/ _ \ | | |/ _ \ \ /\ / / '_ \| |/ _ \ / _` |/ _` |/ _ \ '__|
 \ V /| | (_| |  __/ (_) | |_| | (_) \ V  V /| | | | | (_) | (_| | (_| |  __/ |
  \_/ |_|\__,_|\___|\___/|____/ \___/ \_/\_/ |_| |_|_|\___/ \__,_|\__,_|\___|_|
"""


def terminal_colors() -> bool:
    """Usa ANSI apenas quando a saída aceita cores e o usuário não as desativou."""
    if not sys.stdout.isatty() or "NO_COLOR" in os.environ:
        return False
    if os.name != "nt":
        return True
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_uint()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        return bool(kernel32.SetConsoleMode(handle, mode.value | 0x0004))
    except (AttributeError, OSError):
        return False


def paint(value: str, code: str, colors: bool) -> str:
    return f"\x1b[{code}m{value}\x1b[0m" if colors else value


def show_banner(colors: bool) -> None:
    """Revela o ASCII art em terminais interativos, sem atrasar saídas redirecionadas."""
    lines = BANNER.strip("\n").splitlines()
    border = "-" * max(map(len, lines))
    animate = sys.stdout.isatty() and shutil.get_terminal_size((120, 25)).columns >= len(border) + 2
    print(paint("+" + border + "+", "2;36", colors))
    for number, line in enumerate(lines):
        shade = "1;36" if number % 2 == 0 else "1;35"
        if animate:
            for end in range(8, len(line) + 8, 8):
                print("\r" + paint(line[:end], shade, colors), end="", flush=True)
                time.sleep(0.008)
            print()
        else:
            print(paint(line, shade, colors))
    print(paint("+" + border + "+", "2;36", colors))


FORMAT = (
    "bv[height=1080][vcodec^=avc1][protocol^=m3u8]+ba[ext=m4a]/"
    "bv[height=1080][vcodec^=avc1][protocol=https]+ba[ext=m4a]/"
    "bv[height=1080][ext=mp4]+ba[ext=m4a]/"
    "bv[height<=1080][vcodec^=avc1][protocol^=m3u8]+ba[ext=m4a]/"
    "bv[height<=1080][vcodec^=avc1][protocol=https]+ba[ext=m4a]/"
    "bv[height<=1080][ext=mp4]+ba[ext=m4a]/"
    "b[height<=1080][ext=mp4]"
)


def format_for_height(height: int) -> str:
    """Seleciona a resolução exata em MP4, priorizando HLS/H.264."""
    return (
        f"bv[height={height}][vcodec^=avc1][protocol^=m3u8]+ba[ext=m4a]/"
        f"bv[height={height}][vcodec^=avc1][protocol=https]+ba[ext=m4a]/"
        f"bv[height={height}][ext=mp4]+ba[ext=m4a]/"
        f"b[height={height}][ext=mp4]"
    )


def downloads_folder() -> Path:
    """Usa a pasta Downloads configurada no Windows, inclusive se redirecionada."""
    if os.name == "nt":
        try:
            import winreg

            key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
            downloads_id = "{374DE290-123F-4565-9164-39C4925E467B}"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                value, _ = winreg.QueryValueEx(key, downloads_id)
            return Path(os.path.expandvars(value))
        except OSError:
            pass
    return Path.home() / "Downloads"


def node_runtime() -> dict:
    """Aponta para o Node incluído no executável, quando empacotado."""
    if getattr(sys, "frozen", False):
        bundled_node = Path(sys._MEIPASS) / "node.exe"
        if not bundled_node.is_file():
            raise RuntimeError("Node.js não foi incluído no executável")
        return {"node": {"path": str(bundled_node)}}
    local_node = Path(__file__).resolve().parent / ".tools" / "node-v24.22.1" / "node.exe"
    if local_node.is_file():
        return {"node": {"path": str(local_node)}}
    return {"deno": {}, "node": {}}


def available_resolutions(url: str) -> list[int]:
    import yt_dlp

    with yt_dlp.YoutubeDL(
        {"js_runtimes": node_runtime(), "noplaylist": True, "quiet": True}
    ) as downloader:
        info = downloader.extract_info(url, download=False)
    formats = info.get("formats") or []
    has_m4a = any(
        item.get("vcodec") == "none"
        and item.get("acodec") != "none"
        and item.get("ext") == "m4a"
        for item in formats
    )
    heights = sorted(
        {
            item["height"]
            for item in formats
            if isinstance(item.get("height"), int)
            and item.get("ext") == "mp4"
            and item.get("vcodec") not in (None, "none")
            and (has_m4a or item.get("acodec") not in (None, "none"))
        }
    )
    if not heights:
        raise RuntimeError("Não há resoluções MP4 com áudio para este vídeo.")
    return heights


def choose_resolution(heights: list[int], colors: bool = False) -> int | None:
    """Mostra um seletor entre Mín. e Máx. controlado pelas setas."""
    if len(heights) == 1:
        print(paint(f"Única resolução disponível: {heights[0]}p", "1;32", colors))
        return heights[0]

    print(paint("Use as setas esquerda/direita (ou A/D), Enter confirma e Esc cancela.", "2", colors))
    index = len(heights) - 1

    def line() -> tuple[str, str]:
        marker = round(index * 24 / (len(heights) - 1))
        bar = "-" * marker + "O" + "-" * (24 - marker)
        left = f"MÍN {heights[0]}p ["
        right = f"] MÁX {heights[-1]}p  Escolhida: "
        chosen = f"{heights[index]}p"
        plain = left + bar + right + chosen
        styled = (
            paint(left, "2", colors)
            + paint(bar[:marker], "36", colors)
            + paint("O", "1;35", colors)
            + paint(bar[marker + 1 :], "2", colors)
            + paint(right, "2", colors)
            + paint(chosen, "1;32", colors)
        )
        return plain, styled

    if os.name == "nt" and sys.stdin.isatty():
        import msvcrt

        previous_length = 0
        while True:
            plain, styled = line()
            print("\r" + styled + " " * max(0, previous_length - len(plain)), end="", flush=True)
            previous_length = len(plain)
            key = msvcrt.getwch()
            if key in ("\r", "\n"):
                print()
                return heights[index]
            if key == "\x1b":
                print()
                return None
            if key in ("\x00", "\xe0"):
                arrow = msvcrt.getwch()
                if arrow in ("K", "H"):
                    index = max(0, index - 1)
                elif arrow in ("M", "P"):
                    index = min(len(heights) - 1, index + 1)
            elif key.lower() == "a":
                index = max(0, index - 1)
            elif key.lower() == "d":
                index = min(len(heights) - 1, index + 1)

    print(line()[1])
    print("Opções:", ", ".join(paint(f"{i + 1}: {height}p", "1;36", colors) for i, height in enumerate(heights)))
    try:
        answer = input(paint("Número da resolução (Enter = Máx.): ", "1;35", colors)).strip()
    except EOFError:
        return heights[-1]
    if not answer:
        return heights[-1]
    if answer.isdecimal() and 1 <= int(answer) <= len(heights):
        return heights[int(answer) - 1]
    print(paint("Escolha inválida.", "1;31", colors))
    return None


def download_video(
    url: str, destination: Path, verify: bool = False, height: int | None = None
) -> int:
    try:
        import imageio_ffmpeg
        import yt_dlp
        from yt_dlp.utils import DownloadError
    except ImportError:
        print(
            "Dependências ausentes. Instale com: python -m pip install -r requirements.txt",
            file=sys.stderr,
        )
        return 1

    try:
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        if not verify:
            destination.mkdir(parents=True, exist_ok=True)
        options = {
            "format": format_for_height(height) if height else FORMAT,
            "external_downloader": {"m3u8": "ffmpeg"},
            "ffmpeg_location": ffmpeg,
            "js_runtimes": node_runtime(),
            "merge_output_format": "mp4",
            "noplaylist": True,
            "outtmpl": str(destination / "%(title)s [%(id)s].%(ext)s"),
        }
        with yt_dlp.YoutubeDL(options) as downloader:
            if verify:
                info = downloader.extract_info(url, download=False)
                formats = info.get("requested_formats") or [info]
                video = next((item for item in formats if item.get("vcodec") != "none"), None)
                audio = next((item for item in formats if item.get("acodec") != "none"), None)
                if not video or not audio:
                    raise RuntimeError("não foi encontrado vídeo MP4 com áudio")
                print(
                    f"Disponível: {video.get('width')}x{video.get('height')} "
                    f"com áudio. Formatos: {info.get('format_id')}."
                )
                return 0
            print(f"Destino: {destination.resolve()}", flush=True)
            result = downloader.download([url])
        if result:
            return 1
    except (DownloadError, OSError, RuntimeError) as exc:
        print(f"Não foi possível baixar o vídeo: {exc}", file=sys.stderr)
        if "HTTP Error 403" in str(exc):
            print(
                "O YouTube recusou a transferência. Tente novamente mais tarde "
                "e atualize o yt-dlp se o erro persistir.",
                file=sys.stderr,
            )
        return 1

    print("Download concluído em MP4.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Baixa vídeos do YouTube em MP4 (até 1080p) na pasta Downloads."
    )
    parser.add_argument("url", nargs="?", help="link do vídeo; se omitido, pede no console")
    parser.add_argument(
        "--saida",
        type=Path,
        default=downloads_folder(),
        help="pasta de destino (padrão: Downloads do Windows)",
    )
    parser.add_argument(
        "--verificar",
        action="store_true",
        help="consulta os formatos disponíveis sem baixar o arquivo",
    )
    args = parser.parse_args()

    if args.url:
        return download_video(args.url, args.saida, args.verificar)

    colors = terminal_colors()
    show_banner(colors)
    print(paint("videoDownloader", "1;35", colors) + " | vídeos em MP4")
    print(paint("Destino  ", "2", colors) + str(args.saida.resolve()))
    while True:
        try:
            url = input("\n" + paint("> Cole o link do vídeo (Enter para sair): ", "1;36", colors)).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not url:
            return 0
        try:
            heights = available_resolutions(url)
            print(paint("Resoluções disponíveis: ", "2", colors) + ", ".join(
                paint(f"{h}p", "1;36", colors) for h in heights
            ))
            if args.verificar:
                continue
            height = choose_resolution(heights, colors)
            if height is not None:
                download_video(url, args.saida, height=height)
        except Exception as exc:
            print(f"Não foi possível consultar o vídeo: {exc}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
