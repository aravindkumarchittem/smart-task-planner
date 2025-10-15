# import os
# import json
# import httpx
# from typing import Dict, Any
# from datetime import datetime, timedelta

# class TaskPlanningService:
#     def __init__(self):
#         self.api_key = os.getenv("PERPLEXITY_API_KEY")
#         self.base_url = "https://api.perplexity.ai/chat/completions"
    
#     async def generate_task_plan(self, goal: str, timeline: str = None) -> Dict[str, Any]:
#         prompt = self._build_prompt(goal, timeline)
        
#         headers = {
#             "Authorization": f"Bearer {self.api_key}",
#             "Content-Type": "application/json"
#         }
        
#         payload = {
#             "model": "llama-3.1-sonar-small-128k-online",  # or another Perplexity model
#             "messages": [
#                 {
#                     "role": "system",
#                     "content": "You are an expert project planner. Break down goals into actionable tasks with realistic timelines and dependencies. Always respond with valid JSON."
#                 },
#                 {
#                     "role": "user", 
#                     "content": prompt
#                 }
#             ],
#             "temperature": 0.7,
#             "max_tokens": 2000
#         }
        
#         try:
#             async with httpx.AsyncClient() as client:
#                 response = await client.post(
#                     self.base_url,
#                     headers=headers,
#                     json=payload,
#                     timeout=30.0
#                 )
                
#                 if response.status_code == 200:
#                     result = response.json()
#                     plan_text = result['choices'][0]['message']['content']
#                     return self._parse_llm_response(plan_text, goal)
#                 else:
#                     print(f"Perplexity API error: {response.status_code} - {response.text}")
#                     return self._generate_fallback_plan(goal)
                    
#         except Exception as e:
#             print(f"Error calling Perplexity API: {str(e)}")
#             return self._generate_fallback_plan(goal)
    
#     def _build_prompt(self, goal: str, timeline: str = None) -> str:
#         today = datetime.now().strftime("%Y-%m-%d")
        
#         base_prompt = f"""
#         Break down this goal into actionable tasks with suggested deadlines and dependencies.
        
#         Goal: "{goal}"
#         Today's date: {today}
#         """
        
#         if timeline:
#             base_prompt += f"\nDesired timeline: {timeline}"
        
#         base_prompt += """
        
#         CRITICAL: You MUST respond with ONLY valid JSON in this exact format, no other text:
#         {
#             "tasks": [
#                 {
#                     "id": 1,
#                     "description": "Very specific actionable task description",
#                     "duration": "2 days",
#                     "start_date": "YYYY-MM-DD",
#                     "end_date": "YYYY-MM-DD",
#                     "dependencies": []
#                 }
#             ],
#             "total_duration": "X days"
#         }
        
#         Guidelines:
#         - Create 4-8 specific, actionable tasks
#         - Make durations realistic
#         - Include logical dependencies between tasks
#         - Calculate dates based on today's date and durations
#         - Ensure total_duration matches the sum of task durations considering dependencies
#         - Tasks should be sequential where dependencies make sense
#         """
        
#         return base_prompt
    
#     def _parse_llm_response(self, response_text: str, goal: str) -> Dict[str, Any]:
#         try:
#             # Clean the response text - remove markdown code blocks if present
#             cleaned_text = response_text.replace('```json', '').replace('```', '').strip()
            
#             # Extract JSON
#             start_idx = cleaned_text.find('{')
#             end_idx = cleaned_text.rfind('}') + 1
            
#             if start_idx == -1 or end_idx == 0:
#                 raise ValueError("No JSON found in response")
                
#             json_str = cleaned_text[start_idx:end_idx]
#             plan_data = json.loads(json_str)
            
#             # Validate and format tasks
#             tasks = []
#             for i, task in enumerate(plan_data.get('tasks', [])):
#                 tasks.append({
#                     "id": i + 1,
#                     "description": task.get('description', f'Task {i+1}'),
#                     "duration": task.get('duration', '1 day'),
#                     "start_date": task.get('start_date', ''),
#                     "end_date": task.get('end_date', ''),
#                     "dependencies": task.get('dependencies', [])
#                 })
            
