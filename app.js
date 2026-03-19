// 配置
const CONFIG = {
    dataPath: './data/',
    defaultDate: new Date().toISOString().split('T')[0],
    categories: {
        'federal': { name: '联邦政策', color: 'bg-red-500', icon: 'fa-landmark' },
        'ai': { name: 'AI教育', color: 'bg-blue-500', icon: 'fa-robot' },
        'higher': { name: '高等教育', color: 'bg-green-500', icon: 'fa-university' },
        'teacher': { name: '师资', color: 'bg-purple-500', icon: 'fa-chalkboard-teacher' },
        'international': { name: '国际学生', color: 'bg-orange-500', icon: 'fa-globe' },
        'stem': { name: 'STEM教育', color: 'bg-teal-500', icon: 'fa-flask' },
        'k12': { name: 'K-12教育', color: 'bg-pink-500', icon: 'fa-school' }
    }
};

// 状态
let currentDate = CONFIG.defaultDate;
let availableDates = [];

// DOM元素
const datePicker = document.getElementById('datePicker');
const newsContainer = document.getElementById('newsContainer');
const loadingState = document.getElementById('loadingState');
const errorState = document.getElementById('errorState');
const emptyState = document.getElementById('emptyState');

// 初始化
async function init() {
    // 设置日期选择器默认值
    datePicker.value = currentDate;
    datePicker.max = currentDate;
    
    // 加载可用日期列表
    await loadAvailableDates();
    
    // 加载今天的新闻
    await loadNews(currentDate);
    
    // 绑定事件
    datePicker.addEventListener('change', (e) => {
        currentDate = e.target.value;
        loadNews(currentDate);
    });
}

// 加载可用日期列表
async function loadAvailableDates() {
    try {
        const response = await fetch(`${CONFIG.dataPath}index.json`);
        if (response.ok) {
            const data = await response.json();
            availableDates = data.dates || [];
            
            // 更新统计
            document.getElementById('totalDays').textContent = availableDates.length;
            if (availableDates.length > 0) {
                document.getElementById('latestUpdate').textContent = availableDates[0];
            }
        }
    } catch (error) {
        console.log('No index.json found');
    }
}

// 加载指定日期的新闻
async function loadNews(date) {
    showLoading();
    
    try {
        const response = await fetch(`${CONFIG.dataPath}${date}.json`);
        
        if (!response.ok) {
            throw new Error('No data for this date');
        }
        
        const data = await response.json();
        renderNews(data);
        
        // 更新统计
        document.getElementById('totalNews').textContent = data.news?.length || 0;
        
    } catch (error) {
        showError();
    }
}

// 渲染新闻列表
function renderNews(data) {
    hideAllStates();
    
    if (!data.news || data.news.length === 0) {
        showEmpty();
        return;
    }
    
    const html = data.news.map((item, index) => {
        const category = CONFIG.categories[item.category] || { 
            name: '其他', 
            color: 'bg-gray-500',
            icon: 'fa-newspaper'
        };
        
        return `
            <article class="news-card bg-white rounded-lg shadow-md p-6 ${item.content && item.content !== item.summary ? 'cursor-pointer' : ''}" ${item.content && item.content !== item.summary ? `onclick="toggleDetails(${index})"` : ''}>
                <div class="flex items-start justify-between">
                    <div class="flex-1">
                        <div class="flex items-center space-x-2 mb-2">
                            <span class="category-badge ${category.color} text-white">
                                <i class="fas ${category.icon} mr-1"></i>${category.name}
                            </span>
                            ${item.source ? `<span class="text-xs text-gray-500">${item.source}</span>` : ''}
                            ${item.original_date ? `<span class="text-xs text-gray-400"><i class="far fa-clock mr-1"></i>${item.original_date}</span>` : ''}
                        </div>
                        <h3 class="text-lg font-semibold text-gray-900 mb-2 hover:text-blue-600 transition">
                            ${item.title}
                        </h3>
                        <p class="text-gray-600 text-sm line-clamp-2" id="summary-${index}">
                            ${item.summary || (item.content ? item.content.substring(0, 200) + '...' : '暂无摘要')}
                        </p>
                        ${item.content && item.content !== item.summary ? `
                        <div id="details-${index}" class="hidden mt-4 pt-4 border-t border-gray-100">
                            <p class="text-gray-700 text-sm mb-3">${item.content}</p>
                        </div>
                        ` : ''}
                        ${item.url ? `
                        <div class="mt-3 pt-3 border-t border-gray-100">
                            <a href="${item.url}" target="_blank" class="inline-flex items-center text-blue-600 hover:text-blue-800 text-sm">
                                查看来源 <i class="fas fa-external-link-alt ml-1"></i>
                            </a>
                        </div>
                        ` : ''}
                    </div>
                    <div class="ml-4 text-right">
                        <span class="text-xs text-gray-400">#${index + 1}</span>
                        ${item.content && item.content !== item.summary ? `
                        <i class="fas fa-chevron-down text-gray-400 mt-2 block transition-transform" id="arrow-${index}"></i>
                        ` : ''}
                    </div>
                </div>
            </article>
        `;
    }).join('');
    
    newsContainer.innerHTML = html;
    newsContainer.classList.remove('hidden');
}

// 展开/收起详情
function toggleDetails(index) {
    const details = document.getElementById(`details-${index}`);
    const arrow = document.getElementById(`arrow-${index}`);
    
    if (details.classList.contains('hidden')) {
        details.classList.remove('hidden');
        arrow.style.transform = 'rotate(180deg)';
    } else {
        details.classList.add('hidden');
        arrow.style.transform = 'rotate(0deg)';
    }
}

// 显示加载状态
function showLoading() {
    hideAllStates();
    loadingState.classList.remove('hidden');
}

// 显示错误状态
function showError() {
    hideAllStates();
    errorState.classList.remove('hidden');
}

// 显示空状态
function showEmpty() {
    hideAllStates();
    emptyState.classList.remove('hidden');
}

// 隐藏所有状态
function hideAllStates() {
    loadingState.classList.add('hidden');
    errorState.classList.add('hidden');
    emptyState.classList.add('hidden');
    newsContainer.classList.add('hidden');
}

// 加载今天
function loadToday() {
    currentDate = CONFIG.defaultDate;
    datePicker.value = currentDate;
    loadNews(currentDate);
}

// 启动应用
document.addEventListener('DOMContentLoaded', init);
