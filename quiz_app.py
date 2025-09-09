import customtkinter as ctk
import json
import time
from datetime import datetime
import pandas as pd
from tkinter import messagebox

# Set appearance mode
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class QuizApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("🎯 Python Quiz Master")
        self.geometry("800x600")
        self.resizable(True, True)
        
        # Load questions
        self.load_questions()
        
        # Quiz variables
        self.current_question = 0
        self.score = 0
        self.time_remaining = 15
        self.timer_running = False
        self.user_answers = []
        
        # Create main container
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Show welcome screen
        self.show_welcome_screen()
    
    def load_questions(self):
        try:
            with open('questions.json', 'r') as f:
                data = json.load(f)
                self.questions = data['questions']
        except FileNotFoundError:
            messagebox.showerror("Error", "questions.json file not found!")
            self.quit()
    
    def show_welcome_screen(self):
        # Clear existing widgets
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # Welcome content
        welcome_frame = ctk.CTkFrame(self.main_container)
        welcome_frame.pack(expand=True, fill="both", pady=50)
        
        title_label = ctk.CTkLabel(welcome_frame, text="🎯 Python Quiz Master", 
                                  font=ctk.CTkFont(size=28, weight="bold"))
        title_label.pack(pady=20)
        
        info_text = """
        Welcome to the Ultimate Python Quiz!
        
        • Multiple choice and True/False questions
        • 15 seconds per question
        • Instant feedback
        • Detailed results at the end
        
        Test your Python knowledge and see how you score!
        """
        
        info_label = ctk.CTkLabel(welcome_frame, text=info_text,
                                 font=ctk.CTkFont(size=16), justify="left")
        info_label.pack(pady=20)
        
        start_button = ctk.CTkButton(welcome_frame, text="Start Quiz", 
                                    command=self.start_quiz,
                                    font=ctk.CTkFont(size=18),
                                    height=50, width=200)
        start_button.pack(pady=30)
        
        theme_button = ctk.CTkButton(welcome_frame, text="Switch Theme",
                                    command=self.switch_theme)
        theme_button.pack(pady=10)
    
    def start_quiz(self):
        self.current_question = 0
        self.score = 0
        self.user_answers = []
        self.show_question()
    
    def show_question(self):
        # Clear existing widgets
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        if self.current_question >= len(self.questions):
            self.show_results()
            return
        
        question_data = self.questions[self.current_question]
        
        # Header frame
        header_frame = ctk.CTkFrame(self.main_container)
        header_frame.pack(fill="x", pady=10)
        
        progress_label = ctk.CTkLabel(header_frame, 
                                     text=f"Question {self.current_question + 1}/{len(self.questions)}",
                                     font=ctk.CTkFont(weight="bold"))
        progress_label.pack(side="left", padx=10)
        
        score_label = ctk.CTkLabel(header_frame, 
                                  text=f"Score: {self.score}/{len(self.questions)}",
                                  font=ctk.CTkFont(weight="bold"))
        score_label.pack(side="right", padx=10)
        
        # Timer label
        self.time_remaining = 15
        self.timer_label = ctk.CTkLabel(header_frame, 
                                       text=f"Time: {self.time_remaining}s",
                                       font=ctk.CTkFont(weight="bold"),
                                       text_color="red")
        self.timer_label.pack(side="right", padx=20)
        
        # Question frame
        question_frame = ctk.CTkFrame(self.main_container)
        question_frame.pack(fill="both", expand=True, pady=20)
        
        question_text = ctk.CTkLabel(question_frame, text=question_data["question"],
                                    font=ctk.CTkFont(size=18, weight="bold"),
                                    wraplength=600, justify="left")
        question_text.pack(pady=20)
        
        # Options frame
        options_frame = ctk.CTkFrame(question_frame)
        options_frame.pack(pady=20)
        
        self.selected_option = ctk.StringVar(value="")
        
        for i, option in enumerate(question_data["options"]):
            option_btn = ctk.CTkRadioButton(options_frame, text=option,
                                           variable=self.selected_option,
                                           value=option,
                                           font=ctk.CTkFont(size=14))
            option_btn.pack(pady=5, anchor="w")
        
        # Submit button
        submit_button = ctk.CTkButton(question_frame, text="Submit Answer",
                                     command=self.check_answer,
                                     font=ctk.CTkFont(size=14),
                                     state="disabled")
        submit_button.pack(pady=20)
        
        # Enable submit button when an option is selected
        def enable_submit(*args):
            submit_button.configure(state="normal")
        
        self.selected_option.trace("w", enable_submit)
        
        # Start timer
        self.start_timer()
    
    def start_timer(self):
        self.timer_running = True
        self.update_timer()
    
    def update_timer(self):
        if self.timer_running:
            self.time_remaining -= 1
            self.timer_label.configure(text=f"Time: {self.time_remaining}s")
            
            if self.time_remaining <= 5:
                self.timer_label.configure(text_color="red")
            else:
                self.timer_label.configure(text_color="white")
            
            if self.time_remaining <= 0:
                self.timer_running = False
                messagebox.showwarning("Time's up!", "Time ran out for this question!")
                self.user_answers.append({
                    "question": self.questions[self.current_question]["question"],
                    "user_answer": "Time's up",
                    "correct_answer": self.questions[self.current_question]["correct_answer"],
                    "correct": False
                })
                self.next_question()
            else:
                self.after(1000, self.update_timer)
    
    def check_answer(self):
        self.timer_running = False
        
        user_answer = self.selected_option.get()
        correct_answer = self.questions[self.current_question]["correct_answer"]
        is_correct = user_answer == correct_answer
        
        if is_correct:
            self.score += 1
            messagebox.showinfo("Correct!", "✅ Well done! That's correct!")
        else:
            messagebox.showerror("Incorrect", 
                                f"❌ Wrong answer! The correct answer was: {correct_answer}")
        
        # Store user answer for review
        self.user_answers.append({
            "question": self.questions[self.current_question]["question"],
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "correct": is_correct
        })
        
        self.next_question()
    
    def next_question(self):
        self.current_question += 1
        self.show_question()
    
    def show_results(self):
        # Clear existing widgets
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # Results frame
        results_frame = ctk.CTkFrame(self.main_container)
        results_frame.pack(fill="both", expand=True, pady=20)
        
        # Score display
        score_percentage = (self.score / len(self.questions)) * 100
        
        if score_percentage >= 80:
            emoji = "🎉"
            message = "Excellent! You're a Python expert!"
        elif score_percentage >= 60:
            emoji = "👍"
            message = "Good job! You know your Python!"
        else:
            emoji = "📚"
            message = "Keep learning! You'll get better!"
        
        score_text = f"{emoji} Final Score: {self.score}/{len(self.questions)} ({score_percentage:.1f}%)"
        
        score_label = ctk.CTkLabel(results_frame, text=score_text,
                                  font=ctk.CTkFont(size=24, weight="bold"))
        score_label.pack(pady=20)
        
        message_label = ctk.CTkLabel(results_frame, text=message,
                                    font=ctk.CTkFont(size=16))
        message_label.pack(pady=10)
        
        # Review answers
        review_frame = ctk.CTkScrollableFrame(results_frame, height=300)
        review_frame.pack(fill="both", expand=True, pady=20, padx=20)
        
        for i, answer in enumerate(self.user_answers):
            answer_frame = ctk.CTkFrame(review_frame)
            answer_frame.pack(fill="x", pady=5, padx=5)
            
            color = "green" if answer["correct"] else "red"
            icon = "✅" if answer["correct"] else "❌"
            
            question_label = ctk.CTkLabel(answer_frame, 
                                         text=f"{i+1}. {answer['question']}",
                                         font=ctk.CTkFont(weight="bold"),
                                         wraplength=600, justify="left")
            question_label.pack(anchor="w")
            
            user_answer_label = ctk.CTkLabel(answer_frame,
                                            text=f"Your answer: {answer['user_answer']} {icon}",
                                            text_color=color)
            user_answer_label.pack(anchor="w")
            
            if not answer["correct"]:
                correct_label = ctk.CTkLabel(answer_frame,
                                            text=f"Correct answer: {answer['correct_answer']}")
                correct_label.pack(anchor="w")
        
        # Action buttons
        button_frame = ctk.CTkFrame(results_frame)
        button_frame.pack(pady=20)
        
        retry_button = ctk.CTkButton(button_frame, text="Try Again",
                                    command=self.start_quiz)
        retry_button.pack(side="left", padx=10)
        
        save_button = ctk.CTkButton(button_frame, text="Save Results",
                                   command=self.save_results)
        save_button.pack(side="left", padx=10)
        
        quit_button = ctk.CTkButton(button_frame, text="Quit",
                                   command=self.quit)
        quit_button.pack(side="left", padx=10)
    
    def save_results(self):
        try:
            # Create results data
            result_data = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "score": self.score,
                "total_questions": len(self.questions),
                "percentage": (self.score / len(self.questions)) * 100
            }
            
            # Try to load existing results
            try:
                existing_df = pd.read_csv('results.csv')
                results_df = pd.concat([existing_df, pd.DataFrame([result_data])], ignore_index=True)
            except FileNotFoundError:
                results_df = pd.DataFrame([result_data])
            
            # Save to CSV
            results_df.to_csv('results.csv', index=False)
            messagebox.showinfo("Success", "Results saved successfully! 📊")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save results: {str(e)}")
    
    def switch_theme(self):
        current_mode = ctk.get_appearance_mode()
        new_mode = "Light" if current_mode == "Dark" else "Dark"
        ctk.set_appearance_mode(new_mode)

if __name__ == "__main__":
    app = QuizApp()
    app.mainloop()