// 跟踪鼠标位置
let mouseX = 0;
let mouseY = 0;
let lastMouseX = 0;
let lastMouseY = 0;
let moveSpeed = 0;
let moveAngle = 0;

// 监听鼠标移动
document.addEventListener("mousemove", (e) => {
  // 计算鼠标移动速度和角度
  const dx = e.clientX - lastMouseX;
  const dy = e.clientY - lastMouseY;
  moveSpeed = Math.sqrt(dx * dx + dy * dy);
  moveAngle = Math.atan2(dy, dx);

  mouseX = e.clientX;
  mouseY = e.clientY;
  lastMouseX = mouseX;
  lastMouseY = mouseY;
});

// 创建樱花元素
function createSakura() {
  const sakura = document.createElement("span");
  sakura.className = "sakura";

  // 初始位置和大小
  const startPositionLeft = Math.random() * window.innerWidth;
  const size = Math.random() * 15 + 10;
  let posX = startPositionLeft;
  let posY = -50;
  let rotation = Math.random() * 360;
  let velocityX = (Math.random() - 0.5) * 2;
  let velocityY = Math.random() * 2 + 1;

  sakura.style.width = size + "px";
  sakura.style.height = size + "px";

  // 动画更新函数
  function updatePosition() {
    // 受鼠标移动影响的偏移量
    if (moveSpeed > 0) {
      const mouseInfluence = Math.min(moveSpeed / 10, 5);
      velocityX += Math.cos(moveAngle) * mouseInfluence * 0.1;
      velocityY += Math.sin(moveAngle) * mouseInfluence * 0.1;
    }

    // 添加自然飘落效果
    velocityX += (Math.random() - 0.5) * 0.3;
    velocityY += Math.random() * 0.1;

    // 限制速度
    velocityX = Math.max(Math.min(velocityX, 5), -5);
    velocityY = Math.max(Math.min(velocityY, 5), 0.5);

    // 更新位置
    posX += velocityX;
    posY += velocityY;
    rotation += velocityX * 2;

    // 更新样式
    sakura.style.left = posX + "px";
    sakura.style.top = posY + "px";
    sakura.style.transform = `rotate(${rotation}deg)`;

    // 检查是否超出屏幕
    if (
      posY < window.innerHeight &&
      posX > -50 &&
      posX < window.innerWidth + 50
    ) {
      requestAnimationFrame(updatePosition);
    } else {
      sakura.remove();
    }
  }

  // 将樱花添加到容器中
  const container = document.querySelector(".sakura-container");
  container.appendChild(sakura);

  // 开始动画
  requestAnimationFrame(updatePosition);
}

// 初始化樱花效果
function initSakura() {
  // 创建樱花容器
  if (!document.querySelector(".sakura-container")) {
    const container = document.createElement("div");
    container.className = "sakura-container";
    document.body.appendChild(container);
  }

  // 持续创建樱花
  setInterval(createSakura, 300);
}

// 页面加载完成后启动樱花效果
document.addEventListener("DOMContentLoaded", initSakura);
// 原有的鼠标跟踪代码保持不变...

// 添加点击绽放效果
document.addEventListener("click", (e) => {
  createBurst(e.clientX, e.clientY);
});

// 创建绽放效果
function createBurst(x, y) {
  const burstCount = 12; // 绽放的花瓣数量
  const burstSize = 20; // 花瓣大小
  const burstRadius = 100; // 绽放半径

  for (let i = 0; i < burstCount; i++) {
    const angle = (i / burstCount) * Math.PI * 2;
    const velocity = 8; // 初始速度

    const petal = document.createElement("span");
    petal.className = "sakura burst-petal";

    // 设置初始位置为点击位置
    petal.style.left = x + "px";
    petal.style.top = y + "px";
    petal.style.width = burstSize + "px";
    petal.style.height = burstSize + "px";

    let posX = x;
    let posY = y;
    let velocityX = Math.cos(angle) * velocity;
    let velocityY = Math.sin(angle) * velocity;
    let rotation = Math.random() * 360;
    let opacity = 1;
    let scale = 1;

    // 动画更新函数
    function updateBurstPetal() {
      // 更新位置和速度
      velocityX *= 0.98; // 水平速度衰减
      velocityY *= 0.98; // 垂直速度衰减
      velocityY += 0.1; // 添加重力效果

      posX += velocityX;
      posY += velocityY;

      // 旋转和缩放效果
      rotation += velocityX * 2;
      scale *= 0.98;
      opacity *= 0.96;

      // 更新样式
      petal.style.transform = `translate(-50%, -50%) rotate(${rotation}deg) scale(${scale})`;
      petal.style.left = posX + "px";
      petal.style.top = posY + "px";
      petal.style.opacity = opacity;

      // 当透明度足够低时移除花瓣
      if (opacity > 0.1) {
        requestAnimationFrame(updateBurstPetal);
      } else {
        petal.remove();
      }
    }

    // 添加到容器
    const container = document.querySelector(".sakura-container");
    container.appendChild(petal);

    // 开始动画
    requestAnimationFrame(updateBurstPetal);
  }

  // 创建中心光效
  const burst = document.createElement("div");
  burst.className = "burst-effect";
  burst.style.left = x + "px";
  burst.style.top = y + "px";

  const container = document.querySelector(".sakura-container");
  container.appendChild(burst);

  // 动画结束后移除光效
  setTimeout(() => burst.remove(), 1000);
}
