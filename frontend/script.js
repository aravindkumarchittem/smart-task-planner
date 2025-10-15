class SmartTaskPlanner {
    constructor() {
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        const form = document.getElementById('goalForm');
        form.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        const goal = document.getElementById('goalInput').value.trim();
        const timeline = document.getElementById('timelineInput').value.trim();
        
        if (!goal) {
            this.showError('Please enter a goal');
            return;
        }

        this.showLoading(true);
        this.hideError();
        this.hideResult();

        try {
            const plan = await this.generatePlan(goal, timeline);
            this.displayPlan(plan);
        } catch (error) {
            this.showError('Failed to generate plan. Please try again. ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }

    async generatePlan(goal, timeline) {
const response = await fetch('http://localhost:8000/generate-plan', {            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                goal: goal,
                timeline: timeline || undefined
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    displayPlan(plan) {
        // Update goal summary
        document.getElementById('goalTitle').textContent = plan.goal;
        document.getElementById('totalDuration').textContent = `Total: ${plan.total_duration}`;
        
        // Generate task list
        this.generateTaskList(plan.tasks);
        
        // Generate timeline
        this.generateTimeline(plan.tasks);
        
        // Show result section
        this.showResult();
    }

    generateTaskList(tasks) {
        const taskList = document.getElementById('taskList');
        taskList.innerHTML = '';

        tasks.forEach(task => {
            const taskItem = document.createElement('div');
            taskItem.className = 'task-item';
            
            taskItem.innerHTML = `
                <div class="task-header">
                    <div class="task-number">${task.id}</div>
                    <div class="task-description">${task.description}</div>
                </div>
                <div class="task-meta">
                    <span class="meta-badge">
                        <i class="fas fa-clock"></i> ${task.duration}
                    </span>
                    <span class="meta-badge">
                        <i class="fas fa-calendar"></i> ${task.start_date} - ${task.end_date}
                    </span>
                    ${task.dependencies.length > 0 ? `
                        <span class="meta-badge dependencies">
                            <i class="fas fa-link"></i> Depends on: ${task.dependencies.join(', ')}
                        </span>
                    ` : ''}
                </div>
            `;
            
            taskList.appendChild(taskItem);
        });
    }

    generateTimeline(tasks) {
        const timeline = document.getElementById('timeline');
        timeline.innerHTML = '';

        tasks.forEach(task => {
            const timelineItem = document.createElement('div');
            timelineItem.className = 'timeline-item';
            
            timelineItem.innerHTML = `
                <div class="timeline-dot">${task.id}</div>
                <div class="timeline-content">
                    <h4>${task.description}</h4>
                    <div class="timeline-dates">
                        <i class="fas fa-calendar"></i> ${task.start_date} - ${task.end_date} (${task.duration})
                    </div>
                    ${task.dependencies.length > 0 ? `
                        <div class="timeline-dependencies">
                            <i class="fas fa-link"></i> Requires tasks: ${task.dependencies.join(', ')}
                        </div>
                    ` : ''}
                </div>
            `;
            
            timeline.appendChild(timelineItem);
        });
    }

    showLoading(show) {
        const loading = document.getElementById('loading');
        const button = document.getElementById('generateBtn');
        
        if (show) {
            loading.style.display = 'block';
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
        } else {
            loading.style.display = 'none';
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-magic"></i> Generate Task Plan';
        }
    }

    showError(message) {
        const errorAlert = document.getElementById('errorAlert');
        errorAlert.textContent = message;
        errorAlert.style.display = 'block';
    }

    hideError() {
        const errorAlert = document.getElementById('errorAlert');
        errorAlert.style.display = 'none';
    }

    showResult() {
        document.getElementById('result').style.display = 'block';
        // Scroll to result
        document.getElementById('result').scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }

    hideResult() {
        document.getElementById('result').style.display = 'none';
    }
}

// Initialize the application when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new SmartTaskPlanner();
});