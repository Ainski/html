document.addEventListener("DOMContentLoaded", function () {
  // 获取所有导航按钮和表单容器
  const navButtons = document.querySelectorAll("#navButtons button");
  const forms = document.querySelectorAll(".form-container");

  // 导航切换功能
  navButtons.forEach((button, index) => {
    button.addEventListener("click", () => {
      // 移除所有表单的active类
      forms.forEach((form) => form.classList.remove("active"));
      // 为当前选中的表单添加active类
      forms[index].classList.add("active");
      // 更新按钮样式
      navButtons.forEach((btn) => btn.classList.remove("active"));
      button.classList.add("active");
    });
  });

  // 验证码计时器
  let countdowns = {};

  function startCountdown(buttonId) {
    const button = document.getElementById(buttonId);
    let timeLeft = 60;

    button.disabled = true;
    button.textContent = `${timeLeft}秒后重新发送`;

    countdowns[buttonId] = setInterval(() => {
      timeLeft--;
      if (timeLeft <= 0) {
        clearInterval(countdowns[buttonId]);
        button.disabled = false;
        button.textContent = "发送验证码";
      } else {
        button.textContent = `${timeLeft}秒后重新发送`;
      }
    }, 1000);
  }

  // 邮箱验证
  function validateEmail(email) {
    const pattern = /^[\w\.-]+@[\w\.-]+\.\w+$/;
    return pattern.test(email);
  }

  // 密码验证
  function validatePassword(password) {
    return password.length >= 6;
  }

  // 发送验证码
  async function sendVerificationCode(email, isRegister, buttonId) {
    if (!validateEmail(email)) {
      alert("请输入有效的邮箱地址");
      return;
    }

    try {
      const response = await fetch("/send_code", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: email,
          is_register: isRegister,
        }),
      });

      const data = await response.json();
      alert(data.message);

      if (data.status === "success") {
        startCountdown(buttonId);
      }
    } catch (error) {
      console.error("Error:", error);
      alert("发送验证码失败，请稍后重试");
    }
  }

  // 密码登录表单提交
  document
    .getElementById("passwordLoginForm")
    .addEventListener("submit", async (e) => {
      e.preventDefault();

      const email = document.getElementById("passwordLoginEmail").value;
      const password = document.getElementById("passwordLoginPassword").value;

      if (!validateEmail(email)) {
        alert("请输入有效的邮箱地址");
        return;
      }

      if (!validatePassword(password)) {
        alert("密码长度至少为6位");
        return;
      }

      try {
        const response = await fetch("/login", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: email,
            password: password,
          }),
        });

        const data = await response.json();
        if (data.status === "success") {
          window.location.href = data.redirect;
        } else {
          alert(data.message);
        }
      } catch (error) {
        console.error("Error:", error);
        alert("登录失败，请稍后重试");
      }
    });

  // 邮箱登录发送验证码
  document
    .getElementById("emailLoginSendCode")
    .addEventListener("click", async () => {
      const email = document.getElementById("emailLoginEmail").value;
      await sendVerificationCode(email, false, "emailLoginSendCode");
    });

  // 邮箱登录表单提交
  document
    .getElementById("emailLoginForm")
    .addEventListener("submit", async (e) => {
      e.preventDefault();

      const email = document.getElementById("emailLoginEmail").value;
      const code = document.getElementById("emailLoginCode").value;

      if (!validateEmail(email)) {
        alert("请输入有效的邮箱地址");
        return;
      }

      if (!code) {
        alert("请输入验证码");
        return;
      }

      try {
        const response = await fetch("/login", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: email,
            verification_code: code,
          }),
        });

        const data = await response.json();
        if (data.status === "success") {
          window.location.href = data.redirect;
        } else {
          alert(data.message);
        }
      } catch (error) {
        console.error("Error:", error);
        alert("登录失败，请稍后重试");
      }
    });

  // 注册发送验证码
  document
    .getElementById("registerSendCode")
    .addEventListener("click", async () => {
      const email = document.getElementById("registerEmail").value;
      await sendVerificationCode(email, true, "registerSendCode");
    });

  // 注册表单提交
  document
    .getElementById("registerForm")
    .addEventListener("submit", async (e) => {
      e.preventDefault();

      const email = document.getElementById("registerEmail").value;
      const code = document.getElementById("registerCode").value;
      const username = document.getElementById("registerUsername").value;
      const password = document.getElementById("registerPassword").value;

      if (!validateEmail(email)) {
        alert("请输入有效的邮箱地址");
        return;
      }

      if (!code) {
        alert("请输入验证码");
        return;
      }

      if (!username) {
        alert("请输入用户名");
        return;
      }

      if (!validatePassword(password)) {
        alert("密码长度至少为6位");
        return;
      }

      try {
        const response = await fetch("/register", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: email,
            code: code,
            username: username,
            password: password,
          }),
        });

        const data = await response.json();
        alert(data.message);

        if (data.status === "success") {
          // 注册成功后切换到登录表单
          navButtons[0].click();
        }
      } catch (error) {
        console.error("Error:", error);
        alert("注册失败，请稍后重试");
      }
    });
});