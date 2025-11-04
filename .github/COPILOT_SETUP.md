# GitHub Copilot Configuration

Custom instructions that help Copilot understand this codebase without duplicating what's already in the code.

## Structure

```text
.github/
├── copilot-instructions.md          # Main instructions (repository-wide)
└── instructions/                     # Path-specific instructions
    ├── rust-backend.instructions.md
    ├── python-ai-service.instructions.md
    ├── frontend-react.instructions.md
    ├── docker-compose.instructions.md
    └── config-files.instructions.md
```

## Design Philosophy

**Point, don't duplicate:**

- ✅ Non-negotiable rules (security, error patterns)
- ✅ Key files to read (let Copilot extract info)
- ✅ Where to look (paths, not details)

**Let Copilot read the code:**

- Commands → In main instructions only, not repeated in path-specific
- Implementation patterns → Point to files, don't explain
- Tech details → Reference config files, don't list versions
- Architecture → Point to READMEs, don't duplicate diagrams

## Maintenance

### Update When

1. Non-negotiable rules change (e.g., new security requirement)
2. Key file locations change (e.g., file renamed)
3. Core workflows change (e.g., new build tool)

## Further Reading

- [GitHub Docs: Custom Instructions](https://docs.github.com/en/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot)
- [VS Code: Copilot Customization](https://code.visualstudio.com/docs/copilot/copilot-customization)
