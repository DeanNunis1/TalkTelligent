import tkinter as tk
import customtkinter as ctk
import webbrowser
from tkinter import ttk
from PIL import ImageTk,Image  
from ttkthemes import ThemedTk
from TT_Backend import Answers
from database import Database
import asyncio
from tkinter import messagebox
import threading
from functools import partial
from TT_Backend import main
import queue
from uuid import uuid4
from multiprocessing import Process, Queue

class MyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TalkTelligent")
        self.geometry("1000x600")
        self.resizable(False,False)
        self.user_id = None
        self.login_frame = LoginFrame(self)
        self.login_frame.pack(expand=True, fill=tk.BOTH)
        self.db = Database()

        self.answers = Answers()
        self.queue = queue.Queue()

    def set_user_id(self, user_id):
        self.user_id = user_id

    def show_home(self, user_id):  # Add user_id as an argument
        self.login_frame.pack_forget()

        self.home_frame = HomeFrame(self, user_id)  # Pass user_id when initializing HomeFrame
        self.home_frame.pack(expand=True, fill=tk.BOTH)

class LoginFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        # Load the image file and create a PhotoImage object
        self.image = Image.open("images/light.jpg")
        self.photo = ImageTk.PhotoImage(self.image)

        # Create a Canvas widget and set the image as the background
        self.canvas = tk.Canvas(self, width=self.image.width, height=self.image.height)
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        self.canvas.create_text(500, 60, text="TalkTelligent", fill="white", font=('CenturyGothic 50 bold'))
        self.canvas.create_text(500, 500, text="Visit our website at TalkTelligent.com", fill="white", font=('CenturyGothic 15 bold'))
        self.canvas.create_text(499, 582, text="© TalkTelligent 2023. ALL RIGHTS RESERVED", fill="white", font=('CenturyGothic 10 bold'))
        self.canvas.pack(fill="both", expand=True)



        self.frame=ctk.CTkFrame(self, width=320, height=360, corner_radius=15, bg_color =("blue"), fg_color= ("midnightblue"))
        self.frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.l2=ctk.CTkLabel(self.frame, text="Log into your Account",font=('Century Gothic',20))
        self.l2.place(x=50, y=45)

        self.l4=ctk.CTkLabel(self.frame, text="Email Address:",font=('Century Gothic',13))
        self.l4.place(x=53, y=86)

        self.entry1=ctk.CTkEntry(self.frame, width=220, placeholder_text='Email', fg_color =("Slategray1"), placeholder_text_color= ("grey35"), text_color= ("grey1"))
        self.entry1.place(x=50, y=110)

        self.l5=ctk.CTkLabel(self.frame, text="Password:",font=('Century Gothic',13))
        self.l5.place(x=53, y=142)

        self.entry2=ctk.CTkEntry(self.frame, width=220, placeholder_text='Password', show="*", fg_color =("Slategray1"), placeholder_text_color= ("grey35"), text_color= ("grey1"))
        self.entry2.place(x=50, y=165)

        self.l3=ctk.CTkButton(self.frame, text="Create Account",font=('Century Gothic',12), height = 1, width = 1, fg_color = ("transparent"), hover = ("false"), command=self.create_account_link)
        self.l3.place(x=48,y=198)

        self.l3=ctk.CTkButton(self.frame, text="Forget password?",font=('Century Gothic',12), height = 1, width = 1, fg_color = ("transparent"), hover = ("false"), command=self.forgot_password_link)
        self.l3.place(x=160,y=198)

#Create custom button
        button1 = ctk.CTkButton(self.frame, width=220, text="Login", command = self.login, corner_radius=6)
        button1.place(x=50, y=233)

    def login(self):
        email = self.entry1.get()
        password = self.entry2.get()

        db = Database()
        user = db.check_login_credentials(email, password)
        db.close()

        if user:
            user_id = user.get("id")  # Get the user ID from the Users table
            self.master.show_home(user_id)  # Pass user_id to the show_home method
        else:
            tk.messagebox.showerror("Error", "Invalid email or password.")

    def create_account_link(self):
        webbrowser.open("https://www.example.com")

    def forgot_password_link(self):
        webbrowser.open("https://www.example.com")

class HomeFrame(tk.Frame, asyncio.Future):
    def __init__(self, master, user_id):
        super().__init__(master)

        self.view_selector = ViewSelector(self)
        self.view_selector.grid(row=0, column=0, sticky="ns")

        self.user_id = user_id

        self.frames = {}

        for F in (HomePage, Tools, Usage):
            frame = F(self, master, self.user_id)
            self.frames[F] = frame
            frame.grid(row=0, column=1, sticky="nsew")

        self.show_frame(HomePage)

        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=0)

    def show_frame(self, context):
        frame = self.frames[context]
        frame.tkraise()


