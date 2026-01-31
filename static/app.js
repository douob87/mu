// DOM 元素
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const clearBtn = document.getElementById('clearBtn');
const addSongForm = document.getElementById('addSongForm');
const artistInput = document.getElementById('artistInput');
const songNameInput = document.getElementById('songNameInput');
const songsList = document.getElementById('songsList');
const noResults = document.getElementById('noResults');
const messageDiv = document.getElementById('message');

// 頁面載入時取得所有歌曲
document.addEventListener('DOMContentLoaded', () => {
    loadSongs();
});

// 搜尋按鈕事件
searchBtn.addEventListener('click', () => {
    const query = searchInput.value.trim();
    loadSongs(query);
});

// Enter 鍵搜尋
searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const query = searchInput.value.trim();
        loadSongs(query);
    }
});

// 清除搜尋
clearBtn.addEventListener('click', () => {
    searchInput.value = '';
    loadSongs();
});

// 新增歌曲表單提交
addSongForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const artist = artistInput.value.trim();
    const songName = songNameInput.value.trim();

    if (!artist || !songName) {
        showMessage('請填寫歌手和歌名', 'error');
        return;
    }

    try {
        const response = await fetch('/api/songs', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                artist: artist,
                song_name: songName
            })
        });

        if (response.ok) {
            showMessage('歌曲新增成功！', 'success');
            artistInput.value = '';
            songNameInput.value = '';
            loadSongs(); // 重新載入歌曲列表
        } else {
            const error = await response.json();
            showMessage(error.error || '新增失敗', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage('發生錯誤，請稍後再試', 'error');
    }
});

// 載入歌曲列表
async function loadSongs(searchQuery = '') {
    try {
        const url = searchQuery
            ? `/api/songs?search=${encodeURIComponent(searchQuery)}`
            : '/api/songs';

        const response = await fetch(url);
        const songs = await response.json();

        displaySongs(songs);
    } catch (error) {
        console.error('Error:', error);
        showMessage('載入歌曲失敗', 'error');
    }
}

// 顯示歌曲列表
function displaySongs(songs) {
    songsList.innerHTML = '';

    if (songs.length === 0) {
        noResults.style.display = 'block';
        return;
    }

    noResults.style.display = 'none';

    songs.forEach(song => {
        const songItem = createSongElement(song);
        songsList.appendChild(songItem);
    });
}

// 創建歌曲元素
function createSongElement(song) {
    const div = document.createElement('div');
    div.className = 'song-item';
    div.innerHTML = `
        <div class="song-info">
            <div class="song-artist">${escapeHtml(song.artist)}</div>
            <div class="song-name">${escapeHtml(song.song_name)}</div>
            <div class="song-date">${formatDate(song.created_at)}</div>
        </div>
        <button class="btn btn-delete" onclick="deleteSong(${song.id})">刪除</button>
    `;
    return div;
}

// 刪除歌曲
async function deleteSong(id) {
    if (!confirm('確定要刪除這首歌曲嗎？')) {
        return;
    }

    try {
        const response = await fetch(`/api/songs/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showMessage('刪除成功！', 'success');
            loadSongs(); // 重新載入歌曲列表
        } else {
            showMessage('刪除失敗', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage('發生錯誤，請稍後再試', 'error');
    }
}

// 顯示訊息
function showMessage(text, type) {
    messageDiv.textContent = text;
    messageDiv.className = `message ${type}`;
    messageDiv.classList.add('show');

    setTimeout(() => {
        messageDiv.classList.remove('show');
    }, 3000);
}

// 格式化日期
function formatDate(dateString) {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');

    return `${year}-${month}-${day} ${hours}:${minutes}`;
}

// HTML 轉義，防止 XSS 攻擊
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}