(function () {
    const observer = new ResizeObserver(([entry]) => parent.postMessage({height: entry.target.offsetHeight}, "*"));
    observer.observe(document.documentElement);
})();
