import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import ollama
from rich.console import Console
from rich.panel import Panel

console = Console()

def get_git_metadata(repo_path: Path):
    try:
        cmd = [
            "git", "-C", str(repo_path), "log", "-1",
            "--format=%cd%x00%s%x00%an", "--date=iso-strict"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        raw = res.stdout.strip().split("\x00")
        if len(raw) == 3:
            return {
                "last_modified": datetime.fromisoformat(raw[0]),
                "commit_msg": raw[1],
                "author": raw[2],
                "is_git": True,
            }
    except Exception:
        pass
    return None

def scan_graveyard(target_dir: Path, threshold_days: int):
    now = datetime.now(timezone.utc)
    abandoned = []

    for entry in target_dir.iterdir():
        if entry.name.startswith((".", "node_modules", "venv", "__pycache__")):
            continue

        meta = None
        if entry.is_dir() and (entry / ".git").exists():
            meta = get_git_metadata(entry)

        if not meta:
            try:
                mtime = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc)
            except Exception:
                continue
            meta = {
                "last_modified": mtime,
                "commit_msg": "Untracked or non-git file",
                "author": "Unknown",
                "is_git": False,
            }

        delta_days = (now - meta["last_modified"]).days
        if delta_days >= threshold_days:
            meta["name"] = entry.name
            meta["days_inactive"] = delta_days
            abandoned.append(meta)

    return sorted(abandoned, key=lambda x: x["days_inactive"], reverse=True)

def generate_epitaphs(items, model="gemma2:2b", ofrenda=False):
    prompt = f"""You are the gravekeeper of an abandoned software cemetery.
Here is metadata for dead or forgotten code projects:
{json.dumps([{'name': it['name'], 'days_inactive': it['days_inactive'], 'last_commit': it['commit_msg']} for it in items], indent=2)}

Task:
Generate a valid JSON array of objects with keys:
- "name": exact name of the item
- "epitaph": a witty 1-2 sentence obituary in the spirit of Halloween/Día de los Muertos describing how it was abandoned.
{'- "revival_hint": a 1-sentence prompt on how to bring it back to life.' if ofrenda else ''}

Return ONLY raw JSON with no Markdown backticks:"""

    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.7}
    )
    raw = response["message"]["content"].strip()
    if raw.startswith("```"):
        raw = raw.strip("`").replace("json\n", "", 1).strip()
    return json.loads(raw)

def print_ascii_tombstones(epitaph_map):
    for name, data in epitaph_map.items():
        epitaph = data.get("epitaph", "Rested in silence.")
        revival = data.get("revival_hint", "")

        tombstone_art = (
            "[bold red]     .---.[/bold red]\n"
            "[bold red]    / RIP /[/bold red]\n"
            "[bold red]   |  ___  |[/bold red]   [bold yellow]" + name + "[/bold yellow]\n"
            "[bold red]   | |   | |[/bold red]   " + epitaph + "\n"
            "[bold red]   |_|___|_|[/bold red]"
        )
        if revival:
            tombstone_art += f"\n   [cyan]🌼 Ofrenda Revival:[/cyan] {revival}"
        
        console.print(Panel(tombstone_art, expand=False, border_style="dim white"))

def write_html_graveyard(output_path: Path, epitaph_map):
    cards = ""
    for name, data in epitaph_map.items():
        cards += f"""
        <div class="tombstone">
            <div class="cross">†</div>
            <h3>{name}</h3>
            <p class="epitaph">"{data.get('epitaph', '')}"</p>
            {f"<p class='ofrenda'>🌼 <strong>Remembered:</strong> {data.get('revival_hint')}</p>" if data.get('revival_hint') else ""}
        </div>
        """

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>The Code Cemetery</title>
    <style>
        body {{ background: #0f0f13; color: #dcdcdc; font-family: monospace; padding: 2rem; }}
        h1 {{ text-align: center; color: #ff5555; }}
        .grid {{ display: flex; flex-wrap: wrap; gap: 1.5rem; justify-content: center; }}
        .tombstone {{ background: #1c1d22; border: 1px solid #333; border-radius: 60px 60px 8px 8px; width: 280px; padding: 1.5rem; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.5); }}
        .cross {{ font-size: 1.5rem; color: #777; }}
        .epitaph {{ font-style: italic; color: #aaa; margin: 1rem 0; }}
        .ofrenda {{ font-size: 0.85rem; color: #f1fa8c; border-top: 1px dashed #444; padding-top: 0.5rem; }}
    </style>
</head>
<body>
    <h1>🪦 The Code Cemetery (Día de los Muertos Edition) 🌼</h1>
    <div class="grid">{cards}</div>
</body>
</html>"""
    output_path.write_text(html, encoding="utf-8")
    console.print(f"\n[green]Graveyard page saved to:[/green] {output_path.resolve()}")

def main():
    parser = argparse.ArgumentParser(description="rip: A graveyard for forgotten code.")
    parser.add_argument("path", nargs="?", default=".", help="Directory to scan")
    parser.add_argument("--days", type=int, default=30, help="Days of inactivity threshold")
    parser.add_argument("--model", default="gemma2:2b", help="Ollama model to use")
    parser.add_argument("--ofrenda", action="store_true", help="Include revival tips")
    parser.add_argument("--out", default="cemetery.html", help="HTML export filename")
    args = parser.parse_args()

    target = Path(args.path).resolve()
    console.print(f"[bold red]Scanning {target} for code untouched for > {args.days} days...[/bold red]")
    
    dead_items = scan_graveyard(target, args.days)
    if not dead_items:
        console.print("[green]No dead projects found! Lower --days to find older files.[/green]")
        return

    console.print(f"Found [bold yellow]{len(dead_items)}[/bold yellow] abandoned souls. Channeling spirits via [cyan]{args.model}[/cyan]...")
    
    try:
        epitaph_data = generate_epitaphs(dead_items[:6], model=args.model, ofrenda=args.ofrenda)
        epitaph_map = {item["name"]: item for item in epitaph_data}
    except Exception as e:
        console.print(f"[red]Error contacting Ollama or parsing response:[/red] {e}")
        sys.exit(1)

    print_ascii_tombstones(epitaph_map)
    write_html_graveyard(Path(args.out), epitaph_map)

if __name__ == "__main__":
    main()