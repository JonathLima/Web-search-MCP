FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Expose the MCP HTTP endpoint port
EXPOSE 8000

# Run the MCP server in Streamable HTTP mode
CMD ["python", "-m", "src.server", "http"]
