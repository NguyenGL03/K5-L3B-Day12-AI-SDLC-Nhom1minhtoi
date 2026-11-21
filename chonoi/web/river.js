/* Cảnh sông vẽ theo snapshot. Nền được vẽ lại khi kích thước khung đổi. */
(() => {
  "use strict";

  const backdrop = document.createElement("canvas");
  let backdropSize = "";

  function ellipse(ctx, x, y, rx, ry, color, angle = 0) {
    ctx.fillStyle = color;
    ctx.beginPath(); ctx.ellipse(x, y, rx, ry, angle, 0, Math.PI * 2); ctx.fill();
  }

  function polygon(ctx, color, points) {
    ctx.fillStyle = color;
    ctx.beginPath(); ctx.moveTo(...points[0]);
    for (const point of points.slice(1)) ctx.lineTo(...point);
    ctx.closePath(); ctx.fill();
  }

  function paintBackdrop(width, height, surface, scale) {
    const key = `${width}/${height}/${surface}/${scale}/${devicePixelRatio}`;
    if (key === backdropSize) return;
    backdropSize = key;
    const density = devicePixelRatio || 1;
    backdrop.width = Math.ceil(width * density);
    backdrop.height = Math.ceil(height * density);
    const ctx = backdrop.getContext("2d");
    ctx.scale(density, density);

    const sky = ctx.createLinearGradient(0, 0, 0, surface);
    sky.addColorStop(0, "#7daab6"); sky.addColorStop(1, "#ffd9a3");
    ctx.fillStyle = sky; ctx.fillRect(0, 0, width, surface);
    ellipse(ctx, width * 0.78, surface * 0.39, scale * 1.35, scale * 1.35, "#ffe6b5");
    for (let i = 0; i < 28; i++) {
      const x = i * width / 27;
      const rise = (0.6 + (Math.sin(i * 1.43) + 1) * 0.4) * scale;
      ellipse(ctx, x, surface - rise * 0.4, width / 24, rise, "#668f86");
    }
    for (let i = 0; i < 13; i++) {
      const x = (i * 0.081 + 0.018) * width;
      const y = surface - scale * (i % 3 === 0 ? 1.6 : 0.9);
      ctx.fillStyle = "#315f59"; ctx.fillRect(x - 1, y, 2, surface - y);
      ellipse(ctx, x, y, scale * 1.25, scale * 0.52, "#397167", -0.18);
    }

    const water = ctx.createLinearGradient(0, surface, 0, height);
    water.addColorStop(0, "#399d94"); water.addColorStop(0.38, "#1e666c");
    water.addColorStop(1, "#102d46");
    ctx.fillStyle = water; ctx.fillRect(0, surface, width, height - surface);
    for (let i = 0; i < 7; i++) {
      const x = width * (i / 7 + 0.04);
      polygon(ctx, "rgba(255,235,180,.045)", [[x, surface], [x + scale * 2, surface],
        [x + scale * 8, height * 0.82], [x + scale * 4, height * 0.82]]);
    }
    for (let i = 0; i < 16; i++) {
      const x = (i * 0.073 + 0.02) * width;
      ellipse(ctx, x, height - scale * (i % 3) * 0.28, scale * 3.4, scale * 0.75, "#173c50");
    }
  }

  function drawPlant(ctx, node, x, surface, scale, accent) {
    ctx.save(); ctx.translate(x, surface); ctx.scale(scale, scale);
    ctx.globalAlpha = node.ready ? 1 : 0.37;
    ellipse(ctx, 0, 0.17, 1.28, 0.22, "#195d54");
    if (node.kind === "bong_sung") {
      ellipse(ctx, -0.45, 0, 0.74, 0.22, "#629553", -0.1);
      ellipse(ctx, 0.53, 0.04, 0.64, 0.19, "#7baa60", 0.13);
      polygon(ctx, "#399d94", [[0.59, 0.03], [1.05, -0.15], [1.16, 0.09]]);
      for (const angle of [-1.08, -0.64, -0.23, 0.23, 0.64, 1.08]) {
        ctx.save(); ctx.translate(0, -0.11); ctx.rotate(angle);
        ellipse(ctx, 0, -0.44, 0.18, 0.49, angle < 0 ? "#ec88a6" : "#ffb1bd");
        ctx.restore();
      }
      ellipse(ctx, 0, -0.19, 0.22, 0.12, "#ffdc88");
    } else {
      for (const x of [-0.62, -0.08, 0.52]) {
        polygon(ctx, "#3e764e", [[x - 0.13, 0], [x - 0.37, -0.7], [x + 0.23, -0.22], [x + 0.08, 0]]);
        ellipse(ctx, x, -0.73 - Math.abs(x) * 0.3, 0.21, 0.15, accent);
      }
    }
    ctx.restore();
  }

  function drawFish(ctx, fish, x, y, scale, tick, color) {
    ctx.save(); ctx.translate(x, y); ctx.rotate(fish.heading_deg * Math.PI / 180);
    const size = scale * (fish.kind === "ca_loc" ? 1.15 : 0.85);
    const count = fish.kind === "ca_loc" ? 1 : fish.kind === "ca_keo" ? 2 : 3;
    ctx.scale(size, size);
    for (let i = count - 1; i >= 0; i--) {
      ctx.save(); ctx.translate(-i * 0.88, i === 1 ? -0.55 : i === 2 ? 0.5 : 0);
      ctx.globalAlpha = i ? 0.72 : 1;
      polygon(ctx, color, [[-0.67, 0], [-1.4, -0.45 + Math.sin(tick / 8 + i) * 0.1], [-1.25, 0.38]]);
      polygon(ctx, "#52838a", [[-0.45, -0.14], [-0.13, -0.59], [0.32, -0.22]]);
      ellipse(ctx, 0, 0, 0.9, fish.kind === "ca_keo" ? 0.25 : 0.35, color);
      ellipse(ctx, 0.15, 0.13, 0.55, 0.13, "rgba(239,246,218,.35)");
      ellipse(ctx, 0.54, -0.07, 0.12, 0.12, "#fcf5da");
      ellipse(ctx, 0.57, -0.07, 0.06, 0.07, "#102b3a");
      ctx.restore();
    }
    ctx.restore();
  }

  function drawDiver(ctx, player, x, y, scale, tick) {
    ctx.save(); ctx.translate(x, y);
    ctx.rotate(player.at_surface ? player.heading_deg > 90 && player.heading_deg < 270 ? Math.PI : 0 : player.heading_deg * Math.PI / 180);
    ctx.scale(scale, scale);
    const flutter = Math.sin(tick / 4) * 0.12;
    polygon(ctx, "#ef9a53", [[-0.6, -0.08], [-1.5, -0.3 + flutter], [-1.36, 0.12], [-0.48, 0.25]]);
    ellipse(ctx, -0.1, 0.02, 0.87, 0.38, "#516a83");
    ellipse(ctx, -0.31, -0.31, 0.6, 0.15, "#d6af6a");
    ellipse(ctx, 0.6, -0.02, 0.45, 0.43, "#f3b780");
    ellipse(ctx, 0.79, -0.08, 0.31, 0.22, "#173e50");
    ellipse(ctx, 0.88, -0.14, 0.11, 0.06, "#b8ecdf");
    ctx.restore();
  }

  function draw(ctx, state, view, kindColor) {
    const { x, y, width, height, surface, scale, sx, sy } = view;
    const tick = state.phase_tick;
    paintBackdrop(width, height, surface - y, scale);
    ctx.drawImage(backdrop, x, y, width, height);
    ctx.lineWidth = 1.5;
    ctx.strokeStyle = "rgba(235,251,218,.54)";
    ctx.beginPath(); ctx.moveTo(x, surface); ctx.lineTo(x + width, surface); ctx.stroke();
    for (let i = 0; i < 14; i++) {
      const px = x + ((i * width / 14 + tick * 0.21) % width);
      ctx.beginPath(); ctx.moveTo(px, surface + 4); ctx.lineTo(Math.min(px + scale * 1.65, x + width), surface + 4); ctx.stroke();
    }

    const [dx] = state.meta.dock_pos || [2, 0];
    const dock = sx(dx);
    ctx.fillStyle = "#493d3a";
    ctx.fillRect(dock - scale, surface - scale, scale * 0.28, scale * 1.9);
    ctx.fillRect(dock + scale, surface - scale, scale * 0.28, scale * 1.9);
    ctx.fillStyle = "#b5825d"; ctx.fillRect(dock - scale * 1.55, surface - scale * 0.64, scale * 3.1, scale * 0.63);
    ctx.fillStyle = "#805740"; ctx.fillRect(dock - scale * 0.83, surface - scale * 2, scale * 1.66, scale * 1.39);
    polygon(ctx, "#bb6952", [[dock - scale * 1.25, surface - scale * 1.93], [dock, surface - scale * 2.95], [dock + scale * 1.25, surface - scale * 1.93]]);

    for (const node of state.nodes) {
      drawPlant(ctx, node, sx(node.pos[0]), surface, scale, kindColor(node.kind));
    }
    for (const fish of state.fish) drawFish(ctx, fish, sx(fish.pos[0]), sy(fish.pos[1]), scale, tick, kindColor(fish.kind));
    for (const monster of state.monsters || []) {
      const mx = sx(monster.pos[0]), my = sy(monster.pos[1]);
      const color = monster.state === "chase" ? "#b29cce" : "#819b65";
      polygon(ctx, color, [[mx - 0.5 * scale, my], [mx - 2.7 * scale, my - 0.4 * scale], [mx - 1.5 * scale, my + 0.4 * scale]]);
      ellipse(ctx, mx, my, scale * 1.55, scale * 0.48, color);
      ellipse(ctx, mx + scale, my - scale * 0.25, scale * 0.13, scale * 0.13, "#f9d880");
    }
    for (const event of state.events || []) {
      if (!["fish_spawned", "node_spawned"].includes(event.name) || event.day !== state.day) continue;
      const age = state.tick - event.tick;
      if (age < 0 || age > 45) continue;
      const entity = (event.name === "fish_spawned" ? state.fish : state.nodes).find(item => item.id === event.data.id);
      if (!entity) continue;
      ctx.strokeStyle = `rgba(246,226,172,${0.7 * (1 - age / 45)})`;
      ctx.beginPath(); ctx.arc(sx(entity.pos[0]), sy(entity.pos[1]), scale * (0.8 + age / 32), 0, Math.PI * 2); ctx.stroke();
    }
    const player = state.player;
    const px = sx(player.pos[0]), py = sy(player.pos[1]);
    if (!player.at_surface) {
      for (let i = 0; i < 4; i++) {
        const rise = (tick / 17 + i * 0.7) % 3;
        ellipse(ctx, px + Math.sin(rise * 3 + i) * scale * 0.42, py - (rise + 0.6) * scale,
          scale * 0.12, scale * 0.12, `rgba(223,251,244,${0.65 - rise / 6})`);
      }
    }
    if (!(player.invuln_ticks > 0 && Math.floor(state.tick / 5) % 2)) drawDiver(ctx, player, px, py, scale, tick);
  }

  window.ChonoiRiver = { draw };
})();
