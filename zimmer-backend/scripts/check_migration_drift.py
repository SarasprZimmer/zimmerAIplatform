import os
import glob
import sys
import subprocess

DRIFT_REV_ID = "check_drift"

def find_file_with(substr: str):
    for p in glob.glob("migrations/versions/*.py"):
        if substr in os.path.basename(p):
            return p
    return None

def main():
    env = os.environ.copy()

    # Ensure DB is migrated to head (use whatever DATABASE_URL is set)
    try:
        subprocess.check_call(["alembic", "-c", "alembic.ini", "upgrade", "head"], env=env)
    except subprocess.CalledProcessError as e:
        print("❌ Could not upgrade to head before drift check:", e)
        sys.exit(3)

    # Create a temp autogenerate revision; if models != DB, Alembic will emit ops.
    # We use a fixed rev-id so we can easily locate and delete it.
    try:
        subprocess.check_call([
            "alembic", "-c", "alembic.ini",
            "revision", "--autogenerate",
            "-m", "drift_check", "--rev-id", DRIFT_REV_ID
        ], env=env)
    except subprocess.CalledProcessError as e:
        print("❌ Autogenerate failed:", e)
        sys.exit(4)

    path = find_file_with(DRIFT_REV_ID)
    if not path:
        print("❌ Could not find generated drift revision file with rev-id:", DRIFT_REV_ID)
        sys.exit(5)

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # If Alembic emitted any operations, there is drift.
        ops_indicators = (
            "op.create_table(", "op.drop_table(",
            "op.add_column(", "op.drop_column(",
            "op.create_foreign_key(", "op.drop_constraint(",
            "op.alter_column(", "op.create_index(", "op.drop_index("
        )
        drift = any(tok in content for tok in ops_indicators)

        if drift:
            print("❌ Drift detected: autogenerate produced schema operations.")
            print(f"   See: {path}")
            # Print a small excerpt of the diff area
            lines = content.splitlines()
            for i, line in enumerate(lines):
                if "def upgrade():" in line:
                    print("— upgrade() snippet —")
                    print("\n".join(lines[i:i+40]))
                    break
            sys.exit(2)
        else:
            print("✅ No drift detected")

    finally:
        # Cleanup the temp file so it doesn't pollute repo
        try:
            os.remove(path)
        except OSError:
            pass

if __name__ == "__main__":
    main()
