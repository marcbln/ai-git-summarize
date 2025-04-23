# AI-Git Refactoring Plan v2

## Combined Objectives
1. Rename CLI tool from `git-summarize` to `ai-git`
2. Rename directory structure from `git_summarize/` to `ai_git/`

```mermaid
graph TD
    A[Refactoring Process] --> B[Directory Structure]
    A --> C[Package Configuration]
    A --> D[Code References]
    A --> E[Documentation]
    A --> F[Testing]
    
    B --> B1[[Rename git_summarize/ to ai_git/]]
    B --> B2[[Update internal imports]]
    
    C --> C1[[Update pyproject.toml name]]
    C --> C2[[Modify entrypoint path]]
    C --> C3[[Update environment variables]]
    
    D --> D1[[CLI command definitions]]
    D --> D2[[Help text references]]
    
    E --> E1[[Merge README files]]
    E --> E2[[Update command examples]]
    E --> E3[[Update ai_docs references]]
    
    F --> F1[[Reinstall package]]
    F --> F2[[Test CLI availability]]
    F --> F3[[Verify imports]]
```

## Implementation Strategy

### 1. Directory & Code Updates
```bash
# Rename root directory
mv git_summarize ai_git

# Update all Python imports (example)
sed -i 's/from git_summarize/from ai_git/g' ai_git/**/*.py
```

### 2. Package Configuration (pyproject.toml)
```toml
[project]
name = "ai-git"
# ...
[project.scripts]
ai-git = "ai_git.cli:app"  # Updated path
```

### 3. Environment Variables
```diff
- GIT_SUMMARIZE_DEFAULT_MODEL
+ AI_GIT_DEFAULT_MODEL
```

### 4. Documentation Sync
1. Merge `ai_git/README.md` into root README
2. Update all documentation references:
```diff
- git-summarize --help
+ ai-git --help
```

### 5. Validation Checklist
1. Reinstall package:
```bash
uv pip uninstall ai-git
uv pip install -e .
```
2. Verify functionality:
```bash
ai-git --list-models
python3 -c "from ai_git import __version__; print(__version__)"
```
3. Check documentation links in:
- ai_docs/rename_plan.md
- ai_docs/refactor_plan.md