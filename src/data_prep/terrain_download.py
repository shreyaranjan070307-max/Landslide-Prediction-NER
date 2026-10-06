import subprocess
from pathlib import Path

BUCKET = "s3://copernicus-dem-30m"
output_dir = Path("terrain_data/raw")
output_dir.mkdir(parents=True, exist_ok=True)

for lat in range(21, 30):
    for lon in range(88, 98):
        tile = f"Copernicus_DSM_COG_10_N{lat:02d}_00_E{lon:03d}_00_DEM"
        filename = f"{tile}.tif"
        output_file = output_dir / filename

        print(f"Downloading {filename}...")

        command = [
            "aws", "s3", "cp",
            "--no-sign-request",
            f"{BUCKET}/{tile}/{filename}",
            str(output_file)
        ]

        subprocess.run(command, check=True)

print("\nAll terrain tiles downloaded!")
