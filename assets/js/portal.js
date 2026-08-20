(() => {
  "use strict";

  const stage = document.querySelector("[data-screen-stage]");
  if (!stage) return;

  const items = [...document.querySelectorAll("[data-program-item]")];
  const songCount = Number(stage.dataset.songCount || items.length);

  function setCurrentSong(songNumber) {
    const selected = Number.isInteger(songNumber) && songNumber >= 1 && songNumber <= songCount
      ? songNumber
      : 0;
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
  }

  const initialSong = Number(new URL(window.location.href).searchParams.get("song"));
  setCurrentSong(initialSong);

  const fullscreenButton = document.querySelector("[data-fullscreen-button]");
  fullscreenButton?.addEventListener("click", () => {
    if (document.fullscreenElement) document.exitFullscreen?.();
    else stage.requestFullscreen?.();
  });

  document.addEventListener("fullscreenchange", () => {
    if (fullscreenButton) {
      fullscreenButton.textContent = document.fullscreenElement ? "離開全螢幕" : "進入全螢幕";
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key.toLowerCase() === "f") {
      event.preventDefault();
      fullscreenButton?.click();
      return;
    }
    if (/^[0-9]$/.test(event.key)) setCurrentSong(Number(event.key));
    if (event.key === "ArrowRight") {
      setCurrentSong(Math.min(Number(stage.dataset.currentSong) + 1, songCount));
    }
    if (event.key === "ArrowLeft") {
      setCurrentSong(Math.max(Number(stage.dataset.currentSong) - 1, 0));
    }
  });
})();
