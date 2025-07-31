**MCP (Model Context Protocol)** is a protocol that enables LLMs to access custom tools and services. An MCP client (Cascade, in this case) can make requests to MCP servers to access tools that they provide. Cascade now natively integrates with MCP, allowing you to bring your own selection of MCP servers for Cascade to use. See the [official MCP docs](https://modelcontextprotocol.io/) for more information.

## Adding a new MCP plugin

New MCP plugins can be added from the Plugin Store, which you can access by clicking on the `Plugins` icon in the top right menu in the Cascade panel, or from the `Windsurf Settings` > `Cascade` > `Plugins` section. If you cannot find your desired MCP plugin, you can add it manually by editing the raw `mcp_config.json` file. Official MCP plugins will show up with a blue checkmark, indicating that they are made by the parent service company. When you click on a plugin, simply click `Install` to expose the server and its tools to Cascade. Windsurf supports two [transport types](https://modelcontextprotocol.io/docs/concepts/transports) for MCP servers: `stdio` and `/sse`. For `/sse` servers, the URL should reflect that of the endpoint and resemble `https://<your-server-url>/sse`. We can also support streamable HTTP transport and MCP Authentication.

Each plugin has a certain number of tools it has access to. Cascade has a limit of 100 total tools that it has access to at any given time. At the plugin level, you can navigate to the Tools tab and toggle the tools that you wish to enable. Or, from the `Windsurf Settings`, you can click on the `Manage plugins` button.

## mcp\_config.json

The `~/.codeium/windsurf/mcp_config.json` file is a JSON file that contains a list of servers that Cascade can connect to. The JSON should follow the same schema as the config file for Claude Desktop. Here’s an example configuration, which sets up a single server for GitHub:

```
<span><span>{</span></span>
<span><span>  "mcpServers"</span><span>: {</span></span>
<span><span>    "github"</span><span>: {</span></span>
<span><span>      "command"</span><span>: </span><span>"npx"</span><span>,</span></span>
<span><span>      "args"</span><span>: [</span></span>
<span><span>        "-y"</span><span>,</span></span>
<span><span>        "@modelcontextprotocol/server-github"</span></span>
<span><span>      ],</span></span>
<span><span>      "env"</span><span>: {</span></span>
<span><span>        "GITHUB_PERSONAL_ACCESS_TOKEN"</span><span>: </span><span>"&lt;YOUR_PERSONAL_ACCESS_TOKEN&gt;"</span></span>
<span><span>      }</span></span>
<span><span>    }</span></span>
<span><span>  }</span></span>
<span><span>}</span></span>
```

It’s important to note that for SSE servers, the configuration is slightly different and requires a `serverUrl` field. Here’s an example configuration for a SSE server:

```
<span><span>{</span></span>
<span><span>  "mcpServers"</span><span>: {</span></span>
<span><span>    "figma"</span><span>: {</span></span>
<span><span>      "serverUrl"</span><span>: </span><span>"&lt;your-server-url&gt;/sse"</span></span>
<span><span>    }</span></span>
<span><span>  }</span></span>
<span><span>}</span></span>
```

Be sure to provide the required arguments and environment variables for the servers that you want to use. See the [official MCP server reference repository](https://github.com/modelcontextprotocol/servers) or [OpenTools](https://opentools.com/) for some example servers.

## Admin Controls (Teams & Enterprises)

Team admins can toggle MCP access for their team, as well as whitelist approved MCP servers for their team to use:

[

## MCP Team Settings

Configurable MCP settings for your team.



](https://windsurf.com/team/settings)

By default, users within a team will be able to configure their own MCP servers. However, once you whitelist even a single MCP server, **all non-whitelisted servers will be blocked** for your team.

### How Server Matching Works

When you whitelist an MCP server, the system uses **regex pattern matching** with the following rules:

-   **Full String Matching**: All patterns are automatically anchored (wrapped with `^(?:pattern)$`) to prevent partial matches
-   **Command Field**: Must match exactly or according to your regex pattern
-   **Arguments Array**: Each argument is matched individually against its corresponding pattern
-   **Array Length**: The number of arguments must match exactly between whitelist and user config
-   **Special Characters**: Characters like `$`, `.`, `[`, `]`, `(`, `)` have special regex meaning and should be escaped with `\` if you want literal matching

### Configuration Options

### Common Regex Patterns

| Pattern | Matches | Example |
| --- | --- | --- |
| `.*` | Any string | `/home/user/script.py` |
| `[0-9]+` | Any number | `8080`, `3000` |
| `[a-zA-Z0-9_]+` | Alphanumeric + underscore | `api_key_123` |
| `\\$HOME` | Literal `$HOME` | `$HOME` (not expanded) |
| `\\.py` | Literal `.py` | `script.py` |
| `\\[cli\\]` | Literal `[cli]` | `mcp[cli]` |

## Notes

### Admin Configuration Guidelines

-   **Environment Variables**: The `env` section is not regex-matched and can be configured freely by users
-   **Disabled Tools**: The `disabledTools` array is handled separately and not part of whitelist matching
-   **Case Sensitivity**: All matching is case-sensitive
-   **Error Handling**: Invalid regex patterns will be logged and result in access denial
-   **Testing**: Test your regex patterns carefully - overly restrictive patterns may block legitimate use cases

### Troubleshooting

If users report that their MCP servers aren’t working after whitelisting:

1.  **Check Exact Matching**: Ensure the whitelist pattern exactly matches the user’s configuration
2.  **Verify Regex Escaping**: Special characters may need escaping (e.g., `\.` for literal dots)
3.  **Review Logs**: Invalid regex patterns are logged with warnings
4.  **Test Patterns**: Use a regex tester to verify your patterns work as expected

Remember: Once you whitelist any server, **all other servers are automatically blocked** for your team members.

### General Information

-   Since MCP tool calls can invoke code written by arbitrary server implementers, we do not assume liability for MCP tool call failures. To reiterate:
-   We currently support an MCP server’s [tools](https://modelcontextprotocol.io/docs/concepts/tools) and [resources](https://modelcontextprotocol.io/docs/concepts/resources), not [prompts](https://modelcontextprotocol.io/docs/concepts/prompts).