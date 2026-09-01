from pathlib import Path
import argparse

from .model import run_model


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the dynamic process-water model."
    )
    parser.add_argument("--input-dir", type=Path, default=Path("config"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    args = parser.parse_args()

    rows, summary = run_model(args.input_dir, args.output_dir)
    print(f"Generated {len(rows)} detailed rows.")
    print(f"Generated {len(summary)} scenario/system summaries.")
    print("Reminder: bundled example data are synthetic and not validated limits.")


if __name__ == "__main__":
    main()
