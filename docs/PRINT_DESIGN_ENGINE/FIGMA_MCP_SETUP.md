# Figma MCP Setup for MATANGI

Figma MCP is not currently connected in this ChatGPT session. The following setup enables an IDE agent to read Figma frames and, where supported by the Figma server and account, create/update native Figma content.

## Official Figma MCP server

Use the official server and follow the maintained guide:
- Guide: https://github.com/figma/mcp-server-guide
- Server URL: https://mcp.figma.com/mcp
- Developer documentation: https://developers.figma.com/docs/figma-mcp-server/

For VS Code, add an HTTP MCP server with ID `figma` and URL `https://mcp.figma.com/mcp` through the MCP server UI. For Cursor, follow the Figma plugin instructions in the official guide.

## Alternative community context server

- Repository: https://github.com/GLips/Figma-Context-MCP
- This alternative requires a Figma personal access token. Keep that token in the local IDE secret store or environment; never commit it to GitHub or paste it into issue comments.

## Design handoff

1. Create a Figma file named `MATANGI Print Studio`.
2. Create pages: `00 Foundations`, `01 Overview`, `02 Campaign Editor`, `03 Product Board`, `04 Command Library`, `05 Research`, `06 Preflight & Export`, `07 Mobile`.
3. Import tokens and component rules from `DESIGN.md`.
4. Design desktop frames at 1440 × 900 and mobile frames at 390 × 844.
5. Include empty, loading, error, blocked and completed states.
6. Add frame links and component names to the implementation issue/PR.
7. Keep Figma credentials out of the repository.

Figma plan/seat limits and server capabilities may affect tool availability; verify the current official docs before depending on write-to-canvas or high-volume extraction.
