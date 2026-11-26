import gifos
import os
import requests

USERNAME = os.environ.get("GITHUB_REPOSITORY_OWNER") or os.environ.get("GIT_USERNAME", "abrara9123")

headers = {"Accept": "application/vnd.github+json"}
if token := os.environ.get("GH_TOKEN"):
    headers["Authorization"] = f"Bearer {token}"
response = requests.get(
    f"https://api.github.com/users/{USERNAME}", headers=headers, timeout=20
)
response.raise_for_status()
profile = response.json()

# Terminal settings
t = gifos.Terminal(width=700, height=450, xpad=10, ypad=10)

# -- Initial prompt --
t.set_prompt(f"\x1b[91m{USERNAME}\x1b[0m@\x1b[93mgithub\x1b[0m ~> ")

# -- Boot sequence --
t.gen_text("Initializing terminal...", row_num=1)
t.clone_frame(5)
t.gen_text("\x1b[32m[OK]\x1b[0m System ready", row_num=2)
t.clone_frame(10)

# -- Command to view stats --
t.gen_prompt(row_num=3)
t.gen_typing_text("github-stats --user " + USERNAME, row_num=3, contin=True, speed=1)
t.clone_frame(5)

# -- Display statistics --
t.gen_text("", row_num=4)
t.gen_text(f"\x1b[96m=== GitHub Stats for {USERNAME} ===\x1b[0m", row_num=5)
t.clone_frame(3)

stats = [
    ("Name", profile.get("name") or USERNAME),
    ("Public repos", profile["public_repos"]),
    ("Followers", profile["followers"]),
    ("Following", profile["following"]),
]
stats_lines = [f"\x1b[93m{label + ':':<15}\x1b[0m{value}" for label, value in stats]

for i, line in enumerate(stats_lines):
    t.gen_text(line, row_num=6+i)
    t.clone_frame(3)

t.clone_frame(10)
t.gen_text("\x1b[96m================================\x1b[0m", row_num=6+len(stats_lines))
t.clone_frame(15)

# -- Clear and Skills --
t.gen_prompt(row_num=7+len(stats_lines))
t.gen_typing_text("clear", row_num=7+len(stats_lines), contin=True, speed=1)
t.clone_frame(5)
t.clear_frame()

t.gen_prompt(row_num=1)
t.gen_typing_text("cat skills.txt", row_num=1, contin=True, speed=1)
t.clone_frame(5)

t.gen_text("", row_num=2)
t.gen_text("\x1b[96m=== Tech Stack ===\x1b[0m", row_num=3)
t.clone_frame(3)

skills = [
    ("\x1b[94mLanguages:\x1b[0m   ", "C++, C, Python, Java"),
    ("\x1b[94mTools:\x1b[0m       ", "Git, CMake, GDB"),
    ("\x1b[94mSystems:\x1b[0m     ", "macOS, Linux"),
    ("\x1b[94mProjects:\x1b[0m    ", "Seer, QuantCore, RedCorn"),
]

for i, (label, value) in enumerate(skills):
    t.gen_text(f"{label}{value}", row_num=4+i)
    t.clone_frame(2)

t.clone_frame(10)
t.gen_text("\x1b[96m==================\x1b[0m", row_num=4+len(skills))
t.clone_frame(5)

# -- Final message --
final_row = 5 + len(skills)
t.gen_prompt(row_num=final_row)
t.gen_typing_text("echo 'Thanks for visiting my profile!'", row_num=final_row, contin=True, speed=1)
t.clone_frame(5)
t.gen_text("\x1b[92mThanks for visiting my profile!\x1b[0m", row_num=final_row+1)
t.clone_frame(40)

# Generate the GIF
t.gen_gif()

print("\n GIF generated: output.gif")
print("\nTo use in your README.md:")
print('![Terminal GIF](./output.gif)')


def add_space_wallpaper():
    from pathlib import Path

    from PIL import Image, ImageChops, ImageOps, ImageSequence

    output = Path("output.gif")
    asset = Path(__file__).resolve().parent / "assets" / "image(20261126-031050).png"
    frames = []
    durations = []

    with Image.open(output) as animation, Image.open(asset) as artwork:
        width, height = animation.size
        corner = (width - 1, height - 1)
        terminal_bg = animation.convert("RGB").getpixel(corner)
        backdrop = Image.new("RGB", animation.size, terminal_bg)
        image = ImageOps.contain(artwork.convert("RGB"), animation.size, Image.Resampling.LANCZOS)

        # Keep the full artwork at the right and fade it behind the terminal text.
        fade = Image.new("L", (image.width, 1))
        fade.putdata([round(218 * min(1.0, x / (image.width * 0.5))) for x in range(image.width)])
        backdrop.paste(image, (width - image.width, (height - image.height) // 2), fade.resize(image.size))

        # Share one palette across frames so the wallpaper stays still as text changes.
        palette = Image.new("P", (1, 1))
        backdrop_colors = backdrop.quantize(colors=224).getpalette()[:224 * 3]
        terminal_colors = [
            (255, 255, 255), (211, 215, 222), (255, 90, 90), (235, 185, 90),
            (115, 210, 240), (92, 160, 255), (110, 210, 130), (30, 115, 63),
        ]
        palette.putpalette(backdrop_colors + [channel for rgb in terminal_colors for channel in rgb])
        loop = animation.info.get("loop", 0)
        for frame in ImageSequence.Iterator(animation):
            rgb = frame.convert("RGB")
            flat = Image.new("RGB", animation.size, rgb.getpixel(corner))
            red, green, blue = ImageChops.difference(rgb, flat).split()
            difference = ImageChops.lighter(ImageChops.lighter(red, green), blue)
            text_mask = difference.point(lambda value: 255 if value > 4 else 0)
            composite = Image.composite(rgb, backdrop, text_mask)
            frames.append(composite.quantize(palette=palette, dither=Image.Dither.NONE))
            durations.append(frame.info.get("duration", 40))

    rendered = output.with_suffix(".wallpaper.gif")
    frames[0].save(
        rendered, save_all=True, append_images=frames[1:], duration=durations,
        loop=loop, disposal=1, optimize=True,
    )
    rendered.replace(output)


add_space_wallpaper()
