import Swiper from "swiper";
import { A11y, Autoplay, Keyboard } from "swiper/modules";

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
  const swiperElement = player?.querySelector(".portal-story-swiper");
  if (!player || !swiperElement) return;

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const defaultDuration = Number(player.dataset.defaultDuration) || 7000;
  const progress = [...player.querySelectorAll("[data-story-progress] span")];
  const announcer = player.querySelector("[data-story-announcer]");
  const storyStorageKey = `portal-story:${window.location.pathname}`;

  function readStoryNumber({ allowStored = false } = {}) {
    const requested = Number(new URL(window.location.href).searchParams.get("story"));
    if (Number.isInteger(requested) && requested >= 1 && requested <= progress.length) return requested;
    if (allowStored) {
      try {
        const stored = Number(window.sessionStorage.getItem(storyStorageKey));
        if (Number.isInteger(stored) && stored >= 1 && stored <= progress.length) return stored;
      } catch (_error) {
        // Some embedded browsers disable sessionStorage; the URL remains authoritative.
      }
    }
    return 1;
  }

  const navigationType = window.performance.getEntriesByType?.("navigation")?.[0]?.type;
  const initialStory = readStoryNumber({ allowStored: navigationType === "back_forward" });

  const swiper = new Swiper(swiperElement, {
    modules: [A11y, Autoplay, Keyboard],
    speed: reducedMotion ? 0 : 420,
    resistanceRatio: 0.72,
    longSwipesRatio: 0.18,
    noSwiping: true,
    noSwipingSelector: ".swiper-no-swiping",
    touchStartPreventDefault: false,
    initialSlide: initialStory - 1,
    keyboard: { enabled: true },
    a11y: { enabled: true, slideLabelMessage: "限時動態 {{index}} / {{slidesLength}}" },
    autoplay: reducedMotion ? false : {
      delay: defaultDuration,
      disableOnInteraction: false,
      pauseOnMouseEnter: true,
      stopOnLastSlide: true,
    },
    on: {
      init(instance) { updateStory(instance); },
      slideChange(instance) { updateStory(instance); },
      autoplayTimeLeft(instance, time, percentage) {
        const bar = progress[instance.activeIndex]?.querySelector("i");
        if (bar) bar.style.transform = `scaleX(${1 - percentage})`;
      },
    },
  });

  function updateStory(instance) {
    progress.forEach((item, index) => {
      item.classList.toggle("is-complete", index < instance.activeIndex);
      item.classList.toggle("is-active", index === instance.activeIndex);
      const bar = item.querySelector("i");
      if (bar) bar.style.transform = index < instance.activeIndex ? "scaleX(1)" : "scaleX(0)";
    });
    const activeSlide = instance.slides[instance.activeIndex];
    const storyNumber = instance.activeIndex + 1;
    const duration = Number(activeSlide?.dataset.storyDuration) || defaultDuration;
    if (instance.params.autoplay) instance.params.autoplay.delay = duration;
    player.querySelectorAll("video").forEach((video) => {
      if (video.closest(".swiper-slide") === activeSlide) video.play().catch(() => {});
      else { video.pause(); video.currentTime = 0; }
    });
    const url = new URL(window.location.href);
    if (storyNumber > 1) url.searchParams.set("story", String(storyNumber));
    else url.searchParams.delete("story");
    window.history.replaceState(window.history.state, "", url);
    try { window.sessionStorage.setItem(storyStorageKey, String(storyNumber)); } catch (_error) {}
    if (announcer) announcer.textContent = `${storyNumber} / ${instance.slides.length}：${activeSlide?.dataset.storyTitle || "竹韻限時動態"}`;
  }

  window.addEventListener("pageshow", (event) => {
    if (!event.persisted) return;
    const restoredStory = readStoryNumber({ allowStored: true });
    if (swiper.activeIndex !== restoredStory - 1) swiper.slideTo(restoredStory - 1, 0);
  });

  let holding = false;
  let holdStartedAt = 0;
  let holdStartedOnTapZone = false;
  let suppressTap = false;
  player.querySelector("[data-story-prev]")?.addEventListener("click", () => {
    if (suppressTap) { suppressTap = false; return; }
    swiper.slidePrev();
  });
  player.querySelector("[data-story-next]")?.addEventListener("click", () => {
    if (suppressTap) { suppressTap = false; return; }
    swiper.slideNext();
  });

  const pause = (event) => {
    if (event.pointerType === "mouse" && event.button !== 0) return;
    if (event.target.closest?.("a, [data-story-share]")) return;
    holding = true;
    holdStartedAt = performance.now();
    holdStartedOnTapZone = Boolean(event.target.closest?.("[data-story-prev], [data-story-next]"));
    player.classList.add("is-paused");
    swiper.autoplay?.pause();
  };
  const resume = () => {
    if (!holding) return;
    suppressTap = holdStartedOnTapZone && performance.now() - holdStartedAt > 250;
    holding = false;
    player.classList.remove("is-paused");
    swiper.autoplay?.resume();
  };
  player.addEventListener("pointerdown", pause);
  player.addEventListener("pointerup", resume);
  player.addEventListener("pointercancel", resume);
  player.addEventListener("pointerleave", resume);

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
})();
