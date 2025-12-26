import subprocess
import datetime
import os
import sys

CHANGELOG_PATH = "CHANGELOG.md"

def run_command(command):
    """Runs a shell command and returns output."""
    try:
        result = subprocess.run(
            command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{command}': {e.stderr}")
        return None

def get_changed_files():
    """Returns a list of changed files (staged and unstaged)."""
    # git status --porcelain gives file status in a machine-readable format
    output = run_command("git status --porcelain")
    if not output:
        return []
    
    files = []
    for line in output.split('\n'):
        # Format is "XY filename"
        parts = line.strip().split()
        if len(parts) >= 2:
            files.append(parts[-1])
    return files

def generate_commit_message(files):
    """Generates a simple commit message based on changed files."""
    if not files:
        return None
    
    # Heuristic: Focus on the most important files or extensions
    extensions = set(f.split('.')[-1] for f in files if '.' in f)
    
    if "CHANGELOG.md" in files:
        files.remove("CHANGELOG.md") # Don't mention itself

    if not files:
        return "docs: Update Changelog"

    base_names = [os.path.basename(f) for f in files[:3]] # List first 3 files
    file_list_str = ", ".join(base_names)
    if len(files) > 3:
        file_list_str += "..."

    main_action = "Update"
    if any("check_data" in f or "test" in f for f in files):
        main_action = "Verify"
    elif any("analysis" in f for f in files):
        main_action = "Enhance analysis in"
    
    message = f"{main_action} {file_list_str}"
    return message

def update_changelog(message):
    """Appends the commit message to the Changelog."""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    if not os.path.exists(CHANGELOG_PATH):
        print(f"Error: {CHANGELOG_PATH} not found.")
        return False

    with open(CHANGELOG_PATH, "r") as f:
        content = f.readlines()

    # Find the insertion point. We look for the first date header or insert after title.
    # Simple strategy: Look for "## [" line. If found, insert before it if it's not today, 
    # or append to it if it is today.
    
    # Actually, simpler for now: Just find the first "## " block.
    # ideally we want a ## [YYYY-MM-DD] block.
    
    new_lines = []
    inserted = False
    
    # Check if today's section exists
    today_header = f"## [{today}]"
    
    has_today = any(today_header in line for line in content)
    
    if has_today:
        # Append to today's section
        for line in content:
            new_lines.append(line)
            if today_header in line and not inserted:
                new_lines.append(f"- {message}\n")
                inserted = True
    else:
        # Create new section after header
        # Assumption: Header is usually the first few lines.
        # We'll insert after the [Unreleased] section or at top if not found.
        
        insert_idx = 0
        for i, line in enumerate(content):
            if "## [Unreleased]" in line:
                insert_idx = i + 1 # Insert after unreleased
                break
            if line.startswith("## [20"): # Found a previous date
                insert_idx = i
                break
        
        # If we didn't find a good spot, just put it after header (line 4ish)
        if insert_idx == 0 and len(content) > 5:
            insert_idx = 4
            
        new_lines = content[:insert_idx]
        if insert_idx > 0 and not content[insert_idx-1].strip() == "":
            new_lines.append("\n")
            
        new_lines.append(f"{today_header}\n")
        new_lines.append(f"- {message}\n")
        new_lines.append("\n")
        new_lines.extend(content[insert_idx:])
        
    with open(CHANGELOG_PATH, "w") as f:
        f.writelines(new_lines)
    
    print(f"Updated {CHANGELOG_PATH} with: {message}")
    return True

def main():
    print("--- Smart Commit ---")
    files = get_changed_files()
    if not files:
        print("No changes to commit.")
        sys.exit(0)
        
    print(f"Found changes in: {files}")
    
    message = generate_commit_message(files)
    print(f"Generated Message: {message}")
    
    if update_changelog(message):
        # Stage everything including changelog
        run_command("git add .")
        
        # Commit
        print("Committing...")
        output = run_command(f'git commit -m "{message}"')
        print(output)
        
        # Push? User might want to push manually, but let's push for "fix"
        # run_command("git push")
        print("Changes committed locally. Run 'git push' to sync.")
    else:
        print("Failed to update changelog. Aborting commit.")
        sys.exit(1)

if __name__ == "__main__":
    main()
