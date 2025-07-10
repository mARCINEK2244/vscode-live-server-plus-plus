class TodoApp {
    constructor() {
        this.tasks = JSON.parse(localStorage.getItem('todoTasks')) || [];
        this.currentFilter = 'all';
        this.initializeElements();
        this.attachEventListeners();
        this.render();
    }

    initializeElements() {
        this.taskInput = document.getElementById('taskInput');
        this.addButton = document.getElementById('addButton');
        this.taskList = document.getElementById('taskList');
        this.emptyState = document.getElementById('emptyState');
        this.totalTasks = document.getElementById('totalTasks');
        this.completedTasks = document.getElementById('completedTasks');
        this.filterButtons = document.querySelectorAll('.filter-btn');
    }

    attachEventListeners() {
        // Add task button
        this.addButton.addEventListener('click', () => this.addTask());
        
        // Enter key to add task
        this.taskInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.addTask();
            }
        });

        // Filter buttons
        this.filterButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                this.currentFilter = e.target.dataset.filter;
                this.updateFilterButtons();
                this.renderTasks();
            });
        });
    }

    addTask() {
        const taskText = this.taskInput.value.trim();
        
        if (taskText === '') {
            this.taskInput.focus();
            return;
        }

        const newTask = {
            id: Date.now().toString(),
            text: taskText,
            completed: false,
            createdAt: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };

        this.tasks.unshift(newTask);
        this.taskInput.value = '';
        this.saveToLocalStorage();
        this.render();
        
        // Add a little animation feedback
        this.addButton.style.transform = 'scale(0.95)';
        setTimeout(() => {
            this.addButton.style.transform = '';
        }, 150);
    }

    toggleTask(taskId) {
        const task = this.tasks.find(t => t.id === taskId);
        if (task) {
            task.completed = !task.completed;
            this.saveToLocalStorage();
            this.render();
        }
    }

    deleteTask(taskId) {
        this.tasks = this.tasks.filter(t => t.id !== taskId);
        this.saveToLocalStorage();
        this.render();
    }

    getFilteredTasks() {
        switch (this.currentFilter) {
            case 'active':
                return this.tasks.filter(task => !task.completed);
            case 'completed':
                return this.tasks.filter(task => task.completed);
            default:
                return this.tasks;
        }
    }

    updateStats() {
        const total = this.tasks.length;
        const completed = this.tasks.filter(task => task.completed).length;
        
        this.totalTasks.textContent = `${total} ${total === 1 ? 'task' : 'tasks'}`;
        this.completedTasks.textContent = `${completed} completed`;
    }

    updateFilterButtons() {
        this.filterButtons.forEach(button => {
            button.classList.toggle('active', button.dataset.filter === this.currentFilter);
        });
    }

    renderTasks() {
        const filteredTasks = this.getFilteredTasks();
        
        if (filteredTasks.length === 0) {
            this.taskList.style.display = 'none';
            this.emptyState.classList.remove('hidden');
        } else {
            this.taskList.style.display = 'block';
            this.emptyState.classList.add('hidden');
        }

        this.taskList.innerHTML = filteredTasks.map(task => `
            <li class="task-item" data-task-id="${task.id}">
                <div class="task-checkbox ${task.completed ? 'checked' : ''}" 
                     onclick="todoApp.toggleTask('${task.id}')">
                </div>
                <span class="task-text ${task.completed ? 'completed' : ''}">${this.escapeHtml(task.text)}</span>
                <span class="task-time">${task.createdAt}</span>
                <button class="delete-btn" onclick="todoApp.deleteTask('${task.id}')">Delete</button>
            </li>
        `).join('');
    }

    render() {
        this.updateStats();
        this.renderTasks();
    }

    saveToLocalStorage() {
        localStorage.setItem('todoTasks', JSON.stringify(this.tasks));
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the app when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.todoApp = new TodoApp();
});

// Add some keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Focus input with Ctrl/Cmd + /
    if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault();
        document.getElementById('taskInput').focus();
    }
    
    // Clear completed tasks with Ctrl/Cmd + Shift + C
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'C') {
        e.preventDefault();
        if (window.todoApp) {
            window.todoApp.tasks = window.todoApp.tasks.filter(task => !task.completed);
            window.todoApp.saveToLocalStorage();
            window.todoApp.render();
        }
    }
});

// Add a welcome message for first-time users
if (!localStorage.getItem('todoTasks') || JSON.parse(localStorage.getItem('todoTasks')).length === 0) {
    setTimeout(() => {
        const input = document.getElementById('taskInput');
        if (input && input.value === '') {
            input.placeholder = "Try: 'Learn something new today!' ✨";
        }
    }, 1000);
}