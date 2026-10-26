"""Create the application's original geometric icon; no screenshot/image input."""
from pathlib import Path
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[1] / "resources"
root.mkdir(exist_ok=True)
scale = 4
image = Image.new("RGBA", (256 * scale, 256 * scale), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)
draw.rounded_rectangle((8 * scale, 8 * scale, 248 * scale, 248 * scale), radius=56 * scale, fill="#202126", outline="#50483d", width=3 * scale)
points = [(49 * scale, 86 * scale), (82 * scale, 176 * scale), (121 * scale, 107 * scale), (158 * scale, 176 * scale), (195 * scale, 86 * scale)]
draw.line(points, fill="#dfc7a2", width=15 * scale, joint="curve")
draw.ellipse((186 * scale, 51 * scale, 210 * scale, 75 * scale), fill="#dfc7a2")
image = image.resize((256, 256), Image.Resampling.LANCZOS)
image.save(root / "wayfinder.png")
image.save(root / "wayfinder.ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