#             return {
#                 "goal": goal,
#                 "tasks": tasks,
#                 "total_duration": plan_data.get('total_duration', 'Unknown')
#             }
            
#         except (json.JSONDecodeError, ValueError) as e:
#             print(f"Error parsing LLM response: {str(e)}")
#             print(f"Raw response: {response_text}")
#             return self._generate_fallback_plan(goal)
    
#     def _generate_fallback_plan(self, goal: str) -> Dict[str, Any]:
#         """Generate a simple fallback plan if API fails"""
#         today = datetime.now()
        
#         return {
#             "goal": goal,
#             "tasks": [
#                 {
#                     "id": 1,
#                     "description": f"Research and detailed planning for {goal}",
#                     "duration": "2 days",
#                     "start_date": today.strftime("%Y-%m-%d"),
#                     "end_date": (today + timedelta(days=2)).strftime("%Y-%m-%d"),
#                     "dependencies": []
#                 },
#                 {
#                     "id": 2,
#                     "description": f"Execute initial preparation phase",
#                     "duration": "3 days",
#                     "start_date": (today + timedelta(days=2)).strftime("%Y-%m-%d"),
#                     "end_date": (today + timedelta(days=5)).strftime("%Y-%m-%d"),
#                     "dependencies": [1]
#                 },
#                 {
#                     "id": 3,
#                     "description": f"Implement core components",
#                     "duration": "4 days",
#                     "start_date": (today + timedelta(days=5)).strftime("%Y-%m-%d"),
#                     "end_date": (today + timedelta(days=9)).strftime("%Y-%m-%d"),
#                     "dependencies": [2]
#                 },
#                 {
#                     "id": 4,
#                     "description": f"Review, test and finalize",
#                     "duration": "2 days",
#                     "start_date": (today + timedelta(days=9)).strftime("%Y-%m-%d"),
#                     "end_date": (today + timedelta(days=11)).strftime("%Y-%m-%d"),
#                     "dependencies": [3]
#                 }
#             ],
#             "total_duration": "11 days"
#         }
import os
import json
import httpx
import re
from typing import Dict, Any
from datetime import datetime, timedelta

