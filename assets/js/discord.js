const card = document.querySelector('[data-discord-card]');

if (card) {
  const online = card.querySelector('[data-discord-online]');
  const members = card.querySelector('[data-discord-members]');
  const status = card.querySelector('[data-discord-status]');
  const name = card.querySelector('[data-discord-name]');
  const description = card.querySelector('[data-discord-description]');
  const copyButton = card.querySelector('[data-copy-invite]');

  const setText = (element, value) => {
    if (element && typeof value === 'string' && value.trim()) element.textContent = value.trim();
  };

  const loadDiscord = async () => {
    try {
      const controller = new AbortController();
      const timeout = window.setTimeout(() => controller.abort(), 6000);
      const response = await fetch(card.dataset.apiUrl, {
        headers: { Accept: 'application/json' },
        mode: 'cors',
        signal: controller.signal,
      });
      window.clearTimeout(timeout);
      if (!response.ok) throw new Error(`Discord API ${response.status}`);

      const invite = await response.json();
      setText(name, invite.guild?.name);
      // 伺服器描述常帶官網網址；這頁本來就在官網上，只留說明文字。
      setText(description, String(invite.guild?.description || '').replace(/\s*https?:\/\/\S+/g, '').replace(/\s*@\s*/g, '＠'));
      const onlineCount = Number(invite.approximate_presence_count);
      const memberCount = Number(invite.approximate_member_count);
      if (!(memberCount > 0)) {
        // 拿到 0 或缺值時不顯示人數，避免看起來像沒有人。
        card.dataset.live = 'empty';
        setText(status, '伺服器已開放加入，進去和大家打聲招呼吧！');
        return;
      }
      setText(online, String(Number.isFinite(onlineCount) ? onlineCount : 0));
      setText(members, String(memberCount));
      setText(status, '人數由 Discord 即時提供，為約略值。');
      card.dataset.live = 'true';
    } catch (error) {
      setText(status, '暫時無法取得 Discord 人數，邀請連結照常可以使用。');
      card.dataset.live = 'false';
    }
  };

  copyButton?.addEventListener('click', async () => {
    const inviteURL = copyButton.dataset.inviteUrl;
    try {
      await navigator.clipboard.writeText(inviteURL);
      copyButton.textContent = '已複製邀請連結';
      window.setTimeout(() => { copyButton.textContent = '複製邀請連結'; }, 2200);
    } catch (error) {
      window.location.href = inviteURL;
    }
  });

  loadDiscord();
}
