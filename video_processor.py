import subprocess


def process_video(input_path, output_path, task_id, progress):
duration = 120
cmd = [
"ffmpeg", "-y", "-i", input_path,
"-t", str(duration),
"-vf",
"scale=1080:1920,crop=900:1600,rotate=0.01*sin(2*PI*t/5),"
"eq=contrast=1.15:brightness=0.03:saturation=1.25,"
"noise=alls=10:allf=t,zoompan=z='min(zoom+0.0015,1.25)':d=1",
"-filter:a", "atempo=1.05",
"-r", "33",
"-c:v", "libx264",
"-preset", "veryfast",
"-pix_fmt", "yuv420p",
"-progress", "pipe:1",
"-nostats",
output_path
]


p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
for line in p.stdout:
if "out_time_ms" in line:
out_ms = int(line.split("=")[1])
progress[task_id] = min(99, int((out_ms / (duration * 1_000_000)) * 100))
p.wait()
