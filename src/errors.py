from __future__ import annotations

class MCPToolError(Exception):

    error_code: str = "UNKNOWN_ERROR"
    retry_guidance: str = "Please try again later or use a different approach."

    def __init__(self, message: str, retry_guidance: str | None = None) -> None:
        super().__init__(message)
        if retry_guidance is not None:
            self.retry_guidance = retry_guidance

class SearchConnectionError(MCPToolError):

    error_code = "SEARCH_CONNECTION_ERROR"
    retry_guidance = (
        "The search service is currently unreachable. "
        "Wait 30 seconds and try again. If the problem persists, "
        "the search infrastructure may need to be restarted."
    )

class SearchTimeoutError(MCPToolError):

    error_code = "SEARCH_TIMEOUT_ERROR"
    retry_guidance = (
        "The search service took too long to respond. "
        "Try a more specific query with fewer terms, or wait a moment and retry."
    )

class SearchEmptyResultError(MCPToolError):

    error_code = "SEARCH_EMPTY_RESULT"
    retry_guidance = (
        "No results were found for this query. "
        "Try rephrasing the query with different keywords, "
        "use broader terms, or try a different time range."
    )

class SearchHTTPError(MCPToolError):

    error_code = "SEARCH_HTTP_ERROR"
    retry_guidance = (
        "The search service returned an HTTP error. "
        "This may be temporary — wait a moment and retry. "
        "If using a specific time range or category, try removing it."
    )

    def __init__(self, message: str, status_code: int, retry_guidance: str | None = None) -> None:
        self.status_code = status_code
        super().__init__(message, retry_guidance)

class SearchValidationError(MCPToolError):

    error_code = "SEARCH_VALIDATION_ERROR"
    retry_guidance = (
        "The search query is invalid. "
        "Ensure the query is a non-empty string with at most 500 characters. "
        "Check that time_range, categories, and safesearch values are valid."
    )

class FetchConnectionError(MCPToolError):

    error_code = "FETCH_CONNECTION_ERROR"
    retry_guidance = (
        "Unable to connect to the specified URL. "
        "The site may be down or the URL may be incorrect. "
        "Verify the URL and try again, or search for an alternative source."
    )

class FetchTimeoutError(MCPToolError):

    error_code = "FETCH_TIMEOUT_ERROR"
    retry_guidance = (
        "The target server did not respond in time. "
        "The site may be overloaded. Try searching for cached or archived versions, "
        "or find the information from an alternative source."
    )

class FetchHTTPError(MCPToolError):

    error_code = "FETCH_HTTP_ERROR"
    retry_guidance = (
        "The page returned an HTTP error. "
        "Try searching for the content on an alternative site or "
        "check if the URL is still valid."
    )

    def __init__(self, message: str, status_code: int, retry_guidance: str | None = None) -> None:
        self.status_code = status_code
        super().__init__(message, retry_guidance)

class FetchBlockedError(MCPToolError):

    error_code = "FETCH_BLOCKED_ERROR"
    retry_guidance = (
        "The target site is blocking automated requests. "
        "Try finding this content on an alternative source, "
        "or search for a cached/archived version of the page."
    )

class FetchParseError(MCPToolError):

    error_code = "FETCH_PARSE_ERROR"
    retry_guidance = (
        "The page content could not be parsed. "
        "The site may return non-standard HTML. "
        "Try an alternative URL or search for the same information elsewhere."
    )

class FetchURLError(MCPToolError):

    error_code = "FETCH_URL_ERROR"
    retry_guidance = (
        "The provided URL is not valid. "
        "Ensure the URL starts with http:// or https:// and contains a valid domain. "
        "Check for typos and try again."
    )

class FetchNonHTMLError(MCPToolError):

    error_code = "FETCH_NON_HTML_ERROR"
    retry_guidance = (
        "The URL does not point to an HTML page. "
        "If you need to read this content type, note that it has been returned as raw text."
    )
