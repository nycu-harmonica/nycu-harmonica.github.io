(() => {
  "use strict";

  const stage = document.querySelector("[data-screen-stage]");
  if (stage) {
    const items = [...document.querySelectorAll("[data-program-item]")];
    const songCount = Number(stage.dataset.songCount || items.length);

    const setCurrentSong = (songNumber) => {
      const selected = Number.isInteger(songNumber) && songNumber >= 1 && songNumber <= songCount ? songNumber : 0;
      items.forEach((item) => {
        const isCurrent = Number(item.dataset.programItem) === selected;
        item.classList.toggle("is-current", isCurrent);
        if (isCurrent) item.setAttribute("aria-current", "true");
        else item.removeAttribute("aria-current");
      });
      stage.dataset.currentSong = String(selected);
      const url = new URL(window.location.href);
      if (selected) url.searchParams.set("song", String(selected));
      else url.searchParams.delete("song");
      window.history.replaceState({}, "", url);
      const current = selected ? items[selected - 1] : null;
      window.BambooSEO?.setState(current ? {
        title: `第 ${selected} 首：${current.dataset.programTitle}`,
        heading: `目前曲目第 ${selected} 首：${current.dataset.programTitle}`,
        description: `竹韻演出投影畫面目前標示第 ${selected} 首《${current.dataset.programTitle}》，曲目資訊：${current.dataset.programCredit}。`,
      } : null);
    };

    setCurrentSong(Number(new URL(window.location.href).searchParams.get("song")));
    const fullscreenButton = document.querySelector("[data-fullscreen-button]");
    fullscreenButton?.addEventListener("click", () => {
      if (document.fullscreenElement) document.exitFullscreen?.();
      else stage.requestFullscreen?.();
    });
    document.addEventListener("fullscreenchange", () => {
      if (fullscreenButton) fullscreenButton.textContent = document.fullscreenElement ? "離開全螢幕" : "進入全螢幕";
    });
    document.addEventListener("keydown", (event) => {
      if (event.key.toLowerCase() === "f") {
        event.preventDefault();
        fullscreenButton?.click();
      } else if (/^[0-9]$/.test(event.key)) setCurrentSong(Number(event.key));
      else if (event.key === "ArrowRight") setCurrentSong(Math.min(Number(stage.dataset.currentSong) + 1, songCount));
      else if (event.key === "ArrowLeft") setCurrentSong(Math.max(Number(stage.dataset.currentSong) - 1, 0));
    });
    return;
  }

  const player = document.querySelector("[data-story-player]");
  const track = player?.querySelector("[data-story-track]");
  if (!player || !track) return;

  const slides = [...track.children];
  const bars = [...player.querySelectorAll("[data-story-progress] > span")];
  const announcer = player.querySelector("[data-story-announcer]");
  const pauseButton = player.querySelector("[data-story-pause]");
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const defaultDuration = Number(player.dataset.defaultDuration) || 7000;
  const storyStorageKey = `portal-story:${window.location.pathname}`;

  let current = -1;
  let elapsed = 0;
  let startedAt = 0;
  let frame = 0;
  let paused = true;
  let manualPause = reducedMotion;
  let holding = false;
  let ended = false;

  const duration = () => Number(slides[current]?.dataset.storyDuration) || defaultDuration;
  const activeVideo = () => slides[current]?.querySelector("video") || null;

  function pauseActiveVideo() {
    activeVideo()?.pause();
  }

  function playActiveVideo() {
    if (paused || manualPause || holding || ended || document.hidden) return;
    activeVideo()?.play().catch(() => {});
  }

  function drawProgress() {
    bars.forEach((bar, index) => {
      const pct = index < current ? 100 : index === current ? Math.min(100, (elapsed / duration()) * 100) : 0;
      bar.style.setProperty("--story-progress", `${pct}%`);
    });
  }

  function updatePauseButton() {
    if (!pauseButton) return;
    const showPlay = manualPause || ended;
    pauseButton.textContent = showPlay ? "▶" : "Ⅱ";
    pauseButton.setAttribute("aria-label", showPlay ? "繼續播放" : "暫停播放");
    pauseButton.setAttribute("aria-pressed", String(showPlay));
  }

  function tick(now) {
    if (paused) return;
    elapsed = now - startedAt;
    if (elapsed >= duration()) {
      if (current >= slides.length - 1) {
        elapsed = duration();
        ended = true;
        paused = true;
        pauseActiveVideo();
        drawProgress();
        updatePauseButton();
        return;
      }
      show(current + 1);
      return;
    }
    drawProgress();
    frame = requestAnimationFrame(tick);
  }

  function startProgress() {
    cancelAnimationFrame(frame);
    elapsed = 0;
    ended = false;
    paused = manualPause || document.hidden;
    startedAt = performance.now();
    drawProgress();
    updatePauseButton();
    if (!paused) {
      playActiveVideo();
      frame = requestAnimationFrame(tick);
    } else pauseActiveVideo();
  }

  function pauseProgress() {
    if (paused) return;
    elapsed = Math.min(duration(), performance.now() - startedAt);
    paused = true;
    cancelAnimationFrame(frame);
    pauseActiveVideo();
    drawProgress();
  }

  function resumeProgress() {
    if (!paused || manualPause || holding || ended || document.hidden) return;
    paused = false;
    startedAt = performance.now() - elapsed;
    playActiveVideo();
    frame = requestAnimationFrame(tick);
  }

  function togglePause() {
    if (ended) {
      show(0);
      return;
    }
    manualPause = !manualPause;
    if (manualPause) pauseProgress();
    else resumeProgress();
    updatePauseButton();
  }

  function show(n) {
    const next = Math.max(0, Math.min(slides.length - 1, n));
    slides.forEach((slide, index) => {
      const isActive = index === next;
      slide.classList.toggle("is-active", isActive);
      slide.toggleAttribute("inert", !isActive);
      const video = slide.querySelector("video");
      if (!video) return;
      video.pause();
      video.currentTime = 0;
    });
    current = next;
    const storyNumber = current + 1;
    const url = new URL(window.location.href);
    if (storyNumber > 1) url.searchParams.set("story", String(storyNumber));
    else url.searchParams.delete("story");
    window.history.replaceState(window.history.state, "", url);
    try { window.sessionStorage.setItem(storyStorageKey, String(storyNumber)); } catch (_error) {}
    const slide = slides[current];
    window.BambooSEO?.setState(storyNumber > 1 ? {
      title: slide.dataset.storyTitle,
      heading: slide.dataset.storyTitle,
      description: slide.dataset.storyDescription,
    } : null);
    if (announcer) announcer.textContent = `${storyNumber} / ${slides.length}：${slide.dataset.storyTitle || "竹韻限時動態"}`;
    startProgress();
  }

  function move(delta) {
    show(current + delta);
  }

  function readStoryNumber({ allowStored = false } = {}) {
    const requested = Number(new URL(window.location.href).searchParams.get("story"));
    if (Number.isInteger(requested) && requested >= 1 && requested <= slides.length) return requested;
    if (allowStored) {
      try {
        const stored = Number(window.sessionStorage.getItem(storyStorageKey));
        if (Number.isInteger(stored) && stored >= 1 && stored <= slides.length) return stored;
      } catch (_error) {
        // Some embedded browsers disable sessionStorage; the URL remains authoritative.
      }
    }
    return 1;
  }

  // 按住任意處暫停；快速點兩側前進後退；水平滑動換頁。互動元素（連結、按鈕）不攔截。
  let gesture = null;
  let suppressTap = false;

  player.addEventListener("pointerdown", (event) => {
    if (event.pointerType === "mouse" && event.button !== 0) return;
    if (event.target.closest("a, [data-story-share], [data-story-pause]")) return;
    suppressTap = false;
    gesture = {
      x: event.clientX,
      y: event.clientY,
      startedAt: performance.now(),
      onTapZone: Boolean(event.target.closest("[data-story-prev], [data-story-next]")),
    };
    holding = true;
    player.classList.add("is-paused");
    pauseProgress();
  });

  const releaseGesture = (event) => {
    if (!gesture) return;
    const dx = event.clientX - gesture.x;
    const dy = event.clientY - gesture.y;
    const heldFor = performance.now() - gesture.startedAt;
    const wasOnTapZone = gesture.onTapZone;
    gesture = null;
    holding = false;
    player.classList.remove("is-paused");
    if (Math.abs(dx) >= 48 && Math.abs(dx) > Math.abs(dy) * 1.15) {
      suppressTap = wasOnTapZone;
      move(dx < 0 ? 1 : -1);
      return;
    }
    suppressTap = wasOnTapZone && heldFor > 250;
    resumeProgress();
  };

  player.addEventListener("pointerup", releaseGesture);
  player.addEventListener("pointercancel", releaseGesture);
  player.addEventListener("pointerleave", releaseGesture);

  player.querySelector("[data-story-prev]")?.addEventListener("click", () => {
    if (suppressTap) { suppressTap = false; return; }
    move(-1);
  });
  player.querySelector("[data-story-next]")?.addEventListener("click", () => {
    if (suppressTap) { suppressTap = false; return; }
    move(1);
  });
  pauseButton?.addEventListener("click", togglePause);

  document.addEventListener("keydown", (event) => {
    if (event.key === "ArrowLeft") move(-1);
    else if (event.key === "ArrowRight") move(1);
    else if (event.key === " " && !event.target.closest?.("a, button")) {
      event.preventDefault();
      togglePause();
    }
  });

  // 桌面觸控板送的是 wheel 事件；一次手勢只換一頁，慣性尾巴不再觸發。
  let wheel = { x: 0, y: 0, last: 0, handled: false };
  player.addEventListener("wheel", (event) => {
    const now = Date.now();
    if (now - wheel.last > 180) wheel = { x: 0, y: 0, last: now, handled: false };
    wheel.last = now;
    wheel.x += event.deltaX || (event.shiftKey ? event.deltaY : 0);
    wheel.y += event.shiftKey ? 0 : event.deltaY;
    if (wheel.handled) {
      event.preventDefault();
      return;
    }
    if (Math.abs(wheel.x) < 45 || Math.abs(wheel.x) <= Math.abs(wheel.y) * 1.15) return;
    event.preventDefault();
    wheel.handled = true;
    move(wheel.x > 0 ? 1 : -1);
  }, { passive: false });

  document.addEventListener("visibilitychange", () => {
    if (document.hidden) pauseProgress();
    else resumeProgress();
  });

  window.addEventListener("pageshow", (event) => {
    if (!event.persisted) return;
    const restoredStory = readStoryNumber({ allowStored: true });
    if (current !== restoredStory - 1) show(restoredStory - 1);
  });

  player.querySelector("[data-story-share]")?.addEventListener("click", async (event) => {
    const button = event.currentTarget;
    try {
      if (navigator.share) await navigator.share({ title: document.title, url: window.location.href });
      else {
        await navigator.clipboard.writeText(window.location.href);
        button.textContent = "已複製";
        window.setTimeout(() => { button.textContent = "分享"; }, 1600);
      }
    } catch (error) {
      if (error?.name !== "AbortError") button.textContent = "請複製網址";
    }
  });

  const navigationType = window.performance.getEntriesByType?.("navigation")?.[0]?.type;
  show(readStoryNumber({ allowStored: navigationType === "back_forward" }) - 1);
})();
