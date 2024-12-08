document.addEventListener("DOMContentLoaded", () => {
  // 如果已存在光标效果元素则移除
  const existingEffect = document.querySelector(".cursor-effect");
  if (existingEffect) {
    existingEffect.remove();
  }

  // 创建光标跟随效果元素
  const cursorEffect = document.createElement("div");
  cursorEffect.className = "cursor-effect";
  document.body.appendChild(cursorEffect);

  let cursorVisible = true;
  let requestId = null;

  // 优化的光标位置更新函数
  function updateCursorPosition(e) {
    if (!cursorVisible) {
      cursorEffect.style.opacity = "1";
      cursorVisible = true;
    }

    cancelAnimationFrame(requestId);

    requestId = requestAnimationFrame(() => {
      cursorEffect.style.left = `${e.clientX}px`;
      cursorEffect.style.top = `${e.clientY}px`;
    });
  }

  // 鼠标移出窗口时隐藏光标效果
  function hideCursor() {
    cursorEffect.style.opacity = "0";
    cursorVisible = false;
  }

  // 事件监听
  document.addEventListener("mousemove", updateCursorPosition);
  document.addEventListener("mouseenter", updateCursorPosition);
  document.addEventListener("mouseleave", hideCursor);
  document.addEventListener("mousedown", () => {
    cursorEffect.classList.add("active");
  });
  document.addEventListener("mouseup", () => {
    cursorEffect.classList.remove("active");
  });

  // 交互元素的特殊效果
  const interactiveElements = document.querySelectorAll(`
        button, 
        input, 
        a, 
        textarea, 
        [role="button"],
        [contenteditable="true"]
    `);

  interactiveElements.forEach((element) => {
    element.addEventListener("mouseenter", () => {
      cursorEffect.style.width = "30px";
      cursorEffect.style.height = "30px";
      cursorEffect.style.backgroundColor = "rgba(255, 167, 196, 0.4)";
    });

    element.addEventListener("mouseleave", () => {
      cursorEffect.style.width = "20px";
      cursorEffect.style.height = "20px";
      cursorEffect.style.backgroundColor = "rgba(255, 167, 196, 0.3)";
    });
  });
});
