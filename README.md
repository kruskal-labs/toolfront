
[![Test Suite](https://github.com/kruskal-labs/toolfront/actions/workflows/test.yml/badge.svg)](https://github.com/kruskal-labs/toolfront/actions/workflows/test.yml)
[![Discord](https://img.shields.io/discord/1323415085011701870?label=Discord&logo=discord&logoColor=white&style=flat-square)](https://discord.gg/rRyM7zkZTf)

<br>
<div align="center"> 
<img alt="toolfront" src="img/logo.png" width="61.8%">
</div>
<br>

> AI agents lack context about your databases, while teams keep rewriting the same queries because past work often gets lost. 
> ToolFront connects agents to your databases and feeds them your team's proven query patterns, so both agents and teammates can learn from each other and ship faster.


## Features

- **⚡ One-step setup**: Connect coding agents like Cursor, GitHub Copilot, and Claude to all your databases with a single command or config.
- **🔒 Privacy-first**: Your data never leaves your premises, and is only shared between agents and databases through a secure MCP server.
- **🧠 Collaborative learning**: The more your team uses ToolFront, the better your AI agents understand your databases and query patterns. Requires API key.

<br>
<div align="center">
<img alt="databases" src="img/databases.png" width="61.8%">
</div>


## Quickstart

ToolFront runs on your computer through an [MCP](https://modelcontextprotocol.io/) server, a secure protocol that lets apps provide context to LLM models.

### Prerequisites


- **[uv](https://docs.astral.sh/uv/)** or **[Docker](https://www.docker.com/)** to run the MCP server (we recommend **uv**)
- **Database connection URLs** of your databases - [see below](#databases)
- **API key** (optional) to activate collaborative learning - [see below](#collaborative-in-context-learning)

### Run ToolFront in your IDE

[![Add to Cursor with UV](img/buttons/button_cursor_uv.png)](https://cursor.com/install-mcp?name=toolfront&config=eyJjb21tYW5kIjoidXZ4IHRvb2xmcm9udCBEQVRBQkFTRS1VUkwtMSBEQVRBQkFTRS1VUkwtMiAtLWFwaS1rZXkgWU9VUi1BUEktS0VZIn0%3D) [![Add to GitHub Copilot with UV](img/buttons/button_copilot_uv.png)](https://insiders.vscode.dev/redirect/mcp/install?name=toolfront&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22toolfront%22%2C%22DATABASE-URL-1%22%2C%22DATABASE-URL-2%22%2C%22--API-KEY%22%2C%22YOUR_API_KEY%22%5D%7D) [![Add to Cursor with Docker](img/buttons/button_cursor_docker.png)](https://cursor.com/install-mcp?name=toolfront&config=eyJjb21tYW5kIjoiZG9ja2VyIiwiYXJncyI6WyJydW4iLCItaSIsImFudGlkbWcvdG9vbGZyb250IiwiREFUQUJBU0UtVVJMLTEiLCJEQVRBQkFTRS1VUkwtMiIsIi0tYXBpLWtleSIsIllPVVItQVBJLUtFWSJdfQo=) [![Add to GitHub Copilot with Docker](img/buttons/button_copilot_docker.png)](https://insiders.vscode.dev/redirect/mcp/install?name=toolfront&config=%7B%22command%22%3A%22docker%22%2C%22args%22%3A%5B%22run%22%2C%22-i%22%2C%22antidmg%2Ftoolfront%22%2C%22DATABASE-URL-1%22%2C%22DATABASE-URL-2%22%2C%22--api-key%22%2C%22YOUR-API-KEY%22%5D%7D)

First, create an MCP config by clicking a setup button above or navigating to the MCP settings for your IDE:

| IDE | Setup Instructions | Documentation |
|-----|-------------------|---------------|
| **Cursor** | Settings → Cursor Settings → MCP Tools (or create `.cursor/mcp.json` file) | [Cursor Documentation](https://docs.cursor.com/context/model-context-protocol#manual-configuration) |
| **GitHub Copilot (VSCode)** | Copilot icon → Edit preferences → Copilot Chat → MCP | [GitHub Copilot Documentation](https://docs.github.com/en/copilot/customizing-copilot/using-model-context-protocol/extending-copilot-chat-with-mcp) |
| **Windsurf** | Plugins icon → Plugin Store → Add manually (or edit `~/.codeium/windsurf/mcp_config.json`) | [Windsurf Documentation](https://docs.windsurf.com/windsurf/cascade/mcp) |
| **Claude Code** | Run `claude mcp add toolfront uvx toolfront [database-urls] --api-key YOUR-API-KEY` | [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code/mcp#configure-mcp-servers) |

Then, edit the MCP configuration with your database connection URLs and optional API key:

<details>
<summary><strong>Edit UV Config</strong></summary>

```json
{
  # Rest of config file
  "toolfront": {
    "command": "uvx",
    "args": [
      "toolfront",
      "snowflake://user:pass@org",
      "postgresql://user:pass@host:port/db",
      # Add other database URLs here
      "--api-key", "YOUR-API-KEY"  // Optional
    ]
  }
}
```

</details>

<details>
<summary><strong>Edit Docker Config</strong></summary>

```json
{
  # Rest of config file
  "toolfront": {
    "command": "docker",
    "args": [
      "run",
      "-i",
      "antidmg/toolfront",
      "snowflake://user:pass@org",
      "postgresql://user:pass@host:port/db",
      # Add other database URLs here
      "--api-key", "YOUR-API-KEY"  // Optional
    ]
  }
}
```

</details>
<br>

You're all set! You can now ask your coding assistant about your databases.


> [!TIP]
> **Version control**: You can pin to specific versions for consistency. Use `toolfront==0.1.x` for UV or `antidmg/toolfront:0.1.x` for Docker.


### Run ToolFront from your Terminal

To use ToolFront outside your IDE, run it directly from your terminal with your database URLs and optional API key:

```bash
# Using UV
uvx toolfront "snowflake://user:pass@org" "postgresql://user:pass@host:port/db" --api-key "YOUR-API-KEY"

# Using Docker  
docker run -i antidmg/toolfront "snowflake://user:pass@org" "postgresql://user:pass@host:port/db" --api-key "YOUR-API-KEY"
```

> [!TIP]
> **Localhost databases**: Add `--network host` before the image name when connecting to databases running on localhost.

## Collaborative In-context Learning

Data teams keep rewriting the same queries because past work often gets siloed, scattered, or lost. ToolFront teaches AI agents how your team works with your databases through [in-context learning](https://transformer-circuits.pub/2022/in-context-learning-and-induction-heads/index.html#in-context-learning-key-concept). With ToolFront, your agents can:

- Reason about historical query patterns
- Remember relevant tables and schemas
- Reference your and your teammates' work

> [!NOTE]
> In-context learning is currently in open beta. To request an API key, please email Esteban at [esteban@kruskal.ai](mailto:esteban@kruskal.ai) or hop into our [Discord server](https://discord.gg/rRyM7zkZTf).


## Databases

ToolFront supports the following databases:

| Database | URL Format | Documentation |
|----------|------------|---------------|
| BigQuery | `bigquery://{project-id}?credentials_path={path-to-service-account.json}` | [Google Cloud Docs](https://cloud.google.com/bigquery/docs/authentication) |
| Databricks | `databricks://token:{token}@{workspace}.cloud.databricks.com/{catalog}?http_path={warehouse-path}` | [Databricks Docs](https://docs.databricks.com/integrations/jdbc-odbc-bi.html#get-connection-details) |
| DuckDB | `duckdb://{path-to-database.duckdb}` | [DuckDB Docs](https://duckdb.org/docs/api/python/dbapi.html) |
| MySQL | `mysql://{user}:{password}@{host}:{port}/{database}` | [MySQL Docs](https://dev.mysql.com/doc/connector-python/en/connector-python-connectargs.html) |
| PostgreSQL | `postgres://{user}:{password}@{hostname}:{port}/{database-name}` | [PostgreSQL Docs](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING) |
| Snowflake | `snowflake://{user}:{password}@{account}/{database}` | [Snowflake Docs](https://docs.snowflake.com/en/developer-guide/python-connector/python-connector-api#connection-parameters) |
| SQLite | `sqlite://{path-to-database.sqlite}` | [SQLite Docs](https://docs.python.org/3/library/sqlite3.html#sqlite3.connect) |

Don't see your database? [Submit an issue](https://github.com/kruskal-labs/toolfront/issues) or pull request, or let us know in our [Discord](https://discord.gg/rRyM7zkZTf)!

> [!TIP]
> **Working with local data files?** Add `duckdb://:memory:` to your config to analyze local Parquet, CSV, Excel, or JSON files.

## Tools

MCP tools are functions that AI agents can call to interact with external systems. ToolFront comes with seven database tools:

| Tool | Description | Requires API Key |
|------|-------------|------------------|
| `test` | Tests whether a data source connection is working | ✗ |
| `discover` | Discovers and lists all configured databases and file sources | ✗ |
| `scan` | Searches for tables using regex, fuzzy matching, or TF-IDF similarity | ✗ |
| `inspect` | Inspects table schemas, showing column names, data types, and constraints | ✗ |
| `sample` | Retrieves sample rows from tables to understand data content and format | ✗ |
| `query` | Executes read-only SQL queries against databases with error handling | ✗ |
| `learn` | Retrieves relevant queries or tables for in-context learning | ✓ |

## FAQ

<details>
<summary><strong>How is ToolFront different from other database MCPs?</strong></summary>
<br>

ToolFront has three key advantages: **multi-database support**, **privacy-first architecture**, and **collaborative learning**.

**Multi-database support**: While some general-purpose MCP servers happen to support multiple databases, most database MCPs only work with one database at a time, forcing you to manage separate MCP servers for each connection. ToolFront connects to all your databases in one place.

**Privacy-first architecture**: Other multi-database solutions route your data through the cloud, which racks up egress fees and creates serious privacy, security, and access control issues. ToolFront keeps everything local.

**Collaborative learning**: Database MCPs just expose raw database operations. ToolFront goes further by teaching your AI agents successful query patterns from your team's work, helping them learn your specific schemas and data relationships to improve over time.

</details>

<details>
<summary><strong>How is collaborative learning different from agent memory?</strong></summary>
<br>

Agent memory stores conversation histories for individuals, whereas ToolFront's collaborative learning remembers relational query patterns across your team and databases.

When one teammate queries a database, that knowledge becomes available to other team members using ToolFront. The system gets smarter over time by learning from your team's collective database interactions.

</details>

<details>
<summary><strong>What data is collected during collaborative learning?</strong></summary>
<br>

With an API key, ToolFront only logs the query syntax and their descriptions generated by your AI agents. It never collects your actual database content or personal information. For details, see the `query` and `learn` functions in [tools.py](src/toolfront/tools.py).

</details>

<details>
<summary><strong>How does ToolFront keep my data safe?</strong></summary>
<br>

- **Local execution**: All database connections and queries run on your machine
- **No secrets exposure**: Database credentials are never shared with AI agents
- **Read-only operations**: Only safe, read-only database queries are allowed
- **No data transmission**: Your database content never leaves your environment
- **Secure MCP protocol**: Direct communication between agents and databases with no third-party storage

</details>

<details>
<summary><strong>How do I troubleshoot connection issues?</strong></summary>
<br>

Run the `uvx toolfront` or `docker run` commands with your database URLs directly from the command line. ToolFront automatically tests all connections before starting and shows detailed error messages if any connection fails.

If you're still having trouble, double-check your database URLs using the examples in the [Databases section](#databases) above.

</details>

## Support & Community

Need help with ToolFront? We're here to assist:

- **Discord**: Join our [community server](https://discord.gg/rRyM7zkZTf) for real-time help and discussions
- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/kruskal-labs/toolfront/issues)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to ToolFront.

## License

ToolFront is released under the [GPL License v3](LICENSE). This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the GPL v3 License. For the full license text, see the [LICENSE](LICENSE) file in the repository.