class TaskPlanningService:
    def __init__(self):
        self.api_key = os.getenv("PERPLEXITY_API_KEY")
        self.base_url = "https://api.perplexity.ai/chat/completions"
    
    async def generate_task_plan(self, goal: str, timeline: str = None) -> Dict[str, Any]:
        """Generate task plan using Perplexity AI with proper timeline handling"""
        if self.api_key and self.api_key != "your_perplexity_api_key_here":
            try:
                return await self._generate_with_perplexity(goal, timeline)
            except Exception as e:
                print(f"Perplexity API failed, using fallback: {e}")
                return self._generate_enhanced_fallback(goal, timeline)
        else:
            return self._generate_enhanced_fallback(goal, timeline)
    
    async def _generate_with_perplexity(self, goal: str, timeline: str = None) -> Dict[str, Any]:
        """Generate plan using Perplexity AI"""
        prompt = self._build_llm_prompt(goal, timeline)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert project planner. Create detailed, actionable task breakdowns with realistic timelines and dependencies. Always respond with valid JSON."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            plan_text = result['choices'][0]['message']['content']
            return self._parse_llm_response(plan_text, goal, timeline)
    
    def _build_llm_prompt(self, goal: str, timeline: str = None) -> str:
        """Build detailed prompt for LLM"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        prompt = f"""
        Create a detailed task breakdown for the following goal:

        GOAL: "{goal}"
        TIMELINE: {timeline if timeline else 'Not specified - suggest realistic timeline'}
        TODAY'S DATE: {today}

        CRITICAL REQUIREMENTS:
        1. MUST respect the timeline if provided (e.g., "3 months" = ~90 days, "2 weeks" = 14 days)
        2. Create 6-10 specific, actionable tasks
        3. Include realistic dependencies between tasks
        4. Calculate dates based on today's date and the timeline
        5. Make durations realistic for the type of goal

        RESPONSE FORMAT (JSON only):
        {{
            "tasks": [
                {{
                    "id": 1,
                    "description": "Specific actionable task description",
                    "duration": "X days",
                    "start_date": "YYYY-MM-DD",
                    "end_date": "YYYY-MM-DD",
                    "dependencies": []
                }}
            ],
            "total_duration": "X days (Y weeks, Z months)",
            "timeline_respected": true/false
        }}

        EXAMPLES:
        - For "Learn Spanish in 3 months": 8-12 tasks spanning ~90 days
        - For "Plan wedding in 6 months": 10-15 tasks spanning ~180 days  
        - For "Launch website in 1 month": 6-8 tasks spanning ~30 days

        Now create the plan for: "{goal}" {f"within {timeline}" if timeline else ""}
        """
        return prompt
    
    def _parse_llm_response(self, response_text: str, goal: str, timeline: str) -> Dict[str, Any]:
        """Parse LLM response and validate timeline"""
        try:
            # Extract JSON from response
            cleaned_text = response_text.replace('```json', '').replace('```', '').strip()
            start_idx = cleaned_text.find('{')
            end_idx = cleaned_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")
                
            json_str = cleaned_text[start_idx:end_idx]
            plan_data = json.loads(json_str)
            
            # Validate and format tasks
            tasks = []
            for i, task in enumerate(plan_data.get('tasks', [])):
                tasks.append({
                    "id": i + 1,
                    "description": task.get('description', f'Task {i+1}'),
                    "duration": task.get('duration', '1 day'),
                    "start_date": task.get('start_date', ''),
                    "end_date": task.get('end_date', ''),
                    "dependencies": task.get('dependencies', [])
                })
            
            return {
                "goal": goal,
                "tasks": tasks,
                "total_duration": plan_data.get('total_duration', 'Unknown'),
                "timeline_respected": plan_data.get('timeline_respected', True)
            }
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"LLM response parsing failed: {e}")
            return self._generate_enhanced_fallback(goal, timeline)
    
    def _generate_enhanced_fallback(self, goal: str, timeline: str = None) -> Dict[str, Any]:
        """Enhanced fallback with proper timeline handling"""
        total_days = self._parse_timeline_input(timeline, goal)
        today = datetime.now()
        
        goal_lower = goal.lower()
        
        if any(keyword in goal_lower for keyword in ['spanish', 'french', 'german', 'language', 'learn']):
            return self._create_language_learning_plan(goal, total_days, today)
        elif any(keyword in goal_lower for keyword in ['exam', 'study', 'semester']):
            return self._create_study_plan(goal, total_days, today)
        elif any(keyword in goal_lower for keyword in ['wedding', 'event']):
            return self._create_wedding_plan(goal, total_days, today)
        elif any(keyword in goal_lower for keyword in ['launch', 'website', 'app', 'product']):
            return self._create_project_plan(goal, total_days, today)
        else:
            return self._create_generic_plan(goal, total_days, today)
    
    def _parse_timeline_input(self, timeline: str, goal: str) -> int:
        """Properly parse timeline input with accurate conversions"""
        if not timeline:
            # Smart defaults based on goal type
            goal_lower = goal.lower()
            if any(keyword in goal_lower for keyword in ['language', 'learn']):
                return 90  # 3 months for language learning
            elif any(keyword in goal_lower for keyword in ['wedding', 'event']):
                return 180  # 6 months for events
            elif any(keyword in goal_lower for keyword in ['business', 'startup']):
                return 120  # 4 months for business
            else:
                return 60   # 2 months default
        
        timeline_lower = timeline.lower().strip()
        
        # Extract numbers
        numbers = re.findall(r'\d+', timeline_lower)
        if not numbers:
            return 60  # Default
        
        total_days = int(numbers[0])
        
        # Accurate conversions
        if 'week' in timeline_lower:
            total_days = total_days * 7
        elif 'month' in timeline_lower:
            total_days = total_days * 30
        elif 'year' in timeline_lower:
            total_days = total_days * 365
        # days is default
        
        return max(7, min(total_days, 730))  # 1 week to 2 years
    
    def _create_language_learning_plan(self, goal: str, total_days: int, today: datetime) -> Dict[str, Any]:
        """Create detailed language learning plan"""
        phases = [
            ("Basic Fundamentals", 0.2, "Learn alphabet, greetings, basic phrases"),
            ("Grammar Foundation", 0.25, "Master basic grammar and sentence structures"),
            ("Vocabulary Building", 0.25, "Expand vocabulary and practice conversations"),
            ("Fluency Development", 0.2, "Advanced grammar and speaking practice"),
            ("Proficiency Mastery", 0.1, "Real-world application and refinement")
        ]
        
        tasks = []
        current_day = 0
        
        for i, (phase_name, weight, description) in enumerate(phases):
            phase_days = max(7, int(total_days * weight))
            
            tasks.append({
                "id": i + 1,
                "description": f"{phase_name}: {description}",
                "duration": f"{phase_days} days",
                "start_date": (today + timedelta(days=current_day)).strftime("%Y-%m-%d"),
                "end_date": (today + timedelta(days=current_day + phase_days - 1)).strftime("%Y-%m-%d"),
                "dependencies": [i] if i > 0 else []
            })
            current_day += phase_days
        
        return {
            "goal": goal,
            "tasks": tasks,
            "total_duration": self._format_duration(total_days),
            "timeline_respected": True
        }
    
    def _create_study_plan(self, goal: str, total_days: int, today: datetime) -> Dict[str, Any]:
        """Create detailed study plan"""
        tasks = [
            {
                "id": 1,
                "description": "Syllabus analysis and study material organization",
                "duration": f"{max(3, total_days // 10)} days",
                "start_date": today.strftime("%Y-%m-%d"),
                "end_date": (today + timedelta(days=max(3, total_days // 10) - 1)).strftime("%Y-%m-%d"),
                "dependencies": []
            },
            {
                "id": 2,
                "description": "Create detailed study schedule and time allocation",
                "duration": f"{max(2, total_days // 15)} days",
                "start_date": (today + timedelta(days=max(3, total_days // 10))).strftime("%Y-%m-%d"),
                "end_date": (today + timedelta(days=max(3, total_days // 10) + max(2, total_days // 15) - 1)).strftime("%Y-%m-%d"),
                "dependencies": [1]
            },
            {
                "id": 3,
                "description": "Comprehensive study of all topics and concepts",
                "duration": f"{max(14, total_days // 2)} days",
                "start_date": (today + timedelta(days=max(3, total_days // 10) + max(2, total_days // 15))).strftime("%Y-%m-%d"),
                "end_date": (today + timedelta(days=max(3, total_days // 10) + max(2, total_days // 15) + max(14, total_days // 2) - 1)).strftime("%Y-%m-%d"),
                "dependencies": [2]
            },
            {
                "id": 4,
                "description": "Practice tests and problem-solving sessions",
                "duration": f"{max(7, total_days // 4)} days",
                "start_date": (today + timedelta(days=max(3, total_days // 10) + max(2, total_days // 15) + max(14, total_days // 2))).strftime("%Y-%m-%d"),
                "end_date": (today + timedelta(days=max(3, total_days // 10) + max(2, total_days // 15) + max(14, total_days // 2) + max(7, total_days // 4) - 1)).strftime("%Y-%m-%d"),
                "dependencies": [3]
            },
            {
                "id": 5,
                "description": "Revision and weak area improvement",
                "duration": f"{max(5, total_days // 6)} days",
                "start_date": (today + timedelta(days=max(3, total_days // 10) + max(2, total_days // 15) + max(14, total_days // 2) + max(7, total_days // 4))).strftime("%Y-%m-%d"),
                "end_date": (today + timedelta(days=max(3, total_days // 10) + max(2, total_days // 15) + max(14, total_days // 2) + max(7, total_days // 4) + max(5, total_days // 6) - 1)).strftime("%Y-%m-%d"),
                "dependencies": [4]
            }
        ]
        
        return {
            "goal": goal,
            "tasks": tasks,
            "total_duration": self._format_duration(total_days),
            "timeline_respected": True
        }
    
    def _create_wedding_plan(self, goal: str, total_days: int, today: datetime) -> Dict[str, Any]:
        """Create detailed wedding planning timeline"""
        tasks = [
            {
                "id": 1,
                "description": "Define budget, guest list, and wedding vision",
                "duration": f"{max(14, total_days // 8)} days",
                "start_date": today.strftime("%Y-%m-%d"),
                "end_date": (today + timedelta(days=max(14, total_days // 8) - 1)).strftime("%Y-%m-%d"),
                "dependencies": []
            },
            {
                "id": 2,
                "description": "Venue selection and booking",
                "duration": f"{max(21, total_days // 6)} days",
                "start_date": (today + timedelta(days=max(14, total_days // 8))).strftime("%Y-%m-%d"),
                "end_date": (today + timedelta(days=max(14, total_days // 8) + max(21, total_days // 6) - 1)).strftime("%Y-%m-%d"),
                "dependencies": [1]
            },
            {
                "id": 3,
                "description": "Book caterer, photographer, and main vendors",
                "duration": f"{max(30, total_days // 4)} days",
                "start_date": (today + timedelta(days=max(14, total_days // 8) + max(21, total_days // 6))).strftime("%Y-%m-%d"),
                "end_date": (today + timedelta(days=max(14, total_days // 8) + max(21, total_days // 6) + max(30, total_days // 4) - 1)).strftime("%Y-%m-%d"),
                "dependencies": [2]
            },
            {
                "id": 4,
                "description": "Send invitations and manage RSVPs",
                "duration": f"{max(21, total_days // 5)} days",
                "start_date": (today + timedelta(days=max(14, total_days // 8) + max(21, total_days // 6) + max(30, total_days // 4))).strftime("%Y-%m-%d"),
                "end_date": (today + timedelta(days=max(14, total_days // 8) + max(21, total_days // 6) + max(30, total_days // 4) + max(21, total_days // 5) - 1)).strftime("%Y-%m-%d"),
                "dependencies": [1]
            },
            {
                "id": 5,
                "description": "Final arrangements and day-of planning",
                "duration": f"{max(14, total_days // 7)} days",
                "start_date": (today + timedelta(days=max(14, total_days // 8) + max(21, total_days // 6) + max(30, total_days // 4) + max(21, total_days // 5))).strftime("%Y-%m-%d"),
                "end_date": (today + timedelta(days=total_days - 1)).strftime("%Y-%m-%d"),
                "dependencies": [3, 4]
            }
        ]
        
        return {
            "goal": goal,
            "tasks": tasks,
            "total_duration": self._format_duration(total_days),
            "timeline_respected": True
        }
    
    def _create_project_plan(self, goal: str, total_days: int, today: datetime) -> Dict[str, Any]:
        """Create detailed project development plan"""
        tasks = [
            {
                "id": 1,
                "description": "Project planning and requirement analysis",
                "duration": f"{max(5, total_days // 6)} days",
                "start_date": today.strftime("%Y-%m-%d"),
                "end_date": (today + timedelta(days=max(5, total_days // 6) - 1)).strftime("%Y-%m-%d"),
                "dependencies": []
            },
            {
                "id": 2,
                "description": "Design and architecture planning",
                "duration": f"{max(7, total_days // 5)} days",
                "start_date": (today + timedelta(days=max(5, total_days // 6))).strftime("%Y-%m-%d"),
                "end_date": (today + timedelta(days=max(5, total_days // 6) + max(7, total_days // 5) - 1)).strftime("%Y-%m-%d"),
                "dependencies": [1]
            },
            {
                "id": 3,
                "description": "Core development and implementation",
                "duration": f"{max(14, total_days // 2)} days",
                "start_date": (today + timedelta(days=max(5, total_days // 6) + max(7, total_days // 5))).strftime("%Y-%m-%d"),
                "end_date": (today + timedelta(days=max(5, total_days // 6) + max(7, total_days // 5) + max(14, total_days // 2) - 1)).strftime("%Y-%m-%d"),
                "dependencies": [2]
            },
            {
                "id": 4,
                "description": "Testing and quality assurance",
                "duration": f"{max(7, total_days // 4)} days",
                "start_date": (today + timedelta(days=max(5, total_days // 6) + max(7, total_days // 5) + max(14, total_days // 2))).strftime("%Y-%m-%d"),
                "end_date": (today + timedelta(days=max(5, total_days // 6) + max(7, total_days // 5) + max(14, total_days // 2) + max(7, total_days // 4) - 1)).strftime("%Y-%m-%d"),
                "dependencies": [3]
            },
            {
                "id": 5,
                "description": "Deployment and launch preparation",
                "duration": f"{max(3, total_days // 8)} days",
                "start_date": (today + timedelta(days=max(5, total_days // 6) + max(7, total_days // 5) + max(14, total_days // 2) + max(7, total_days // 4))).strftime("%Y-%m-%d"),
                "end_date": (today + timedelta(days=total_days - 1)).strftime("%Y-%m-%d"),
                "dependencies": [4]
            }
        ]
        
        return {
            "goal": goal,
            "tasks": tasks,
            "total_duration": self._format_duration(total_days),
            "timeline_respected": True
        }
    
    def _create_generic_plan(self, goal: str, total_days: int, today: datetime) -> Dict[str, Any]:
        """Create generic plan for unknown goal types"""
        tasks = [
            {
                "id": 1,
                "description": "Initial research and planning phase",
                "duration": f"{max(5, total_days // 5)} days",
                "start_date": today.strftime("%Y-%m-%d"),
                "end_date": (today + timedelta(days=max(5, total_days // 5) - 1)).strftime("%Y-%m-%d"),
                "dependencies": []
            },
            {
                "id": 2,
                "description": "Core implementation and progress tracking",
                "duration": f"{max(10, total_days // 2)} days",
                "start_date": (today + timedelta(days=max(5, total_days // 5))).strftime("%Y-%m-%d"),
                "end_date": (today + timedelta(days=max(5, total_days // 5) + max(10, total_days // 2) - 1)).strftime("%Y-%m-%d"),
                "dependencies": [1]
            },
            {
                "id": 3,
                "description": "Refinement and quality improvement",
                "duration": f"{max(7, total_days // 4)} days",
                "start_date": (today + timedelta(days=max(5, total_days // 5) + max(10, total_days // 2))).strftime("%Y-%m-%d"),
                "end_date": (today + timedelta(days=max(5, total_days // 5) + max(10, total_days // 2) + max(7, total_days // 4) - 1)).strftime("%Y-%m-%d"),
                "dependencies": [2]
            },
            {
                "id": 4,
                "description": "Final review and completion",
                "duration": f"{max(3, total_days // 6)} days",
                "start_date": (today + timedelta(days=max(5, total_days // 5) + max(10, total_days // 2) + max(7, total_days // 4))).strftime("%Y-%m-%d"),
                "end_date": (today + timedelta(days=total_days - 1)).strftime("%Y-%m-%d"),
                "dependencies": [3]
            }
        ]
        
        return {
            "goal": goal,
            "tasks": tasks,
            "total_duration": self._format_duration(total_days),
            "timeline_respected": True
        }
    
    def _format_duration(self, total_days: int) -> str:
        """Format duration for display"""
        months = total_days // 30
        weeks = total_days // 7
        days = total_days % 7
        
        if months > 0:
            return f"{total_days} days ({months} month{'s' if months > 1 else ''}{f', {weeks % 4} week{"s" if weeks % 4 > 1 else ""}' if weeks % 4 > 0 else ''})"
        elif weeks > 0:
            return f"{total_days} days ({weeks} week{'s' if weeks > 1 else ''}{f', {days} day{"s" if days > 1 else ""}' if days > 0 else ''})"
        else:
            return f"{total_days} day{'s' if total_days > 1 else ''}"