# Production Dockerfile for data-governance-mcp
FROM python:3.11-slim

# Prevent Python from writing bytecode and enable unbuffered output
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Copy project files required for installation
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install the server package and its dependencies
RUN pip install .

# Start the MCP server on stdio transport by default
ENTRYPOINT ["data-governance-mcp"]
CMD ["run"]
