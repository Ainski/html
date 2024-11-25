document.addEventListener('DOMContentLoaded', function() {
    // 欢迎信息
    alert('欢迎访问您的个人主页！');
    
    // 动态加载帖子
    loadPosts();

    // 点赞功能
    document.querySelectorAll('.like-button').forEach(button => {
        button.addEventListener('click', function() {
            const post = this.closest('.post');
            const likes = post.querySelector('.likes');
            const currentLikes = parseInt(likes.textContent, 10);
            likes.textContent = currentLikes + 1;

            // 显示感谢消息
            alert('感谢您的点赞！');

            // 添加动画效果
            this.classList.add('liked');
            setTimeout(() => {
                this.classList.remove('liked');
            }, 500);

            // 更新点赞按钮样式
            this.style.transform = 'scale(1.2)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 500);
        });
    });

    // 显示/隐藏帖子详情
    document.querySelectorAll('.post').forEach(post => {
        post.querySelector('.toggle-details').addEventListener('click', function() {
            const details = post.querySelector('.details');
            if (details.style.display === 'none') {
                details.style.display = 'block';
                this.textContent = '隐藏详情';
            } else {
                details.style.display = 'none';
                this.textContent = '显示详情';
            }
        });
    });
});

function loadPosts() {
    // 模拟从服务器加载帖子
    const posts = [
        {
            title: '帖子标题1',
            summary: '帖子内容摘要1...',
            details: '这里是帖子的详细内容1...'
        },
        {
            title: '帖子标题2',
            summary: '帖子内容摘要2...',
            details: '这里是帖子的详细内容2...'
        }
        // 更多帖子...
    ];

    const postsContainer = document.querySelector('.posts');
    posts.forEach(post => {
        const postElement = document.createElement('article');
        postElement.className = 'post';
        postElement.innerHTML = `
            <h4>${post.title}</h4>
            <p>${post.summary}</p>
            <button class="toggle-details">显示详情</button>
            <div class="details">${post.details}</div>
            <button class="like-button">点赞</button>
            <span class="likes">0</span>
        `;
        postsContainer.appendChild(postElement);
    });
}