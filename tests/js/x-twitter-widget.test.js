/**
 * Test suite for the X/Twitter widget.
 *
 * The widget renders embedded tweets with the official
 * `twttr.widgets.createTweet` API, sizing each embed to its container and
 * re-rendering on theme / viewport changes.
 */
const MODULE_PATH = "zensical_macros_utils/static/js/x-twitter-widget";

/** Tweet id used by the default fixture container. */
const TWEET_ID = "123456789";
const TWEET_URL = "https://twitter.com/example/status/123456789";

/** Flush the microtask queue so createTweet's then/catch callbacks run. */
function flush() {
  return Promise.resolve().then(() => Promise.resolve());
}

/**
 * (Re)load the widget module in isolation.
 * @param {{ debug?: boolean }} [options]
 */
function loadModule({ debug = false } = {}) {
  globalThis.__X_TWITTER_DEBUG__ = debug;
  jest.isolateModules(() => {
    require(MODULE_PATH);
  });
}

/** Build a fresh createTweet mock returning a resolved promise. */
function createTweetMock() {
  return jest.fn().mockResolvedValue({});
}

describe("X/Twitter widget", () => {
  beforeEach(() => {
    jest.resetModules();
    jest.useFakeTimers();

    document.body.innerHTML = `
      <div class="x-twitter-embed" data-url="${TWEET_URL}" data-tweet-id="${TWEET_ID}"></div>
    `;

    global.twttr = {
      widgets: { createTweet: createTweetMock() },
      ready: (cb) => cb(),
    };

    Object.defineProperty(window, "localStorage", {
      value: { getItem: jest.fn(), setItem: jest.fn(), clear: jest.fn() },
      writable: true,
    });

    Object.defineProperty(document, "readyState", {
      value: "complete",
      writable: true,
    });
  });

  afterEach(() => {
    document.body.innerHTML = "";
    delete global.twttr;
    delete globalThis.__X_TWITTER_DEBUG__;
    jest.clearAllMocks();
    jest.clearAllTimers();
    document.documentElement.removeAttribute("data-md-color-scheme");
    document.body.removeAttribute("data-md-color-scheme");
  });

  /** Return the options passed to the most recent createTweet call. */
  function lastCreateTweetCall() {
    const calls = global.twttr.widgets.createTweet.mock.calls;
    return calls[calls.length - 1];
  }

  // -- Rendering ------------------------------------------------------------

  test("renders the tweet with id, container and options", () => {
    loadModule();

    expect(global.twttr.widgets.createTweet).toHaveBeenCalled();
    const [id, container, options] = lastCreateTweetCall();
    expect(id).toBe(TWEET_ID);
    expect(container.classList.contains("x-twitter-embed")).toBe(true);
    expect(options).toMatchObject({
      theme: "light",
      width: 550,
      dnt: true,
      align: "center",
    });
  });

  test("clears container before rendering", () => {
    const container = document.querySelector(".x-twitter-embed");
    container.innerHTML = "<span>stale</span>";
    loadModule();
    expect(container.querySelector("span")).toBeNull();
  });

  test("resolves createTweet promise without throwing", async () => {
    global.twttr.widgets.createTweet = jest.fn().mockResolvedValue({});
    loadModule();
    await flush();
    expect(global.twttr.widgets.createTweet).toHaveBeenCalled();
  });

  test("handles createTweet rejection without throwing", async () => {
    global.twttr.widgets.createTweet = jest
      .fn()
      .mockRejectedValue(new Error("boom"));
    loadModule();
    await flush();
    expect(global.twttr.widgets.createTweet).toHaveBeenCalled();
  });

  test("skips containers without a tweet id", () => {
    document.body.innerHTML = `
      <div class="x-twitter-embed" data-url="${TWEET_URL}"></div>
    `;
    loadModule();
    expect(global.twttr.widgets.createTweet).not.toHaveBeenCalled();
  });

  // -- Color scheme ---------------------------------------------------------

  test("uses dark theme from html data attribute (slate)", () => {
    document.documentElement.setAttribute("data-md-color-scheme", "slate");
    loadModule();
    expect(lastCreateTweetCall()[2].theme).toBe("dark");
  });

  test("uses light theme from html data attribute (default)", () => {
    document.documentElement.setAttribute("data-md-color-scheme", "default");
    loadModule();
    expect(lastCreateTweetCall()[2].theme).toBe("light");
  });

  test("uses theme from body data attribute", () => {
    document.body.setAttribute("data-md-color-scheme", "slate");
    loadModule();
    expect(lastCreateTweetCall()[2].theme).toBe("dark");
  });

  test("uses theme from checked palette input (slate)", () => {
    document.body.innerHTML = `
      <div class="x-twitter-embed" data-url="${TWEET_URL}" data-tweet-id="${TWEET_ID}"></div>
      <form data-md-component="palette">
        <input type="radio" data-md-color-scheme="slate" checked>
      </form>
    `;
    loadModule();
    expect(lastCreateTweetCall()[2].theme).toBe("dark");
  });

  test("uses light theme from checked palette input (default)", () => {
    document.body.innerHTML = `
      <div class="x-twitter-embed" data-url="${TWEET_URL}" data-tweet-id="${TWEET_ID}"></div>
      <form data-md-component="palette">
        <input type="radio" data-md-color-scheme="default" checked>
      </form>
    `;
    loadModule();
    expect(lastCreateTweetCall()[2].theme).toBe("light");
  });

  test("falls through palette with no checked input", () => {
    document.body.innerHTML = `
      <div class="x-twitter-embed" data-url="${TWEET_URL}" data-tweet-id="${TWEET_ID}"></div>
      <form data-md-component="palette"></form>
    `;
    loadModule();
    expect(lastCreateTweetCall()[2].theme).toBe("light");
  });

  test("uses dark theme from localStorage", () => {
    window.localStorage.getItem.mockReturnValue("slate");
    loadModule();
    expect(lastCreateTweetCall()[2].theme).toBe("dark");
  });

  test("uses light theme from localStorage non-slate value", () => {
    window.localStorage.getItem.mockReturnValue("default");
    loadModule();
    expect(lastCreateTweetCall()[2].theme).toBe("light");
  });

  test("defaults to light theme when nothing is set", () => {
    window.localStorage.getItem.mockReturnValue(null);
    loadModule();
    expect(lastCreateTweetCall()[2].theme).toBe("light");
  });

  test("reads color scheme from __palette JSON in localStorage", () => {
    window.localStorage.getItem.mockImplementation((key) => {
      if (key === "__palette") return JSON.stringify({ color: { scheme: "slate" } });
      return null;
    });
    loadModule();
    expect(lastCreateTweetCall()[2].theme).toBe("dark");
  });

  test("falls back to legacy key when __palette JSON has no color.scheme", () => {
    window.localStorage.getItem.mockImplementation((key) => {
      if (key === "__palette") return JSON.stringify({ other: true });
      if (key === "data-md-color-scheme") return "slate";
      return null;
    });
    loadModule();
    expect(lastCreateTweetCall()[2].theme).toBe("dark");
  });

  test("uses dark theme from OS matchMedia when nothing else is set", () => {
    window.localStorage.getItem.mockReturnValue(null);
    window.matchMedia = jest.fn().mockReturnValue({ matches: true });
    loadModule();
    expect(lastCreateTweetCall()[2].theme).toBe("dark");
    delete window.matchMedia;
  });

  test("uses light theme when matchMedia reports no dark preference", () => {
    window.localStorage.getItem.mockReturnValue(null);
    window.matchMedia = jest.fn().mockReturnValue({ matches: false });
    loadModule();
    expect(lastCreateTweetCall()[2].theme).toBe("light");
    delete window.matchMedia;
  });

  test("reads color scheme via __md_get when available", () => {
    globalThis.__md_get = jest.fn().mockReturnValue({ color: { scheme: "slate" } });
    loadModule();
    expect(lastCreateTweetCall()[2].theme).toBe("dark");
    delete globalThis.__md_get;
  });

  test("falls through __md_get to OS preference when palette not in storage", () => {
    globalThis.__md_get = jest.fn().mockReturnValue(null);
    window.localStorage.getItem.mockReturnValue(null);
    loadModule();
    expect(lastCreateTweetCall()[2].theme).toBe("light");
    delete globalThis.__md_get;
  });

  test("skips server-rendered default body attribute and uses OS dark preference", () => {
    document.body.setAttribute("data-md-color-scheme", "default");
    window.localStorage.getItem.mockReturnValue(null);
    window.matchMedia = jest.fn().mockReturnValue({ matches: true });
    loadModule();
    expect(lastCreateTweetCall()[2].theme).toBe("dark");
    delete window.matchMedia;
  });

  // -- Width ----------------------------------------------------------------

  test("uses container width when available", () => {
    const container = document.querySelector(".x-twitter-embed");
    Object.defineProperty(container, "clientWidth", {
      value: 300,
      configurable: true,
    });
    loadModule();
    expect(lastCreateTweetCall()[2].width).toBe(300);
  });

  test("clamps width to the maximum", () => {
    const container = document.querySelector(".x-twitter-embed");
    Object.defineProperty(container, "clientWidth", {
      value: 900,
      configurable: true,
    });
    loadModule();
    expect(lastCreateTweetCall()[2].width).toBe(550);
  });

  test("clamps width to the minimum", () => {
    const container = document.querySelector(".x-twitter-embed");
    Object.defineProperty(container, "clientWidth", {
      value: 100,
      configurable: true,
    });
    loadModule();
    expect(lastCreateTweetCall()[2].width).toBe(220);
  });

  // -- Widget availability guards ------------------------------------------

  test("skips rendering when twttr is undefined", () => {
    delete global.twttr;
    loadModule();
    // Re-render triggered by the color-scheme observer must not throw.
    expect(() => jest.advanceTimersByTime(100)).not.toThrow();
  });

  test("skips rendering when twttr.widgets is missing", () => {
    global.twttr = {};
    loadModule();
    expect(() => jest.advanceTimersByTime(100)).not.toThrow();
  });

  test("skips rendering when createTweet is missing", () => {
    global.twttr = { widgets: {} };
    expect(() => loadModule()).not.toThrow();
  });

  // -- Script loading -------------------------------------------------------

  test("injects preconnect and script when twttr is absent", () => {
    delete global.twttr;
    const appendSpy = jest.spyOn(document.head, "appendChild");
    loadModule();

    const tags = appendSpy.mock.calls.map((c) => c[0]);
    const preconnect = tags.find(
      (el) => el.tagName === "LINK" && el.rel === "preconnect"
    );
    const script = tags.find((el) => el.tagName === "SCRIPT");
    expect(preconnect).toBeTruthy();
    expect(script).toBeTruthy();
    expect(script.src).toContain("platform.twitter.com/widgets.js");
    appendSpy.mockRestore();
  });

  test("renders after the script finishes loading", () => {
    delete global.twttr;
    const appendSpy = jest.spyOn(document.head, "appendChild");
    loadModule();

    const script = appendSpy.mock.calls
      .map((c) => c[0])
      .find((el) => el.tagName === "SCRIPT");

    const createTweet = createTweetMock();
    global.twttr = { widgets: { createTweet }, ready: (cb) => cb() };
    script.onload();

    expect(createTweet).toHaveBeenCalledWith(
      TWEET_ID,
      expect.any(Object),
      expect.objectContaining({ align: "center" })
    );
    appendSpy.mockRestore();
  });

  test("script onload tolerates twttr never becoming available", () => {
    delete global.twttr;
    const appendSpy = jest.spyOn(document.head, "appendChild");
    loadModule();
    const script = appendSpy.mock.calls
      .map((c) => c[0])
      .find((el) => el.tagName === "SCRIPT");
    expect(() => script.onload()).not.toThrow();
    appendSpy.mockRestore();
  });

  test("script onerror is handled gracefully", () => {
    delete global.twttr;
    const appendSpy = jest.spyOn(document.head, "appendChild");
    loadModule();
    const script = appendSpy.mock.calls
      .map((c) => c[0])
      .find((el) => el.tagName === "SCRIPT");
    expect(() => script.onerror(new Error("load failed"))).not.toThrow();
    appendSpy.mockRestore();
  });

  test("uses twttr.ready when it is a function on load", () => {
    delete global.twttr;
    const appendSpy = jest.spyOn(document.head, "appendChild");
    loadModule();
    const script = appendSpy.mock.calls
      .map((c) => c[0])
      .find((el) => el.tagName === "SCRIPT");

    const createTweet = createTweetMock();
    const ready = jest.fn((cb) => cb());
    global.twttr = { widgets: { createTweet }, ready };
    script.onload();

    expect(ready).toHaveBeenCalled();
    expect(createTweet).toHaveBeenCalled();
    appendSpy.mockRestore();
  });

  // -- Observers & handlers -------------------------------------------------

  test("re-renders on palette change events", () => {
    document.body.innerHTML = `
      <div class="x-twitter-embed" data-url="${TWEET_URL}" data-tweet-id="${TWEET_ID}"></div>
      <form data-md-component="palette">
        <input type="radio" data-md-color-scheme="default" checked>
      </form>
    `;
    loadModule();
    const callsBefore = global.twttr.widgets.createTweet.mock.calls.length;

    const palette = document.querySelector('[data-md-component="palette"]');
    palette.dispatchEvent(new Event("change"));
    jest.advanceTimersByTime(100);

    expect(
      global.twttr.widgets.createTweet.mock.calls.length
    ).toBeGreaterThan(callsBefore);
  });

  test("re-renders on window resize", () => {
    loadModule();
    const callsBefore = global.twttr.widgets.createTweet.mock.calls.length;

    window.dispatchEvent(new Event("resize"));
    jest.advanceTimersByTime(200);

    expect(
      global.twttr.widgets.createTweet.mock.calls.length
    ).toBeGreaterThan(callsBefore);
  });

  test("re-renders on window load to pick up the settled palette theme", () => {
    loadModule();
    const callsBefore = global.twttr.widgets.createTweet.mock.calls.length;

    window.dispatchEvent(new Event("load"));

    expect(
      global.twttr.widgets.createTweet.mock.calls.length
    ).toBeGreaterThan(callsBefore);
  });

  // -- Initialization -------------------------------------------------------

  test("waits for DOMContentLoaded when document is still loading", () => {
    Object.defineProperty(document, "readyState", {
      value: "loading",
      writable: true,
    });
    const addEventListenerSpy = jest.spyOn(document, "addEventListener");

    loadModule();

    const domReady = addEventListenerSpy.mock.calls.find(
      (call) => call[0] === "DOMContentLoaded"
    );
    expect(domReady).toBeTruthy();

    // Invoke the registered handler to run start().
    domReady[1]();
    expect(global.twttr.widgets.createTweet).toHaveBeenCalled();
    addEventListenerSpy.mockRestore();
  });

  // -- Debug logging --------------------------------------------------------

  test("logs to the console when debug is enabled", () => {
    loadModule({ debug: true });
    const logged = console.log.mock.calls.some((args) =>
      String(args[0]).includes("[X-Twitter-Widget]")
    );
    expect(logged).toBe(true);
  });

  test("stays silent when debug is disabled", () => {
    loadModule({ debug: false });
    const logged = console.log.mock.calls.some((args) =>
      String(args[0]).includes("[X-Twitter-Widget]")
    );
    expect(logged).toBe(false);
  });
});
