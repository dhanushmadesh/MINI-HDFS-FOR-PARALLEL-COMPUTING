# MINI_HDFS.py
import os
import json

NODES_DIR = "nodes"
NAMENODE_DIR = "namenode"
METADATA_FILE = os.path.join(NAMENODE_DIR, "metadata.json")


# -----------------------------
# Metadata Helpers
# -----------------------------
def load_metadata():
    if not os.path.exists(METADATA_FILE):
        return {"files": []}
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_metadata(metadata):
    os.makedirs(NAMENODE_DIR, exist_ok=True)
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)


# -----------------------------
# FIXED: Line-Safe File Splitter
# -----------------------------
def split_and_store(file_path, num_nodes=3):
    if not os.path.exists(file_path):
        print("[ERROR] File not found!")
        return False

    # Read all lines (SAFE, no cut words)
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    total_lines = len(lines)
    lines_per_chunk = total_lines // num_nodes

    chunks = []
    start = 0

    for i in range(num_nodes):
        # Last node gets the remaining lines
        end = start + lines_per_chunk if i < num_nodes - 1 else total_lines
        chunk_lines = lines[start:end]

        node_dir = os.path.join(NODES_DIR, f"node{i+1}")
        os.makedirs(node_dir, exist_ok=True)

        chunk_filename = f"{os.path.basename(file_path)}_chunk_{i+1}.txt"
        chunk_path = os.path.join(node_dir, chunk_filename)

        with open(chunk_path, "w", encoding="utf-8") as cf:
            cf.writelines(chunk_lines)

        chunks.append({
            "node": f"node{i+1}",
            "path": chunk_path,
            "lines": len(chunk_lines)
        })

        start = end

    # Update metadata
    metadata = load_metadata()
    metadata["files"].append({
        "file_name": os.path.basename(file_path),
        "num_chunks": num_nodes,
        "chunks": chunks
    })
    save_metadata(metadata)

    print(f"[INFO] File safely split into {num_nodes} chunks (line-safe).")
    return True


# -----------------------------
# Utility: List files in Mini HDFS
# -----------------------------
def list_files():
    data = load_metadata()
    if not data["files"]:
        print("[INFO] No files found.")
        return

    print("\nFiles in Mini HDFS:")
    for i, f in enumerate(data["files"], start=1):
        print(f"{i}. {f['file_name']} ({f['num_chunks']} chunks)")
    print()


# -----------------------------
# Utility: Get chunk file paths
# -----------------------------
def get_chunk_paths(file_name):
    data = load_metadata()
    for entry in data["files"]:
        if entry["file_name"] == file_name:
            return [c["path"] for c in entry["chunks"]]
    return []
