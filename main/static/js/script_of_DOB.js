// script.js
document.addEventListener("DOMContentLoaded", function () {
  const commentForm = document.getElementById("comment-form");
  const commentInput = document.getElementById("comment-input");
  const commentsList = document.getElementById("comments-list");

  // 初始评论数据
  const comments = [
    {  }
    
  ];

  // 渲染评论区
  function renderComments() {
    commentsList.innerHTML = ""; // 清空当前评论区
    comments.forEach((comment) => {
      const commentDiv = document.createElement("div");
      commentDiv.classList.add("comment");

      const usernameSpan = document.createElement("span");
      usernameSpan.classList.add("username");
      usernameSpan.textContent = comment.username;

      const textP = document.createElement("p");
      textP.textContent = comment.text;

      commentDiv.appendChild(usernameSpan);
      commentDiv.appendChild(textP);
      commentsList.appendChild(commentDiv);
    });
  }

  // 提交评论
  commentForm.addEventListener("submit", function (event) {
    event.preventDefault();  // 阻止表单默认提交
    const newComment = commentInput.value.trim();
    if (newComment) {
      comments.push({ username: "当前用户", text: newComment });
      commentInput.value = "";  // 清空输入框
      renderComments();  // 重新渲染评论区
    }
  });

  // 初始渲染评论
  renderComments();
});