class ViewSelector(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.configure(bg="grey99")

        self.master = master

        self.home_label = ctk.CTkLabel(self, text="TalkTelligent",  fg_color=("gray50", "blue4"), bg_color= ("grey99"), font=("Arial", 20), height=60, width=200)
        self.home_label.pack(pady=0, padx = 0)

        self.home_button = ctk.CTkButton(self, text="Home", fg_color=("gray50", "midnightblue"), hover_color=("gray50"), font=("Arial", 25), height=100, width=200, border_width=0, command=lambda: master.show_frame(HomePage))
        self.home_button.pack(pady=1, padx= 0)

        self.usage_button = ctk.CTkButton(self, text="Tools", fg_color=("gray50", "midnightblue"), hover_color=("gray50"), font=("Arial", 25), height=100, width=200, border_width=0, command=lambda: master.show_frame(Tools))
        self.usage_button.pack(pady=1, padx= 0)

        self.profile_button = ctk.CTkButton(self, text="Usage", fg_color=("gray50", "midnightblue"), hover_color=("gray50"), font=("Arial", 25), height=100, width=200, border_width=0, command=lambda: master.show_frame(Usage))
        self.profile_button.pack(pady=1, padx= 0)

        self.website_button = ctk.CTkButton(self, text="Website", fg_color=("gray50", "midnightblue"), hover_color=("gray50"), font=("Arial", 25), height=100, width=200, border_width=0, command=self.open_website)
        self.website_button.pack(pady=1, padx= 0)

        self.home_label1 = ctk.CTkLabel(self, text="For support please visit our website or contact Support@TalkTelligent.com",  fg_color=("gray50", "blue4"), bg_color= ("grey99"), font=("Arial", 15), height=90, width=200, wraplength= 180)
        self.home_label1.pack(pady=0, padx = 0)
        self.home_label1 = ctk.CTkLabel(self, text="© TalkTelligent 2023. ALL RIGHTS RESERVED",  fg_color=("gray50", "blue4"), bg_color= ("grey99"), font=("Arial", 10), height=49, width=200, wraplength= 120, anchor= "center")
        self.home_label1.pack(pady=0, padx = 0)

    def open_website(self):
        webbrowser.open("https://www.example.com")


class HomePage(tk.Frame):
    def __init__(self, parent, app, user_id):
        tk.Frame.__init__(self, parent)
        self.image = Image.open("images/blue.jpg")
        self.photo = ImageTk.PhotoImage(self.image)

        # Create a Canvas widget and set the image as the background
        self.canvas = tk.Canvas(self, width=self.image.width, height=self.image.height)
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        self.canvas.pack(fill="both", expand=True)
        
        # Titles
        self.canvas.create_text(390, 50, text="Welcome to TalkTelligent!", fill="#0096FF", font=('Arial 30 bold'))
        self.canvas.create_text(200, 110, text="Tool Capabilities", fill="#00ffff", justify= 'center', font=('Arial 21 bold'))
        self.canvas.create_text(590, 110, text="Quick Start Guide", fill="#00ffff", justify= 'center', font=('Arial 21 bold'))
        self.canvas.create_text(390, 380, text="New Features", fill="#00ffff", font=('Arial 21 bold'))

        # Descriptions
        self.canvas.create_text(205, 230, text=f"• Capture every sound from your default desktop audio\n\n• Turn audio into text in real-time, never miss a detail\n\n• Questions are highlighted for your attention and with a simple button press, you can answer them easily", justify= 'center', fill="white", width = 275, font=('Arial 13 bold'))
        self.canvas.create_text(590, 220, text=f"• Navigate over to the Tools tab on the left-hand side of the screen\n\n• Press the Start button and the tool will begin listening\n\n• When a question arises press the button next to the question for the answer", justify= 'center', fill="white", width = 275, font=('Arial 13 bold'))    
        self.canvas.create_text(400, 470, text=f"• Over the course of the next year, TalkTelligent will be incorporating new and innovative features that will be available for early access to PRO members\n\n• Community suggestions and feedback will help develop and shape the future of Talktelligent and is highly reccomened to ensure a flawless experience\n\n• When a question arises press the button next to the question for the answer", justify= 'center', fill="white", width = 700, font=('Arial 13 bold'))    


class Tools(tk.Frame):
    def __init__(self, master, app, user_id):
        self.question_buttons = {}
        self.question_ids = {}
        super().__init__(master)
        self.user_id = user_id
        self.session = None
        self.db = Database()
        self.answers = Answers()
        self.queue = queue.Queue()
        self.listening = False
        self.thread = None
        self.stop_event = threading.Event()
        self.count = 1.0

        self.image = Image.open("images/blue.jpg")
        self.photo = ImageTk.PhotoImage(self.image)

        # Create a Canvas widget and set the image as the background
        self.canvas = tk.Canvas(self, width=self.image.width, height=self.image.height)
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        self.canvas.pack(fill="both", expand=True)

        # Add labels and text boxes to the canvas
        self.canvas.create_text(380, 40, text="TalkTelligent Tool", fill="#0096FF", font=('Arial 30 bold'))
        self.canvas.create_text(80, 75, text="Questions:", fill="#00ffff", font=('Arial 14 bold'))
        self.canvas.create_text(385, 385, text="The answer is:", fill="#00ffff", font=('Arial 14 bold'))

        self.home_questions = ctk.CTkTextbox(self.canvas, fg_color="slategray1", corner_radius = 10, text_color=("black"), height=260, width=750, font=("Arial", 14), border_width=2, border_color="grey35")
        self.home_questions.place(x=25, y=100)

        self.home_answers = ctk.CTkTextbox(self.canvas, fg_color="slategray1", corner_radius = 10, text_color=("black"), height=80, width=700, font=("Arial", 12), border_width=2, border_color="grey35")
        self.home_answers.place(x=50, y=405)

        # Add the start button to the canvas
        self.start_button = ctk.CTkButton(self.canvas, text="Start Listening", height=40, width=200, corner_radius=0, hover_color=("green"), font=("Arial", 14), border_width=1, border_color="lightblue", command=lambda: self.toggle_listening())
        self.start_button.place(x=287, y=505)

        self.status = self.canvas.create_text(388, 558, text="Press the button above to start", fill="white", font=('Arial 10 italic'))

        self.canvas.create_text(400, 580, text="Note: If you experience any issues please restart the application and report the issue to our support", fill="white", font=('Arial 12 bold'))
        

    def run_async_tasks(self):
        # Defines the event loop on this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            self.tasks = loop.run_until_complete(asyncio.gather(
                self.answers.audio_source(), 
                self.answers.process(), 
                self.handle_questions())
            )
            while not self.stop_event.is_set():
                loop.run_until_complete(self.tasks)
        except Exception as e:
            print('Error while running async tasks: ', str(e))
    
    async def cancel_async_tasks(self):
        self.tasks.cancel()
        try:
            await self.tasks
        except asyncio.CancelledError:
            print('Async tasks have been cancelled.')

    def check_queue(self):
        while not self.queue.empty():
            question = self.queue.get()
            self.add_question(question)
        # Only schedule the next check if we're still listening
        if self.listening:
            self.after(100, self.check_queue)

    async def handle_questions(self):
        while True:
            question = await self.answers.question_queue.get()
            self.queue.put(question)


    def add_question(self, output):
        regular_output = output
        question_id = str(uuid4())  # create a unique id for the question
        # Creates space for button
        spaced_output = f"             {output}"
        # Add question to home_questions
        if self.count == 1.0:
            self.home_questions.insert(self.count, f"{spaced_output}\n\n")
            self.count += 2.0
        else:
            self.home_questions.insert(self.count, f"{spaced_output}\n\n")
            self.count += 2.0
        # Create a button for the question
        self.question_ids[question_id] = spaced_output
        button = ctk.CTkButton(self.canvas, text="Answer", height=15, width=50, corner_radius=0, hover_color=("green"), font=("Arial", 12), border_width=1, border_color="lightblue", command=partial(self.answer_and_remove_question, regular_output, spaced_output, question_id))
        self.question_buttons[question_id] = button
        # Place the button next to the question
        button.place(x=35, y=110 + 32.5 * (len(self.question_buttons) - 1))
        # Remove the question and button after 30 seconds
        timer_id = self.after(20000, self.remove_question_and_button, question_id)
        self.question_ids[question_id] = (spaced_output, timer_id)

    def answer_and_remove_question(self, regular_output, spaced_output, question_id):
        self.after_cancel(self.question_ids[question_id][1])  # Cancel the timer
        self.remove_question_and_button(question_id)
        answer = self.answers.answer_question(regular_output)
        self.home_answers.delete(1.0, tk.END)
        self.home_answers.insert(tk.END, answer)

    def remove_question_and_button(self, question_id):
        question, timer_id = self.question_ids[question_id]
        questions = self.home_questions.get(1.0, tk.END).split('\n\n')
        if question in questions:
            idx = questions.index(question)
            self.home_questions.delete(f"{idx*3 + 1}.0", f"{(idx+1)*3 + 1}.0")
            button = self.question_buttons[question_id]
            button.destroy()
            del self.question_buttons[question_id]
            del self.question_ids[question_id]
            self.count -= 2.0

            # Adjust the position of the remaining buttons
            remaining_questions = sorted(self.question_buttons.items(), key=lambda item: item[1].winfo_y())
            for i, (remaining_question_id, button) in enumerate(remaining_questions[idx:], start=idx):
                button.place(x=35, y=110 + 32.5 * i)

            # Adjust the position of the remaining questions in the text box
            remaining_text = questions[idx+1:]
            self.home_questions.delete('1.0', tk.END)
            for question_text in remaining_text:
                self.home_questions.insert(tk.END, f"{question_text}\n\n")


    # Function for Start button command
    def toggle_listening(self):
        if not self.listening:
            try:
                for question_id in list(self.question_buttons.keys()):
                    self.remove_question_and_button(question_id)
            except:
                pass
            self.start_button.configure(text="Stop Listening", hover_color=("red"))
            self.listening = True
            self.canvas.itemconfig(self.status, text="Currently Listening...", font=('Arial 12 bold'))
            self.session = self.db.start_session(self.user_id)
            # Start the thread and the event loop
            self.stop_event.clear()  # Clear the stop event
            self.thread = threading.Thread(target=self.run_async_tasks, daemon=True)
            self.thread.start()
            self.check_queue()

        else:
            self.start_button.configure(text="Start Listening", hover_color=("green"))
            self.listening = False
            self.canvas.itemconfig(self.status, text="Press the button above to begin", font=('Arial 10 italic'))
            self.db.end_session(self.session)
            self.db.update_session_duration(self.session)
            # Schedule the cancellation from the thread running the event loop
            self.stop_event.set()  # This will signal the thread to stop
    
