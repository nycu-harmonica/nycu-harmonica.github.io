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
      setText(description, invite.guild?.description);
      setText(online, String(invite.approximate_presence_count));
      setText(members, String(invite.approximate_member_count));
      setText(status, '已連線 Discord，顯示目前的約略上線與成員人數。');
      card.dataset.live = 'true';
    } catch (error) {
      setText(online, '—');
      setText(members, '—');
      setText(status, '暫時無法取得即時人數；邀請連結仍可正常使用。');
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
