const vscode = acquireVsCodeApi();

const searchQueryInput = document.getElementById('search-query');
const categoryFilterSelect = document.getElementById('category-filter');
const searchButton = document.getElementById('search-button');
const memoriesContainer = document.getElementById('memories-container');
const detailContainer = document.getElementById('memory-detail');
const backToListButton = document.getElementById('back-to-list');

const newCategoryNameInput = document.getElementById('new-category-name');
const addCategoryButton = document.getElementById('add-category-button');
const categoryList = document.getElementById('category-list');

searchButton.addEventListener('click', () => {
    performSearch();
});

addCategoryButton.addEventListener('click', () => {
    const newCategoryName = newCategoryNameInput.value;
    if (newCategoryName) {
        vscode.postMessage({
            command: 'addCategory',
            categoryName: newCategoryName
        });
        newCategoryNameInput.value = ''; // Clear input
    }
});

function performSearch() {
    const query = searchQueryInput.value;
    const category = categoryFilterSelect.value;
    vscode.postMessage({
        command: 'searchMemories',
        query: query,
        category: category
    });
}

function updateCategoryList(categories) {
    categoryList.innerHTML = '';
    categories.forEach(category => {
        const li = document.createElement('li');
        li.innerText = category;
        categoryList.appendChild(li);
    });
}

function renderMemoryVisualization(data) {
    const chartContainer = document.getElementById('visualization-chart');
    chartContainer.innerHTML = ''; // Clear previous chart

    if (!data || Object.keys(data).length === 0) {
        chartContainer.innerHTML = '<p>No visualization data available.</p>';
        return;
    }

    const ul = document.createElement('ul');
    for (const category in data) {
        const li = document.createElement('li');
        li.innerText = `${category}: ${data[category]} memories`;
        ul.appendChild(li);
    }
    chartContainer.appendChild(ul);
}

window.addEventListener('message', event => {
    const message = event.data; // The JSON data our extension sent

    switch (message.command) {
        case 'updateMemories':
            memoriesContainer.innerHTML = ''; // Clear the container
            detailContainer.style.display = 'none'; // Hide detail view initially
            memoriesContainer.style.display = 'block'; // Show list view

            if (message.memories && message.memories.length > 0) {
                for (const memory of message.memories) {
                    const memoryElement = document.createElement('div');
                    memoryElement.className = 'memory-item';
                    memoryElement.innerHTML = `
                        <h2>${memory.title}</h2>
                        <p>${memory.content}</p>
                    `;
                    memoryElement.addEventListener('click', () => {
                        // Populate detail view
                        document.getElementById('detail-title').innerText = memory.title;
                        document.getElementById('detail-content').innerText = memory.content;
                        document.getElementById('detail-category').innerText = memory.category;
                        document.getElementById('detail-importance').innerText = memory.importance;
                        document.getElementById('detail-created-at').innerText = new Date(memory.created_at).toLocaleString();
                        document.getElementById('detail-last-accessed').innerText = new Date(memory.last_accessed).toLocaleString();
                        document.getElementById('detail-tags').innerText = memory.tags.join(', ');

                        // Show detail view and hide list view
                        memoriesContainer.style.display = 'none';
                        detailContainer.style.display = 'block';
                    });
                    memoriesContainer.appendChild(memoryElement);
                }
            } else {
                memoriesContainer.innerHTML = '<p>No memories found.</p>';
            }
            break;
        case 'updateCategories':
            updateCategoryList(message.categories);
            break;
        case 'updateVisualization':
            renderMemoryVisualization(message.data);
            break;
        case 'updateAnalytics':
            renderMemoryAnalytics(message.data);
            break;
    }
});

function renderMemoryAnalytics(data) {
    const analyticsContainer = document.getElementById('analytics-data');
    analyticsContainer.innerHTML = '';

    if (!data || Object.keys(data).length === 0) {
        analyticsContainer.innerHTML = '<p>No analytics data available.</p>';
        return;
    }

    const ul = document.createElement('ul');
    for (const key in data) {
        const li = document.createElement('li');
        li.innerText = `${key}: ${JSON.stringify(data[key])}`;
        ul.appendChild(li);
    }
    analyticsContainer.appendChild(ul);
}

backToListButton.addEventListener('click', () => {
    detailContainer.style.display = 'none';
    memoriesContainer.style.display = 'block';
});