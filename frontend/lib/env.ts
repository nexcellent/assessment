/** Where FastAPI listens when both run on one machine. */
const DEFAULT_BACKEND_URL = 'http://127.0.0.1:8000';

/**
 * The backend's base URL, read on the server only: the pages fetch from it while they
 * render, the browser never calls the backend. `docker-compose.yml` sets `BACKEND_URL`
 * to the backend container; locally the default is right.
 */
export function getBackendUrl(): string {
  return process.env.BACKEND_URL || DEFAULT_BACKEND_URL;
}
