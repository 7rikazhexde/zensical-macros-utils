(function () {
  /**
   * Enable verbose logging in the browser console.
   * Off by default; set `window.__X_TWITTER_DEBUG__ = true` before this
   * script loads to opt in.
   * @type {boolean}
   */
  const DEBUG = Boolean(globalThis.__X_TWITTER_DEBUG__);

  /** Prefix used for all log messages. @type {string} */
  const LOG_PREFIX = "[X-Twitter-Widget]";

  /** Maximum width (px) Twitter renders an embedded tweet at. @type {number} */
  const MAX_WIDTH = 550;

  /** Minimum sensible width (px) for an embedded tweet. @type {number} */
  const MIN_WIDTH = 220;

  /** Official Twitter widgets script URL. @type {string} */
  const TWITTER_SCRIPT_SRC = "https://platform.twitter.com/widgets.js";

  /**
   * Log a debug message when DEBUG is enabled.
   * @param {string} message - Primary message.
   * @param {...*} args - Additional values to log.
   */
  function log(message, ...args) {
    if (DEBUG) {
      console.log(`${LOG_PREFIX} ${message}`, ...args);
    }
  }

  /**
   * Map a Material color-scheme name to a Twitter widget theme.
   * @param {string} scheme - 'slate' for dark, anything else for light.
   * @returns {string} 'dark' or 'light'.
   */
  function schemeToTheme(scheme) {
    return scheme === "slate" ? "dark" : "light";
  }

  /**
   * Read the persisted palette scheme.
   *
   * Material/zensical stores the palette at a path-scoped localStorage key
   * and exposes `__md_get` as a global helper to read it.  If available, that
   * is used; otherwise we fall back to the raw (unscoped) `__palette` key for
   * non-Material deployments, then the legacy `data-md-color-scheme` key.
   * @returns {string|null} The stored scheme name, or null.
   */
  function readStoredScheme() {
    try {
      // __md_get reads from the scoped key ({pathname}.__palette), which is
      // what the bundle and the inline palette script actually write to.
      if (typeof __md_get === "function") {
        const data = __md_get("__palette");
        if (data && data.color && data.color.scheme) {
          return data.color.scheme;
        }
      }
      const raw = localStorage.getItem("__palette");
      if (raw) {
        const data = JSON.parse(raw);
        if (data && data.color && data.color.scheme) {
          return data.color.scheme;
        }
      }
    } catch (err) {
      log("Could not parse stored palette:", err);
    }
    return localStorage.getItem("data-md-color-scheme");
  }

  /**
   * Whether the OS / browser prefers a dark color scheme.
   * @returns {boolean}
   */
  function prefersDarkScheme() {
    return (
      typeof window.matchMedia === "function" &&
      window.matchMedia("(prefers-color-scheme: dark)").matches
    );
  }

  /**
   * Determine the color scheme the reader is currently seeing.
   *
   * Priority order:
   * 1. Palette radio – set by the bundle after initialization; most accurate.
   * 2. Persisted palette – reads the scoped localStorage key via `__md_get`.
   * 3. HTML/body attribute – but "default" is the server-rendered placeholder
   *    before the client JS runs, so it is skipped; only explicit non-default
   *    values (e.g. "slate" set by an inline script) are trusted here.
   * 4. OS preference via matchMedia.
   *
   * @returns {string} 'dark' or 'light'.
   */
  function getColorScheme() {
    const palette = document.querySelector('[data-md-component="palette"]');
    if (palette) {
      const checkedInput = palette.querySelector('input[type="radio"]:checked');
      if (checkedInput) {
        const scheme = checkedInput.getAttribute("data-md-color-scheme");
        log("Using palette color scheme:", scheme);
        return schemeToTheme(scheme);
      }
    }

    // Check persisted palette before the body attribute: the body is
    // server-rendered as "default" and Material only updates it when a palette
    // is explicitly stored, so the stored value is more reliable.
    const storedScheme = readStoredScheme();
    if (storedScheme) {
      log("Using stored color scheme:", storedScheme);
      return schemeToTheme(storedScheme);
    }

    // "default" is the server-rendered placeholder — skip it and fall through
    // to the OS preference so users relying on prefers-color-scheme get dark.
    const attrScheme =
      document.documentElement.getAttribute("data-md-color-scheme") ||
      document.body.getAttribute("data-md-color-scheme");
    if (attrScheme && attrScheme !== "default") {
      log("Using document color scheme:", attrScheme);
      return schemeToTheme(attrScheme);
    }

    log("Falling back to OS color-scheme preference");
    return prefersDarkScheme() ? "dark" : "light";
  }

  /**
   * Compute the render width for a tweet, clamped to the container.
   * @param {HTMLElement} container - The embed container.
   * @returns {number} Width in pixels.
   */
  function computeWidth(container) {
    const available = container.clientWidth || MAX_WIDTH;
    return Math.max(MIN_WIDTH, Math.min(available, MAX_WIDTH));
  }

  /**
   * Render (or re-render) a single tweet inside its container using the
   * official createTweet API, which sizes the embed reliably on both
   * desktop and mobile.
   * @param {HTMLElement} container - Element with data-tweet-id.
   */
  function renderTweet(container) {
    const tweetId = container.getAttribute("data-tweet-id");
    if (!tweetId) {
      log("Container has no tweet id, skipping");
      return;
    }

    if (!(window.twttr && window.twttr.widgets && window.twttr.widgets.createTweet)) {
      log("twttr.widgets.createTweet is unavailable");
      return;
    }

    const theme = getColorScheme();
    const width = computeWidth(container);
    log("Rendering tweet", tweetId, "theme:", theme, "width:", width);

    container.innerHTML = "";
    window.twttr.widgets
      .createTweet(tweetId, container, {
        theme: theme,
        width: width,
        dnt: true,
        align: "center",
      })
      .then(() => log("Tweet rendered successfully"))
      .catch((err) => log("Error rendering tweet:", err));
  }

  /**
   * Render every tweet embed on the page.
   */
  function renderAllTweets() {
    log("Rendering all tweets");
    document.querySelectorAll(".x-twitter-embed").forEach(renderTweet);
  }

  /**
   * Create a debounced version of a function.
   * @param {Function} func - Function to debounce.
   * @param {number} wait - Delay in milliseconds.
   * @returns {Function} Debounced function.
   */
  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      clearTimeout(timeout);
      timeout = setTimeout(() => func(...args), wait);
    };
  }

  /**
   * Invoke a callback once the Twitter widgets API is ready.
   * @param {Function} callback - Function to run when ready.
   */
  function whenReady(callback) {
    if (window.twttr && typeof window.twttr.ready === "function") {
      window.twttr.ready(callback);
    } else {
      callback();
    }
  }

  /**
   * Ensure the Twitter widgets script is loaded, then run the callback.
   * Uses a preconnect hint to speed up the initial connection.
   * @param {Function} onReady - Callback to run once widgets are available.
   */
  function loadWidgetScript(onReady) {
    if (window.twttr && window.twttr.widgets) {
      log("Twitter widgets already available");
      whenReady(onReady);
      return;
    }

    log("Loading Twitter widgets script");
    const preconnect = document.createElement("link");
    preconnect.rel = "preconnect";
    preconnect.href = "https://platform.twitter.com";
    document.head.appendChild(preconnect);

    const script = document.createElement("script");
    script.src = TWITTER_SCRIPT_SRC;
    script.async = true;
    script.onload = () => {
      log("Twitter script loaded");
      whenReady(onReady);
    };
    script.onerror = (err) => log("Failed to load Twitter script:", err);
    document.head.appendChild(script);
  }

  /**
   * Observe color-scheme changes and re-render tweets when the theme flips.
   */
  function setupColorSchemeObserver() {
    log("Setting up color scheme observer");
    const debouncedRender = debounce(renderAllTweets, 100);

    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.attributeName === "data-md-color-scheme") {
          log("Color scheme mutation detected");
          debouncedRender();
        }
      });
    });

    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["data-md-color-scheme"],
    });
    observer.observe(document.body, {
      attributes: true,
      attributeFilter: ["data-md-color-scheme"],
    });

    const palette = document.querySelector('[data-md-component="palette"]');
    if (palette) {
      palette.addEventListener("change", () => {
        log("Palette change detected");
        debouncedRender();
      });
    }
  }

  /**
   * Re-render tweets (debounced) when the viewport width changes so the
   * embed width keeps matching its container on resize / orientation change.
   */
  function setupResizeHandler() {
    log("Setting up resize handler");
    window.addEventListener("resize", debounce(renderAllTweets, 200));
  }

  /**
   * Set up observers and trigger the initial render.
   *
   * The window 'load' listener re-renders after the full page (including
   * zensical's palette JS) has settled, so the correct theme is picked up
   * even if the initial render ran before the palette radio was set.
   */
  function start() {
    setupColorSchemeObserver();
    setupResizeHandler();
    loadWidgetScript(renderAllTweets);
    window.addEventListener("load", renderAllTweets);
  }

  /**
   * Entry point: wait for the DOM if necessary, then start.
   */
  function initialize() {
    log("Starting initialization");
    if (document.readyState === "loading") {
      log("Document still loading, waiting for DOMContentLoaded");
      document.addEventListener("DOMContentLoaded", start);
      return;
    }
    start();
  }

  log("Script loaded");
  initialize();
})();
