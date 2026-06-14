# Sector Agent

Sector Agent is a command-line financial research assistant built with LangGraph,
LangChain, Ollama, and yfinance. It can analyze a supported sector, compare two
supported sectors, or analyze a supported company using local JSON data and recent
Yahoo Finance closing prices.

## Features

- Sector analysis from `data/sector.json`
- Comparison of two sectors
- Company analysis from `data/company.json`
- Recent market-price retrieval with yfinance
- Local LLM responses through Ollama
- Route and error information printed after every run

## Requirements

- Python 3.10 or newer
- Ollama installed and running
- Internet access for company market data
- The Ollama model `gemma3:1b`

## Setup

Open PowerShell in the project root:

```powershell
cd C:\Users\user\Desktop\sector-agent\sector-agent
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run this once in the current terminal and try
again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Install the Python dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install langgraph langchain-core langchain-ollama yfinance pandas matplotlib
```

The project does not currently include a `requirements.txt`, so dependencies are
installed explicitly above.

## Ollama Setup

Install Ollama from <https://ollama.com/download>, then download the configured
model:

```powershell
ollama pull gemma3:1b
```

Confirm that the model is available:

```powershell
ollama list
```

Ollama normally starts automatically. If it is not running, start it with:

```powershell
ollama serve
```

The model configuration is in `agent/llm.py`.

## Run The Agent

From the project root, run:

```powershell
python -m agent.main
```

The program will prompt:

```text
What's on your mind?
```

Enter one of the supported query formats:

```text
analyze Apple
analyze energy sector
compare banking and healthcare
```

The output contains:

- `Report`: the generated analysis
- `Route taken`: the LangGraph nodes that ran
- `Errors`: data, market, or provider errors encountered during the run

Enter one query per run. Run `python -m agent.main` again for another query.

## Supported Data

The exact supported sectors are defined in `data/sector.json`. They currently
include:

- Semiconductors
- Banking
- Energy
- Consumer Technology
- Healthcare

The exact supported companies and ticker symbols are defined in
`data/company.json`. Company matching is case-insensitive, but the complete company
name should be used. Examples include Apple, Nvidia, Microsoft, ExxonMobil, Pfizer,
and JPMorgan Chase.

The query parser is intentionally simple. Use the demonstrated wording so it can
identify the correct route:

- Company: `analyze <company>`
- Sector: `analyze <sector> sector`
- Comparison: `compare <sector> and <sector>`

## Test yfinance

To test Yahoo Finance without running the LLM workflow:

```powershell
python -m agent.test
```

This requests five days of AAPL history and prints the returned DataFrame.

Company analysis requires internet access. Sector analysis and sector comparison
use local JSON data, but still require Ollama to generate the report.

## Run Unit Tests

Run the standard-library unit tests with:

```powershell
python -m unittest discover -s tests -v
```

The market-data tests mock yfinance, so they do not require internet access.

### Current Test Status

At the time this README was written, the three market-data tests do not match the
current implementation. The differences are:

- The test expects `history(period="5d", auto_adjust=False)`, while the code calls
  `history(period="5d")`.
- Two expected error messages use different wording from the implementation.

Choose the desired behavior and make the implementation and tests agree before
treating the test suite as passing.

## Project Structure

```text
sector-agent/
|-- agent/
|   |-- graph.py       # LangGraph nodes, routes, and edges
|   |-- llm.py         # Ollama model configuration
|   |-- main.py        # Interactive command-line entry point
|   |-- nodes.py       # Parsing, retrieval, analysis, and report nodes
|   |-- prompt.py      # LangChain prompt templates
|   |-- state.py       # Shared graph-state definition
|   `-- test.py        # Standalone yfinance check
|-- data/
|   |-- company.json   # Supported companies and ticker symbols
|   `-- sector.json    # Supported sectors and sector information
|-- tests/
|   `-- test_nodes.py  # Market-data unit tests
`-- README.md
```

## How The Workflow Works

1. `parse_query` detects a company, sector, or comparison request.
2. LangGraph routes the request to the appropriate local-data retrieval node.
3. Company requests also call yfinance for recent closing prices.
4. An analysis prompt is sent to the local Ollama model.
5. `final_report` asks the model to format the analysis as a report.
6. The CLI prints the report, route, and accumulated errors.

The company route is:

```text
parse_query
  -> retrieve_company_data
  -> retrieve_market_data
  -> company_analysis
  -> final_report
```

## Configuration

To use another Ollama model, update `model` in `agent/llm.py` and pull that model
before running the agent:

```python
llm = ChatOllama(
    model="gemma3:1b",
    temperature=0,
    num_predict=200,
)
```

`num_predict=200` limits response length. Increase it if reports are being cut off,
but expect longer generation times.

## Troubleshooting

### Ollama connection error

Make sure Ollama is running and the configured model is installed:

```powershell
ollama list
ollama serve
```

### `model not found`

Pull the model configured in `agent/llm.py`:

```powershell
ollama pull gemma3:1b
```

### Empty Yahoo Finance data

Check your internet connection and verify the ticker in `data/company.json`. Yahoo
may also temporarily rate-limit requests. Retry the standalone check:

```powershell
python -m agent.test
```

### `unable to open database file`

yfinance uses a local timezone cache. The standalone test sets the cache location
to `.yfinance-cache`. Ensure the project directory is writable and run commands
from the project root.

### Company or sector not found

Check the spelling against `data/company.json` or `data/sector.json`, and use one of
the supported query formats. The parser does not currently understand arbitrary
natural-language phrasing.

### Reports are slow

The full workflow makes two local LLM calls: one for analysis and another for the
final report. Performance depends on the selected model and available hardware.

### Reports contain unsupported details

Local language models can still add details despite prompt instructions. Treat the
output as generated analysis, not verified financial advice. Tighten the templates
in `agent/prompt.py` and validate important claims against the supplied JSON and
market data.

## Limitations

- This project is for educational use and is not financial advice.
- Company and sector coverage is limited to the local JSON files.
- Market data depends on Yahoo Finance availability and is not guaranteed to be
  real-time.
- The parser depends on simple keywords and fixed query formats.
- LLM output may be incomplete because `num_predict` is currently set to 200.
- The model may invent unsupported details; important output must be verified.
- The current unit-test expectations need to be synchronized with the code.