class Usage(tk.Frame):
    def __init__(self, parent, app, user_id):
        tk.Frame.__init__(self, parent)
        self.db = Database()
        self.user_id = user_id
        time = self.db.get_total_usage(user_id)
        max = self.db.get_subscription_max(user_id)
        time = time/60
        self.image = Image.open("images/blue.jpg")
        self.photo = ImageTk.PhotoImage(self.image)

        def website():
            webbrowser.open("https://www.example.com")
        # Create a Canvas widget and set the image as the background
        self.canvas = tk.Canvas(self, width=self.image.width, height=self.image.height)
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        self.canvas.pack(fill="both", expand=True)

        # MAIN LABELS
        self.canvas.create_text(380, 50, text="Current Usage", fill="#0096FF", font=('Arial 30 bold'))
        self.canvas.create_text(375, 295, text="The full list of available plans can be found below. The plan options range in price and include various perks the higher the tier. If you wish to upgrade your plan please select one of the plans below!", fill="white", width = 500, justify = "center", font=('Arial 12 bold'))
        self.canvas.create_text(390, 130, text=f"{int(time)}/{max} Hours", fill="#00ffff", font=('Arial 25 bold'))
        self.canvas.create_text(395, 210, text=f"Your current plan supports {max} hours of streaming per month", fill="white", font=('Arial 18 bold'))

        # PLANS AS BUTTONS/TEXT
        self.canvas.create_text(375, 380, text=f"------------------------------ Pick a Plan ------------------------------", fill="#00ffff", font=('Arial 25 bold'))
        basic = ctk.CTkButton(self.canvas, text="Basic", height=15, width=90, corner_radius=0, hover_color=("grey56"), font=("Arial", 20), border_width=1, border_color="lightblue", fg_color="blue", command= website)
        basic.place(x=80, y=415)
        self.canvas.create_text(130, 480, text=f"✔ Stream 100 Hours\n✔ 24/7 Support\n", fill="white", font=('Arial 13 bold'))
        advanced = ctk.CTkButton(self.canvas, text="Advance", height=20, width=90, corner_radius=0, hover_color=("grey56"), font=("Arial", 20), border_width=1, border_color="lightblue", fg_color="blue", command= website)
        advanced.place(x=330, y=415)
        self.canvas.create_text(385, 480, text=f"✔ Stream 500 Hours\n✔ 24/7 Support\n✔ Ad Free", fill="white", font=('Arial 13 bold'))
        pro = ctk.CTkButton(self.canvas, text="Pro", height=15, width=90, corner_radius=0, hover_color=("grey56"), font=("Arial", 20), border_width=1, border_color="lightblue", fg_color="blue", command= website)
        pro.place(x=600, y=415)
        self.canvas.create_text(660, 490, text=f"✔ Stream 1000 Hours\n✔ 24/7 Support\n✔ Ad Free\n✔ New Features", fill="white", font=('Arial 13 bold'))

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self.canvas, width = 600, corner_radius=0, height = 40, 
        mode = 'determinate', fg_color= 'grey56', progress_color= 'darkblue')
        self.progress_bar.place(x=95, y=150)
        self.progress_bar.set(time/max)

        # Note
        self.canvas.create_text(400, 580, text="Note: If you experience any issues please restart the application and report the issue to our support", fill="white", font=('Arial 12 bold'))


if __name__ == "__main__":
    app = MyApp()
    app.mainloop()