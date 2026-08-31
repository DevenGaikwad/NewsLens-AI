const DEFAULT_STREAMLIT_URL = "https://YOUR-APP.streamlit.app";

/**
 * Validate the sole browser-exposed deployment value before it is used in
 * markup or a Content-Security-Policy header. Community Cloud application
 * URLs are HTTPS origins below streamlit.app; paths, credentials, ports,
 * queries, and fragments are deliberately rejected.
 */
export function validatedStreamlitUrl(value = process.env.NEXT_PUBLIC_STREAMLIT_APP_URL): string {
  const candidate = (value || DEFAULT_STREAMLIT_URL).trim();
  if (candidate.length > 2048 || /[\u0000-\u001f\u007f]/.test(candidate)) {
    throw new Error("NEXT_PUBLIC_STREAMLIT_APP_URL contains invalid characters or is too long.");
  }

  let parsed: URL;
  try {
    parsed = new URL(candidate);
  } catch {
    throw new Error("NEXT_PUBLIC_STREAMLIT_APP_URL must be a valid absolute URL.");
  }

  const hostname = parsed.hostname.toLowerCase();
  const communityCloudHost = /^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.streamlit\.app$/;
  if (
    parsed.protocol !== "https:" ||
    parsed.username ||
    parsed.password ||
    parsed.port ||
    parsed.search ||
    parsed.hash ||
    (parsed.pathname && parsed.pathname !== "/") ||
    !communityCloudHost.test(hostname)
  ) {
    throw new Error(
      "NEXT_PUBLIC_STREAMLIT_APP_URL must be an HTTPS Streamlit Community Cloud origin such as https://your-app.streamlit.app."
    );
  }

  return parsed.origin;
}
