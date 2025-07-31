[](https://github.com/n8n-io/n8n-docs/edit/main/docs/integrations/builtin/core-nodes/n8n-nodes-langchain.mcptrigger.md "Edit this page")

Use the MCP Server Trigger node to allow n8n to act as a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) server, making n8n tools and workflows available to MCP clients.

Credentials

You can find authentication information for this node [here](https://docs.n8n.io/integrations/builtin/credentials/httprequest/).

## How the MCP Server Trigger node works[#](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.mcptrigger/#how-the-mcp-server-trigger-node-works "Permanent link")

The MCP Server Trigger node acts as an entry point into n8n for MCP clients. It operates by exposing a URL that MCP clients can interact with to access n8n tools.

Unlike conventional [trigger nodes](https://docs.n8n.io/glossary/#trigger-node-n8n), which respond to events and pass their output to the next [connected node](https://docs.n8n.io/workflows/components/connections/), the MCP Server Trigger node only connects to and executes [tool](https://docs.n8n.io/advanced-ai/examples/understand-tools/) nodes. Clients can list the available tools and call individual tools to perform work.

You can expose n8n workflows to clients by attaching them with the [Custom n8n Workflow Tool](https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.toolworkflow/) node.

## Node parameters[#](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.mcptrigger/#node-parameters "Permanent link")

Use these parameters to configure your node.

### MCP URL[#](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.mcptrigger/#mcp-url "Permanent link")

The MCP Server Trigger node has two **MCP URLs**: test and production. n8n displays the URLs at the top of the node panel.

Select **Test URL** or **Production URL** to toggle which URL n8n displays.

-   **Test**: n8n registers a test MCP URL when you select **Listen for Test Event** or **Execute workflow**, if the workflow isn't active. When you call the MCP URL, n8n displays the data in the workflow.
-   **Production**: n8n registers a production MCP URL when you activate the workflow. When using the production URL, n8n doesn't display the data in the workflow. You can still view workflow data for a production execution: select the **Executions** tab in the workflow, then select the workflow execution you want to view.

### Authentication[#](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.mcptrigger/#authentication "Permanent link")

You can require authentication for clients connecting to your MCP URL. Choose from these authentication methods:

-   Bearer auth
-   Header auth

Refer to the [HTTP request credentials](https://docs.n8n.io/integrations/builtin/credentials/httprequest/) for more information on setting up each credential type.

### Path[#](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.mcptrigger/#path "Permanent link")

By default, this field contains a randomly generated MCP URL path, to avoid conflicts with other MCP Server Trigger nodes.

You can manually specify a URL path, including adding route parameters. For example, you may need to do this if you use n8n to prototype an API and want consistent endpoint URLs.

## Templates and examples[#](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.mcptrigger/#templates-and-examples "Permanent link")

### Integrating with Claude Desktop[#](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.mcptrigger/#integrating-with-claude-desktop "Permanent link")

You can connect to the MCP Server Trigger node from [Claude Desktop](https://claude.ai/download) by running a gateway to proxy SSE messages to stdio-based servers.

To do so, add the following to your Claude Desktop configuration:

<table><tbody><tr><td><div><pre><span></span><span> 1</span>
<span> 2</span>
<span> 3</span>
<span> 4</span>
<span> 5</span>
<span> 6</span>
<span> 7</span>
<span> 8</span>
<span> 9</span>
<span>10</span>
<span>11</span>
<span>12</span>
<span>13</span>
<span>14</span>
<span>15</span>
<span>16</span></pre></div></td><td><div><pre id="__code_0"><span></span><nav></nav><code><span>{</span>
<span>  </span><span>"mcpServers"</span><span>:</span><span> </span><span>{</span>
<span>    </span><span>"n8n"</span><span>:</span><span> </span><span>{</span>
<span>      </span><span>"command"</span><span>:</span><span> </span><span>"npx"</span><span>,</span>
<span>      </span><span>"args"</span><span>:</span><span> </span><span>[</span>
<span>        </span><span>"mcp-remote"</span><span>,</span>
<span>        </span><span>"&lt;MCP_URL&gt;"</span><span>,</span>
<span>        </span><span>"--header"</span><span>,</span>
<span>        </span><span>"Authorization: Bearer ${AUTH_TOKEN}"</span>
<span>      </span><span>],</span>
<span>      </span><span>"env"</span><span>:</span><span> </span><span>{</span>
<span>        </span><span>"AUTH_TOKEN"</span><span>:</span><span> </span><span>"&lt;MCP_BEARER_TOKEN&gt;"</span>
<span>      </span><span>}</span>
<span>    </span><span>}</span>
<span>  </span><span>}</span>
<span>}</span>
</code></pre></div></td></tr></tbody></table>

Be sure to replace the `<MCP_URL>` and `<MCP_BEARER_TOKEN>` placeholders with the values from your MCP Server Trigger node parameters and credentials.

## Limitations[#](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.mcptrigger/#limitations "Permanent link")

### Configuring the MCP Server Trigger node with webhook replicas[#](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.mcptrigger/#configuring-the-mcp-server-trigger-node-with-webhook-replicas "Permanent link")

The MCP Server Trigger node relies on Server-Sent Events (SSE) or streamable HTTP, which require the same server instance to handle persistent connections. This can cause problems when running n8n in [queue mode](https://docs.n8n.io/hosting/scaling/queue-mode/) depending on your [webhook processor](https://docs.n8n.io/hosting/scaling/queue-mode/#webhook-processors) configuration:

-   If you use queue mode with a **single webhook replica**, the MCP Server Trigger node works as expected.
-   If you run **multiple webhook replicas**, you need to route all `/mcp*` requests to a single, dedicated webhook replica. Create a separate replica set with one webhook container for MCP requests. Afterward, update your ingress or load balancer configuration to direct all `/mcp*` traffic to that instance.

Caution when running with multiple webhook replicas

If you run an MCP Server Trigger node with multiple webhook replicas and don't route all `/mcp*` requests to a single, dedicated webhook replica, your SSE and streamable HTTP connections will frequently break or fail to reliably deliver events.

n8n also provides an [MCP Client Tool](https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.toolmcp/) node that allows you to connect your n8n AI agents to external tools.

Refer to the [MCP documentation](https://modelcontextprotocol.io/introduction) and [MCP specification](https://modelcontextprotocol.io/specification/) for more details about the protocol, servers, and clients.

## Common issues[#](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.mcptrigger/#common-issues "Permanent link")

Here are some common errors and issues with the MCP Server Trigger node and steps to resolve or troubleshoot them.

### Running the MCP Server Trigger node with a reverse proxy[#](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.mcptrigger/#running-the-mcp-server-trigger-node-with-a-reverse-proxy "Permanent link")

When running n8n behind a reverse proxy like nginx, you may experience problems if the MCP endpoint isn't configured for SSE or streamable HTTP.

Specifically, you need to disable proxy buffering for the endpoint. Other items you might want to adjust include disabling gzip compression (n8n handles this itself), disabling chunked transfer encoding, and setting the `Connection` to an empty string to remove it from the forwarded headers. Explicitly disabling these in the MCP endpoint ensures they're not inherited from other places in your nginx configuration.

An example nginx location block for serving MCP traffic with these settings may look like this:

<table><tbody><tr><td></td><td><div><pre id="__code_1"><span></span><nav></nav><code>location /mcp/ {
    proxy_http_version          1.1;
    proxy_buffering             off;
    gzip                        off;
    chunked_transfer_encoding   off;

    proxy_set_header            Connection '';

    # The rest of your proxy headers and settings
    # . . .
}
</code></pre></div></td></tr></tbody></table>