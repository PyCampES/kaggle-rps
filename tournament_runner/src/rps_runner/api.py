import logging
from datetime import datetime
from io import StringIO

import uvicorn
from fastapi import FastAPI
from rich.console import Console
from rich.table import Table
from starlette.responses import HTMLResponse

from rps_runner.html_converter import cleanup_html
from rps_runner.tournament_runner import AgentResult, full_run, get_results

app = FastAPI()
logger = logging.getLogger(__name__)


def html_response(results: list[AgentResult]):
    html = as_html(results)
    html = cleanup_html(html)
    return HTMLResponse(content=html)


@app.get("/run")
def run():
    logger.info(f"starting run")
    results = full_run()
    return html_response(results)


@app.get("/")
def get_result():
    logger.info(f"now={datetime.utcnow()}")
    agent_results = get_results()
    return html_response(agent_results)


def main():
    format = "%(asctime)s.%(msecs)03d %(levelname)-7s %(threadName)-s %(name)-s %(lineno)-s %(message)-s"
    logging.basicConfig(level=logging.INFO, format=format)
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level=None,
        log_config=None,
        access_log=False,
    )


def as_html(results: list[AgentResult]):
    io_stream = StringIO()
    console = Console(
        record=True,
        file=io_stream,
        width=200,
    )
    table = Table("Agent", "Wins", "Ties", "Loses")
    for row in results:
        table.add_row(*[row.name, str(row.wins), str(row.ties), str(row.loses)])
    console.print(table)
    return console.export_html()


if __name__ == "__main__":
    main()
