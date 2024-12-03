# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import random
from datetime import datetime
from tkinter import PhotoImage
import os
from tkinter import Toplevel
import tkinter.messagebox
import pygame
import pygame.mixer
import csv
from ticket_cost_3 import TicketCostCalculator
import qrcode
import libscrc
import json
from tkinter import scrolledtext
from ttkthemes import ThemedTk, ThemedStyle
from tkinter import filedialog


class MetroTicketMachine(tk.Tk):
    def __init__(self):
        super().__init__()

        self.init_zoom_level = 0.3
        self.zoom_level = self.init_zoom_level
        self.isStopped = False
        self.title("Metro Ticket Vending Machine")
        self.geometry("1920x1080")
        self.configure(bg = 'seashell3')
        
        # self.set_theme('scidgreen')
        
        pygame.mixer.init()
        
        self.ui_frame = tk.Frame(self)
        self.ui_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ns")  # Occupy half of the interface

        # Create a label widget to display date and time
        # self.date_time_label = tk.Label(self.ui_frame, text="", font=("Helvetica", 12))
        # self.date_time_label.grid(row=7, column=0, columnspan=4, pady=10, sticky="w")
        
        self.payment_frame = None
        self.create_widgets()

    def create_widgets(self):
        # Create a menu bar
        menubar = tk.Menu(self)

        # Create a "File" menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_json_file)
        file_menu.add_separator()
        # file_menu.add_command(label="Exit", command=self.quit)
        file_menu.configure(bg = 'seashell1')

        # Add the "File" menu to the menu bar
        menubar.add_cascade(label="File", menu=file_menu)
        menubar.configure(bg = 'seashell1')

        # Configure the window to use the menu bar
        self.config(menu=menubar)

        self.grid_rowconfigure(0, weight=1)  # Half of the vertical space
        self.grid_columnconfigure(0, weight=1)  # Full horizontal space
        
        self.image_frame = tk.Frame(self)
        self.image_frame.grid(row=0, column=0, pady=10, sticky="nsew")  # Occupy half of the interface
        self.image_frame.grid_rowconfigure(0, weight=1)

        path = 'bangkok-map.png'
        self.zoom_advanced = Zoom_Advanced(self.image_frame, path=path)

        self.ui_frame = tk.Frame(self)
        self.ui_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsw")  # Occupy half of the interface
        self.ui_frame.configure(bg='seashell1')

        # Place the name label at the top of the right side
        self.name = tk.Label(self.ui_frame, text="BANGKOK MASS RAPID TRANSIT\n TICKET MACHINE", font=("Helvetica", 20, "bold"), fg = 'blue4')
        self.name.grid(row=0, column=0, columnspan=3, padx= 5, pady=(15, 5))
        self.name.configure(bg='seashell1')

        self.ticket_frame = tk.Frame(self.ui_frame)
        self.ticket_frame.grid(row=1, column=0, columnspan=4, pady=10)
        self.ticket_frame.configure(bg='seashell1')

        self.adult_label = tk.Label(self.ticket_frame, text="Adult Tickets:", font = 10)
        self.adult_label.grid(row=1, column=0,padx = 15, pady=10)
        self.adult_label.configure(bg='seashell1')
        self.adult_spinbox = tk.Spinbox(self.ticket_frame, from_=1, to=20, font = 12)
        self.adult_spinbox.grid(row=1, column=1,padx = 15, pady=10)

        self.child_label = tk.Label(self.ticket_frame, text="Child Tickets:", font = 10)
        self.child_label.grid(row=2, column=0, padx= 15, pady=10)
        self.child_label.configure(bg='seashell1')
        self.child_spinbox = tk.Spinbox(self.ticket_frame, from_=0, to=20, font = 12)
        self.child_spinbox.grid(row=2, column=1, padx = 15,pady=10)

        self.current_label = tk.Label(self.ui_frame, text="Current Station:", font = 10)
        self.current_label.grid(row=3, column=0, pady=10,sticky = 'e')
        self.current_label.configure(bg='seashell1')
        self.current_combobox = ttk.Combobox(self.ui_frame, values=["Khu Khot","Yaek Kor Por Aor","Royal Thai Air Force Museum","Bhumibol Adulyadej Hospital"
    ,"Saphan Mai","Sai Yud","Phahon Yothin 59","Wat Phra Sri Mahathat","11th Infantry Regiment","Bang Bua","Royal Forest Department"
    ,"Kasetsart University","Sena Nikhom","Ratchayothin","Phahon Yothin 24","Ha Yaek Lat Phrao","Mo Chit", "Saphan Khwai", "Ari", "Sanam Pao", "Victory Monument", "Phaya Thai", "Ratchathewi","Siam",
    "Chit Lom", "Phloen Chit", "Nana", "Asok", "Phrom Phong", "Thong Lo", "Ekkamai",
    "Phra Khanong", "On Nut", "Bang Chak", "Punnawithi", "Udom Suk", "Bang Na", "Bearing",
    "Samrong", "Pu Chao","Chang Erawan", "Royal Thai Naval Academy", "Pak Nam", "Srinagarindra", "Phraek Sa",
    "Sai Luat", "Kheha","National Stadium","Ratchadamri","Sala Daeng","Chong Nonsi","Saint Louis","Surasak",
    "Saphan Taksin","Krung Thon Buri","Wongwian Yai","Pho Nimit","Talat Phlu","Wutthakat","Bang Wa","คลองบางไผ่","ตลาดบางใหญ่","สามแยกบางใหญ่","บางพลู","บางรักใหญ่",
    "บางรักน้อย-ท่าอิฐ","ไทรม้า","สะพานพระนั่งเกล้า","แยกนนทบุรี 1","บางกระสอ","ศูนย์ราชการนนทบุรี","กระทรวงสาธารณสุข","แยกติวานนท์","วงศ์สว่าง","บางซ่อน","เตาปูน","บางซื่อ","กำแพงเพชร","สวนจตุจักร","พหลโยธิน","ลาดพร้าว","รัชดาภิเษก","สุทธิสาร","ห้วยขวาง","ศูนย์วัฒนธรรมแห่งประเทศไทย","พระราม 9","เพชรบุรี",
"สุขุมวิท","ศูนย์การประชุมแห่งชาติสิริกิติ์","คลองเตย","ลุมพินี","สีลม","สามย่าน","หัวลำโพง","วัดมังกร","สามยอด","สนามไชย","อิสรภาพ","ท่าพระ","บางไผ่",
"บางหว้า","เพชรเกษม 48","ภาษีเจริญ","บางแค","หลักสอง","บางโพ","บางอ้อ","บางพลัด","สิรินธร","บางยี่ขัน","บางขุนนนท์","ไฟฉาย","จรัญสนิทวงศ์ 13","Chatuchak","Wat Samian Nari","Bang Khen","Thung Song Hong","Lak Si","Kan Kheha","Don Mueang","Lak Hok","Rangsit","Taling Chan","Bang Son"],font=("Arial Baltic", 12, "bold"), width = 25, height = 12)
        self.current_combobox.grid(row=3, column=1, pady=10)

        self.current_combobox.bind('<KeyRelease>', self.search_current)
        
        self.destination_label = tk.Label(self.ui_frame, text="Destination Station:", font = 10)
        self.destination_label.grid(row=4, column=0, pady=10,sticky = 'e')
        self.destination_label.configure(bg='seashell1')
        self.destination_combobox = ttk.Combobox(self.ui_frame, values= ["Khu Khot","Yaek Kor Por Aor","Royal Thai Air Force Museum","Bhumibol Adulyadej Hospital"
    ,"Saphan Mai","Sai Yud","Phahon Yothin 59","Wat Phra Sri Mahathat","11th Infantry Regiment","Bang Bua","Royal Forest Department"
    ,"Kasetsart University","Sena Nikhom","Ratchayothin","Phahon Yothin 24","Ha Yaek Lat Phrao","Mo Chit", "Saphan Khwai", "Ari", "Sanam Pao", "Victory Monument", "Phaya Thai", "Ratchathewi","Siam",
    "Chit Lom", "Phloen Chit", "Nana", "Asok", "Phrom Phong", "Thong Lo", "Ekkamai",
    "Phra Khanong", "On Nut", "Bang Chak", "Punnawithi", "Udom Suk", "Bang Na", "Bearing",
    "Samrong", "Pu Chao","Chang Erawan", "Royal Thai Naval Academy", "Pak Nam", "Srinagarindra", "Phraek Sa",
    "Sai Luat", "Kheha","National Stadium","Ratchadamri","Sala Daeng","Chong Nonsi","Saint Louis","Surasak",
    "Saphan Taksin","Krung Thon Buri","Wongwian Yai","Pho Nimit","Talat Phlu","Wutthakat","Bang Wa","คลองบางไผ่","ตลาดบางใหญ่","สามแยกบางใหญ่","บางพลู","บางรักใหญ่",
    "บางรักน้อย-ท่าอิฐ","ไทรม้า","สะพานพระนั่งเกล้า","แยกนนทบุรี 1","บางกระสอ","ศูนย์ราชการนนทบุรี","กระทรวงสาธารณสุข","แยกติวานนท์","วงศ์สว่าง","บางซ่อน","เตาปูน","บางซื่อ","กำแพงเพชร","สวนจตุจักร","พหลโยธิน","ลาดพร้าว","รัชดาภิเษก","สุทธิสาร","ห้วยขวาง","ศูนย์วัฒนธรรมแห่งประเทศไทย","พระราม 9","เพชรบุรี",
"สุขุมวิท","ศูนย์การประชุมแห่งชาติสิริกิติ์","คลองเตย","ลุมพินี","สีลม","สามย่าน","หัวลำโพง","วัดมังกร","สามยอด","สนามไชย","อิสรภาพ","ท่าพระ","บางไผ่",
"บางหว้า","เพชรเกษม 48","ภาษีเจริญ","บางแค","หลักสอง","บางโพ","บางอ้อ","บางพลัด","สิรินธร","บางยี่ขัน","บางขุนนนท์","ไฟฉาย","จรัญสนิทวงศ์ 13","Chatuchak","Wat Samian Nari","Bang Khen","Thung Song Hong","Lak Si","Kan Kheha","Don Mueang","Lak Hok","Rangsit","Taling Chan","Bang Son"],font=("Arial Baltic", 12, "bold"), width = 25, height = 12)
        self.destination_combobox.grid(row=4, column=1, pady=10)
        
        self.destination_combobox.bind('<KeyRelease>', self.search_destination)

        self.calculate_button = tk.Button(self.ui_frame, text="Calculate Total",width =20,height= 3, command=self.calculate_total,font=("Arial Baltic", 10, "bold"), bg = '#E3CF57')
        self.calculate_button.grid(row=5, column=1 , pady=20)
        
        self.tprice_label = tk.Label(self.ui_frame, text="Total Price:", font = 10)
        self.tprice_label.grid(row=6, column=0, padx= 15, pady=10, sticky = 'e')
        self.tprice_label.configure(bg='seashell1')

         # Display the text "Total Price" outside the Entry widget
        self.total_entry = tk.Entry(self.ui_frame, width=20, state='readonly', font=8)
        self.total_entry.grid(row=6, column=1, pady=10)
        self.total_entry.insert(0, "฿0.00")
        
        self.shortest_label = tk.Label(self.ui_frame, text="Shortest Path:", font = 10)
        self.shortest_label.grid(row=7, column=0, padx= 15, pady=10, sticky = 'e')
        self.shortest_label.configure(bg='seashell1')
        
        # self.shortest = tk.Entry(self.ui_frame, width = 30, state='readonly', font=2)
        # self.shortest.grid(row=7, column=1, pady = 20)
        # self.shortest.insert(0,"lol")
        
        self.shortest = scrolledtext.ScrolledText(self.ui_frame, wrap=tk.WORD, width=40, height=1,font=("Arial Baltic", 10, "bold"))
        self.shortest.grid(row=7, column=1, pady = 20)
        self.shortest.config(state = 'disabled')
        self.shortest.insert(tk.END, " ") 

        self.pay_button = tk.Button(self.ui_frame, text="Pay", width=20, height=3, font=("Arial Baltic", 10, "bold"), bg='#EE3B3B', command=self.pay_button_clicked)
        self.pay_button.grid(row=8, column=1, pady=5)
        
        self.ticket_calculator = TicketCostCalculator('output3.csv')
        
        self.payment_sound = pygame.mixer.Sound('cash.mp3')
        self.payment_sound.set_volume(0.2)
        
        self.add_image_to_frame(self.ui_frame, 'BTS3.png')
        
        self.date_time_label = tk.Label(self.ui_frame, text="", font=("Helvetica", 12))
        self.date_time_label.grid(row= 9, column=1, columnspan=4, pady=5, sticky="se")
        self.date_time_label.configure(bg='seashell1')
        
        self.update_date_time_label1()
        
    def search_current(self, event=None):
        value = self.current_combobox.get()
        destinations = ["Khu Khot","Yaek Kor Por Aor","Royal Thai Air Force Museum","Bhumibol Adulyadej Hospital"
    ,"Saphan Mai","Sai Yud","Phahon Yothin 59","Wat Phra Sri Mahathat","11th Infantry Regiment","Bang Bua","Royal Forest Department"
    ,"Kasetsart University","Sena Nikhom","Ratchayothin","Phahon Yothin 24","Ha Yaek Lat Phrao","Mo Chit", "Saphan Khwai", "Ari", "Sanam Pao", "Victory Monument", "Phaya Thai", "Ratchathewi","Siam",
    "Chit Lom", "Phloen Chit", "Nana", "Asok", "Phrom Phong", "Thong Lo", "Ekkamai",
    "Phra Khanong", "On Nut", "Bang Chak", "Punnawithi", "Udom Suk", "Bang Na", "Bearing",
    "Samrong", "Pu Chao","Chang Erawan", "Royal Thai Naval Academy", "Pak Nam", "Srinagarindra", "Phraek Sa",
    "Sai Luat", "Kheha","National Stadium","Ratchadamri","Sala Daeng","Chong Nonsi","Saint Louis","Surasak",
    "Saphan Taksin","Krung Thon Buri","Wongwian Yai","Pho Nimit","Talat Phlu","Wutthakat","Bang Wa","คลองบางไผ่","ตลาดบางใหญ่","สามแยกบางใหญ่","บางพลู","บางรักใหญ่",
    "บางรักน้อย-ท่าอิฐ","ไทรม้า","สะพานพระนั่งเกล้า","แยกนนทบุรี 1","บางกระสอ","ศูนย์ราชการนนทบุรี","กระทรวงสาธารณสุข","แยกติวานนท์","วงศ์สว่าง","บางซ่อน","เตาปูน","บางซื่อ","กำแพงเพชร","สวนจัตุจักร","พหลโยธิน","ลาดพร้าว","รัชดาภิเษก","สุทธิสาร","ห้วยขวาง","ศูนย์วัฒนธรรมแห่งประเทศไทย","พระราม 9","เพชรบุรี",
"สุขุมวิท","ศูนย์การประชุมแห่งชาติสิริกิติ์","คลองเตย","ลุมพินี","สีลม","สามย่าน","หัวลำโพง","วัดมังกร","สามยอด","สนามไชย","อิสรภาพ","ท่าพระ","บางไผ่",
"บางหว้า","เพชรเกษม 48","ภาษีเจริญ","บางแค","หลักสอง","บางโพ","บางอ้อ","บางพลัด","สิรินธร","บางยี่ขัน","บางขุนนนท์","ไฟฉาย","จรัญสนิทวงศ์ 13","Chatuchak","Wat Samian Nari","Bang Khen","Thung Song Hong","Lak Si","Kan Kheha","Don Mueang","Lak Hok","Rangsit","Taling Chan","Bang Son"]


        if value == '':
            self.current_combobox['values'] = destinations
        else:
            data = []
            for item in destinations:
                if value.lower() in item.lower():
                    data.append(item)
            self.current_combobox['values'] = data

    def search_destination(self, event=None):
        value = self.destination_combobox.get()
        destinations = ["Khu Khot","Yaek Kor Por Aor","Royal Thai Air Force Museum","Bhumibol Adulyadej Hospital"
    ,"Saphan Mai","Sai Yud","Phahon Yothin 59","Wat Phra Sri Mahathat","11th Infantry Regiment","Bang Bua","Royal Forest Department"
    ,"Kasetsart University","Sena Nikhom","Ratchayothin","Phahon Yothin 24","Ha Yaek Lat Phrao","Mo Chit", "Saphan Khwai", "Ari", "Sanam Pao", "Victory Monument", "Phaya Thai", "Ratchathewi","Siam",
    "Chit Lom", "Phloen Chit", "Nana", "Asok", "Phrom Phong", "Thong Lo", "Ekkamai",
    "Phra Khanong", "On Nut", "Bang Chak", "Punnawithi", "Udom Suk", "Bang Na", "Bearing",
    "Sai Luat", "Kheha","Chang Erawan","National Stadium","Ratchadamri","Sala Daeng","Chong Nonsi","Saint Louis","Surasak",
    "Samrong", "Pu Chao", "Royal Thai Naval Academy", "Pak Nam", "Srinagarindra", "Phraek Sa",
    "Saphan Taksin","Krung Thon Buri","Wongwian Yai","Pho Nimit","Talat Phlu","Wutthakat","Bang Wa","คลองบางไผ่","ตลาดบางใหญ่","สามแยกบางใหญ่","บางพลู","บางรักใหญ่",
    "บางรักน้อย-ท่าอิฐ","ไทรม้า","สะพานพระนั่งเกล้า","แยกนนทบุรี 1","บางกระสอ","ศูนย์ราชการนนทบุรี","กระทรวงสาธารณสุข","แยกติวานนท์","วงศ์สว่าง","บางซ่อน","เตาปูน","บางซื่อ","กำแพงเพชร","สวนจัตุจักร","พหลโยธิน","ลาดพร้าว","รัชดาภิเษก","สุทธิสาร","ห้วยขวาง","ศูนย์วัฒนธรรมแห่งประเทศไทย","พระราม 9","เพชรบุรี",
"สุขุมวิท","ศูนย์การประชุมแห่งชาติสิริกิติ์","คลองเตย","ลุมพินี","สีลม","สามย่าน","หัวลำโพง","วัดมังกร","สามยอด","สนามไชย","อิสรภาพ","ท่าพระ","บางไผ่",
"บางหว้า","เพชรเกษม 48","ภาษีเจริญ","บางแค","หลักสอง","บางโพ","บางอ้อ","บางพลัด","สิรินธร","บางยี่ขัน","บางขุนนนท์","ไฟฉาย","จรัญสนิทวงศ์ 13","Chatuchak","Wat Samian Nari","Bang Khen","Thung Song Hong","Lak Si","Kan Kheha","Don Mueang","Lak Hok","Rangsit","Taling Chan","Bang Son"]


        if value == '':
            self.destination_combobox['values'] = destinations
        else:
            data = []
            for item in destinations:
                if value.lower() in item.lower():
                    data.append(item)
            self.destination_combobox['values'] = data
            
            
    def update_date_time_label1(self):
        if not self.isStopped:
            # Update the date and time label with the current date and time
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.date_time_label.config(text=current_datetime)

            # Schedule the update every 1000 milliseconds (1 second)
            self.after(1000, self.update_date_time_label1)

    def calculate_total(self):
        num_adult_tickets = int(self.adult_spinbox.get())
        num_child_tickets = int(self.child_spinbox.get())

        # Check if the number of tickets is within the valid range
        if num_adult_tickets < 0 or num_adult_tickets > 20 or num_child_tickets < 0 or num_child_tickets > 20:
            self.handle_invalid_tickets()
            return

        current_station = self.current_combobox.get()
        destination_station = self.destination_combobox.get()

        try:
            shortest_path = self.ticket_calculator.find_shortest_path(current_station, destination_station)

            if shortest_path:
                ticket_cost = self.ticket_calculator.calculate_total_cost(shortest_path)

                if isinstance(ticket_cost, int):
                    # Ticket cost is a valid integer, update the total entry field
                    total_price = (num_adult_tickets * int(ticket_cost)) + (num_child_tickets * (int(ticket_cost) / 2))
                    shortest_p = shortest_path
                    self.update_total_entry(total_price, shortest_p)
                else:
                    # Display the error message
                    self.handle_error(f"Error: {ticket_cost}")
            else:
                # Display the error message for an invalid route
                self.handle_error("Invalid route")

        except Exception as e:
            # Handle unexpected exceptions
            self.handle_error(f"An unexpected error occurred: {str(e)}")

    def handle_invalid_tickets(self):
        self.total_entry.config(state='normal')
        self.total_entry.delete(0, tk.END)
        self.total_entry.insert(0, "Invalid number of tickets")
        self.total_entry.config(state='readonly')

    def handle_error(self, error_message):
        self.total_entry.config(state='normal')
        self.total_entry.delete(0, tk.END)
        self.total_entry.insert(0, error_message)
        self.total_entry.config(state='readonly')

    def update_total_entry(self, total_price, shortest_path):
        self.shortest.config(state='normal')
        self.total_entry.config(state='normal')
        self.shortest.delete("1.0", tk.END)
        self.total_entry.delete(0, tk.END)
        self.shortest.insert(tk.INSERT, ">>".join(shortest_path))
        self.total_entry.insert(0, f"฿{total_price:.2f}")
        self.shortest.config(state='disabled')
        self.total_entry.config(state='readonly')


    
    def open_payment_window(self):
        self.isStopped = True  # Stop the update loop
        self.withdraw()  # Hide the current window
        total_price= float(self.total_entry.get().replace('฿',''))
        payment_window = PaymentWindow(self, total_price,self.current_combobox, self.destination_combobox)  # Create a new window for payment
        payment_window.protocol("WM_DELETE_WINDOW", self.restart_program)  # Handle window close event
        payment_window.mainloop()

    def go_back_to_main(self):
        self.isStopped = True 
        self.deiconify()  # Show the main window again
        self.update()  # Refresh the main window
        self.focus_force()  # Set focus to the main window

        # Destroy the payment frame if it exists
        if self.payment_frame:
            self.isStopped = True 
            self.payment_frame.destroy()
            self.payment_frame = None
            
    def play_payment_sound(self):
        # Play the payment sound effect when the "Pay" button is clicked
        self.payment_sound.play()  # Use .play() to play the sound

    def pay_button_clicked(self):
        total_cost = self.total_entry.get().replace('฿', '').strip()

        if total_cost:
            # If total cost is available, proceed with payment
            shortest_path = self.shortest.get("1.0", tk.END).strip()

            if shortest_path and shortest_path != "Invalid route":
                # If the shortest path is not an invalid route, proceed with payment
                self.isStopped = True  # Stop the update loop
                self.play_payment_sound()
                self.open_payment_window()
            else:
                # If the shortest path is invalid, show an error message
                tkinter.messagebox.showerror("Error", "Invalid route. Please select valid stations.")
        else:
            # If total cost is not available, show an error message
            tkinter.messagebox.showerror("Error", "Please calculate the total cost before proceeding to payment.")
        
        
    def add_image_to_frame(self, frame, image_path):
        # Load the image
        img = Image.open('BTS3.png')
        img = img.resize((216, 77), Image.LANCZOS)  # Resize the image as needed

        # Convert the image to a PhotoImage
        photo = ImageTk.PhotoImage(img)

        # Create a label to display the image
        image_label = tk.Label(self.ui_frame, image=photo)
        image_label.image = photo  # Store a reference to the image to prevent it from being garbage collected

        # Add the image label to the bottom right corner of the frame
        image_label.grid(row=10, column=0, columnspan=4, sticky="e",pady=15)
        image_label.configure(bg='seashell1')
        
        
    def restart_program(self):
        self.isStopped = True  # Stop the update loop
        # This method will be called when the payment window is closed
        self.destroy()  # Destroy the main window
        self.__init__()  # Recreate the main window
        self.mainloop()  # Start the main event loop again
        
    def open_json_file(self):
        file_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            json_data = self.read_json_file(file_path)

            # Create a new Toplevel window to display the JSON data
            display_window = tk.Toplevel()
            display_window.title("JSON Data")

            # Create a text widget to display the JSON data
            text_widget = tk.Text(display_window, wrap="none", width=40, height=20)
            text_widget.insert(tk.END, json.dumps(json_data, indent=2,ensure_ascii=False))
            text_widget.pack(expand=True, fill="both")
            
    def read_json_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
        return json_data

class PaymentWindow(tk.Toplevel):
    def __init__(self, parent, total_price, current_combobox,destination_combobox):
        super().__init__(parent)
        self.parent = parent
        self.isStopped = False 
        self.total_price = total_price
        self.selected_payment_method = tk.StringVar(value="PromptPay")
        self.current_combobox = current_combobox
        self.destination_combobox = destination_combobox
        self.geometry("1920x1080")
        self.configure(bg = 'seashell3')
        self.widget()

    def widget(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.image_frame = tk.Frame(self)
        self.image_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        path = 'bangkok-map.png'
        self.zoom_advanced = Zoom_Advanced(self.image_frame, path=path)

        self.ui_frame = tk.Frame(self)
        self.ui_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ns")
        self.ui_frame.configure(bg ='seashell1')

        self.name = tk.Label(self.ui_frame, text="BANGKOK MASS RAPID TRANSIT\n TICKET MACHINE", font=("Helvetica", 22, "bold"),fg = 'blue4')
        self.name.grid(row=0, column=0, columnspan=4, pady=(15, 30),padx =10, sticky='w')
        self.name.configure(bg ='seashell1')

        self.ticket_frame = tk.Frame(self.ui_frame)
        self.ticket_frame.grid(row=0, column=1, columnspan=4, pady=10)
        self.ticket_frame.configure(bg = 'seashell1')

        payment_label = tk.Label(self.ui_frame, text="Choose the payment method:", font=("Helvetica", 16, "bold"))
        payment_label.grid(row=2, column=1, pady=10)
        payment_label.configure(bg ='seashell1')

        promptpay_button = tk.Radiobutton(self.ui_frame, text="PromptPay", font =("Arial Baltic", 13, "bold") , variable=self.selected_payment_method, value="PromptPay")
        promptpay_button.grid(row=3, column=1, columnspan =4, sticky ='w', pady= 15)
        promptpay_button.configure(bg ='seashell1')
        
        cash_button = tk.Radiobutton(self.ui_frame, text="Cash", font =("Arial Baltic", 13, "bold"), variable=self.selected_payment_method, value="Cash")
        cash_button.grid(row=3, column=1, sticky = 'e', pady = 15)
        cash_button.configure(bg ='seashell1')
        
        # payment_entry = tk.Entry(self.ui_frame, width=30,state='readonly', font=8)
        # payment_entry.grid(row = 3, column = 1,pady=5)

        total_label = tk.Label(self.ui_frame, text=f"Total Price: ฿{self.total_price:.2f}", font=("Arial Baltic", 14))
        total_label.grid(row=4, column=1,pady=10)
        total_label.configure(bg ='seashell1')

        confirm_button = tk.Button(self.ui_frame, text="PAY",font=("Arial Baltic", 11, "bold"), command=self.confirm_payment, width=20,height=3, bg='#E3CF57')
        confirm_button.grid(row=5, column=1,pady=10)

        cancel_payment = tk.Button(self.ui_frame, text="Cancel Payment",font=("Arial Baltic", 11, "bold"), command=self.confirm_cancel_payment,width=20, height=3, bg='#EE3B3B')
        cancel_payment.grid(row=6, column=1,pady=10)

        # path = 'BTS3.png'  # Make sure the image path is correct
        # self.add_image_to_frame(self.image_frame, path)  # Call the local add_image_to_frame method

        self.date_time_label = tk.Label(self.ui_frame, text="", font=("Helvetica", 12))
        self.date_time_label.grid(row=7, column=0, columnspan=10, pady=100, sticky = 'e')
        self.date_time_label.configure(bg ='seashell1')

        self.update_date_time_label2()
        
            # Load the image using PIL
        img = Image.open('BTS3.png')
        img = img.resize((216, 77), Image.LANCZOS)

        # Convert the PIL Image to a Tkinter PhotoImage
        self.image = ImageTk.PhotoImage(img)

        # Create a label to display the image
        image_label = tk.Label(self.ui_frame, image=self.image)
        image_label.grid(row=8, column=1, columnspan = 6, sticky = 'e', pady = 10)
        image_label.configure(bg ='seashell1')
        
        # self.ui_frame = tk.Frame(self)s
        # self.ui_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ns")
        
        self.payment_sound = pygame.mixer.Sound('cash.mp3')
        self.payment_sound.set_volume(0.2)

    def confirm_cancel_payment(self):
        # Display a confirmation dialog
        response = tkinter.messagebox.askyesno("Cancel Payment", "Are you sure you want to cancel the payment?")
        if response:
            self.isStopped = True 
            # User clicked "Yes," so destroy the payment window and go back to the main window
            self.after(1000, self.destroy_frame)
            # self.parent.deiconify()
            self.parent.restart_program()
            
    def destroy_frame(self):
        self.destroy()
        
            
    def open_promptpay_window(self):
        self.play_payment_sound()
        # Create an instance of the PromptPayPayment class and open the UI
        self.promptpay_payment = PromptPayPayment(self, self.total_price)
        self.promptpay_payment.open()
    
    def open_cash_payment_window(self):
        self.play_payment_sound()
        self.cash_payment = CashPayment(self, self.total_price)
        self.cash_payment.create_ui()

    def confirm_payment(self):
        # self.withdraw()
        selected_method = self.selected_payment_method.get()
        
        if selected_method == "PromptPay":
            
            # self.open_promptpay_window()
            tkinter.messagebox.showinfo("PromptPay Unavailable", "Sorry, PromptPay is not available at the moment.")
            
            payment_data = {
                "payment_method": "PromptPay",
                "current_station": self.current_combobox.get(),  
                "destination_station": self.destination_combobox.get(),  
                "total_cost": self.total_price
            }
            self.save_payment_data(payment_data)
                        
        elif selected_method == "Cash":
            self.isStopped = True 
            self.withdraw()
            self.open_cash_payment_window()
            
            payment_data = {
                "payment_method": "Cash",
                "current_station": self.current_combobox.get(),  
                "destination_station": self.destination_combobox.get(),  
                "total_cost": self.total_price
            }
            self.save_payment_data(payment_data)


        else:
            # Handle an unexpected or unsupported payment method
            pass
       
        
    def update_date_time_label2(self):
        if not self.isStopped:
            # Update the date and time label with the current date and time
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.date_time_label.config(text=current_datetime)

            # Schedule the update every 1000 milliseconds (1 second)
            # self.after(1000, self.update_date_time_label, label)
            self.after(1000, self.update_date_time_label2)


    def save_payment_data(self, payment_data):
        # Define the file path for the JSON file
        json_file_path = "payment_data5.json"

        # Load existing payment data (if any)
        existing_data = []
        try:
            with open(json_file_path, "r", encoding="utf-8") as json_file:
                # Try to load the file as a JSON array
                existing_data = json.load(json_file)
        except (FileNotFoundError, json.JSONDecodeError):
            pass  

        # Append the new payment data to the existing data
        existing_data.append(payment_data)

        with open(json_file_path, "w", encoding="utf-8") as json_file:
            json.dump(existing_data, json_file, ensure_ascii=False, indent = 2)

        print("Payment data saved to", json_file_path)
        
    def play_payment_sound(self):
        # Play the payment sound effect when the "Pay" button is clicked
        self.payment_sound.play()  # Use .play() to play the sound


class PromptPayPayment(tk.Toplevel):
    def __init__(self, parent, total_price):
        super().__init__(parent)
        self.parent = parent
        self.total_price = total_price
        self.selected_payment_method = tk.StringVar(value="PromptPay")
        self.geometry("1920x1080")

        self.create_ui()

    def create_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.image_frame = tk.Frame(self)
        self.image_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        path = 'bangkok-map.png'
        self.zoom_advanced = Zoom_Advanced(self.image_frame, path=path)

        self.ui_frame = tk.Frame(self)
        self.ui_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ns")

        self.name = tk.Label(self.ui_frame, text="BANGKOK MASS RAPID TRANSIT\n TICKET MACHINE", font=("Helvetica", 22, "bold"),fg = 'blue4')
        self.name.grid(row=0, column=0, columnspan=4, pady=(15, 30), sticky='w')

        self.ticket_frame = tk.Frame(self.ui_frame)
        self.ticket_frame.grid(row=1, column=0, columnspan=4, pady=10)

        payment_label = tk.Label(self.ui_frame, text="Enter Payment Information:", font=("Helvetica", 16, "bold"))
        payment_label.grid(row=2, column=1, pady=10, sticky = 'e')

        confirm_button = tk.Button(self.ui_frame, text="generate QR-CODE", font=("Arial Baltic", 11, "bold"),
                                   command=self.confirm_payment, width=20, height=3, bg='#E3CF57')
        confirm_button.grid(row=5, column=1,columnspan =2, pady=10)

        cancel_payment = tk.Button(self.ui_frame, text="Cancel Payment", font=("Arial Baltic", 11, "bold"),
                                   command=self.confirm_cancel_payment, width=20, height=3, bg='#EE3B3B')
        cancel_payment.grid(row=6, column=1,columnspan =2, pady=10)

        self.date_time_label = tk.Label(self.ui_frame, text="", font=("Helvetica", 12))
        self.date_time_label.grid(row=7, column=0, columnspan=10, pady=80, sticky='e')
        
        self.update_date_time_label3()
        
        # Load the image using PIL
        img = Image.open('BTS3.png')
        img = img.resize((216, 77), Image.LANCZOS)

        # Convert the PIL Image to a Tkinter PhotoImage
        self.image = ImageTk.PhotoImage(img)

        # Create a label to display the image
        image_label = tk.Label(self.ui_frame, image=self.image)
        image_label.grid(row=8, column=1, columnspan=6, sticky='e', pady=20)
        
        
        self.payment_sound = pygame.mixer.Sound('cash.mp3')
        self.payment_sound.set_volume(0.2)
        
    def update_date_time_label3(self):
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.date_time_label.config(text=current_datetime)

        # Use the 'after' method from a widget to schedule the update
        self.after(1000, self.update_date_time_label3)
        

    def confirm_payment(self):
        # Handle payment logic for PromptPay here
        account_number = "0649319750"  # Replace with the actual account number
        is_one_time = True  # Replace with True or False as needed
        country_code = "TH"
        money_amount = str(self.total_price)  # Use the total price from your PaymentWindow
        currency_code = "THB"

        # Generate the PromptPay QR code data
        qr_code_data = self.generate_promptpay_qr(account_number, is_one_time, country_code, money_amount, currency_code) 

        # # Create a new window to display the QR code
        # qr_code_window = tk.Toplevel(self.window)
        # qr_code_window.geometry("400x400")  # Set the window size as needed
        # qr_code_label = tk.Label(qr_code_window, text="Scan this QR code to make the payment:")
        # qr_code_label.pack()

        # Generate the QR code image using qrcode library
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_code_data)
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        qr_img = qr_img.resize((200, 200), Image.LANCZOS)

            # Convert the PIL Image to a Tkinter PhotoImage
        qr_photo = ImageTk.PhotoImage(qr_img)

        # Create a label to display the QR code image on the payment window
        qr_label = tk.Label(self.ui_frame, image=qr_photo)
        qr_label.photo = qr_photo  # Save a reference to prevent image from being garbage collected
        qr_label.grid(row=3, column=0, columnspan=6, pady=20)
    
    def go_back_to_main(self):
        self.isStopped = True 
        # Assuming that 'self.parent' refers to the main application window
        self.parent.deiconify()  # Show the main window again
        self.parent.update()  # Refresh the main window
        self.parent.focus_force()  # Set focus to the main window

        # Close the payment window
        self.window.destroy()
            
    def confirm_cancel_payment(self):
        # Display a confirmation dialog
        response = tkinter.messagebox.askyesno("Cancel Payment", "Are you sure you want to cancel the payment?")
        if response:
            self.isStopped = True 
            self.destroy()
            # self.payment_frame.destroy()
            # self.go_back_to_main()
            self.parent.parent.restart_program()
            

    def generate_promptpay_qr(self, account, one_time=True, country="TH", money="", currency="THB"):
        # Prepare the PromptPay payload string
        payload = "promptpay://"
        
        # Handle one-time or multi-use code
        if one_time:
            payload += "pay?1"
        else:
            payload += "pay?0"
        
        # Add the receiver's information (phone number or ID)
        if len(account) != 13:
            payload += "&id=" + account
        else:
            payload += "&phone=" + account
        
        # Add the country code
        payload += "&country=" + country
        
        # Add the currency code
        if currency == "THB":
            payload += "&currency=764"
        
        # Add the amount if provided
        if money:
            payload += "&amount=" + money
        
        return payload
    
    # def open(self):
    #     self.create_ui()
    
    def play_payment_sound(self):
        # Play the payment sound effect when the "Pay" button is clicked
        self.payment_sound.play()  # Use .play() to play the sound

class CashPayment(tk.Toplevel):
    def __init__(self, parent, total_price):
        super().__init__(parent)
        self.isStopped = False  
        self.parent = parent
        self.total_price = total_price
        self.selected_payment_method = tk.StringVar(value="Cash")
        self.geometry("1920x1080")
        self.configure(bg = 'seashell3')
        
        self.create_ui()

    def create_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.image_frame = tk.Frame(self)
        self.image_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        path = 'bangkok-map.png'
        self.zoom_advanced = Zoom_Advanced(self.image_frame, path=path)

        self.ui_frame = tk.Frame(self)
        self.ui_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ns")
        self.ui_frame.configure(bg ='seashell1')

        self.name = tk.Label(self.ui_frame, text="BANGKOK MASS RAPID TRANSIT\n TICKET MACHINE", font=("Helvetica", 20, "bold"),fg = 'blue4')
        self.name.grid(row=0, column=0, columnspan=4, pady=(15, 30), sticky='w',padx = 10)
        self.name.configure(bg ='seashell1')

        self.ticket_frame = tk.Frame(self.ui_frame)
        self.ticket_frame.grid(row=1, column=0, columnspan=4, pady=10)
        self.ticket_frame.configure(bg ='seashell1')

        payment_label = tk.Label(self.ui_frame, text="Enter Cash Amount:", font=("Helvetica", 20, "bold"))
        payment_label.grid(row=2, column=1, pady=10, padx = 30, sticky='e')
        payment_label.configure(bg ='seashell1')

        total_label = tk.Label(self.ui_frame, text=f"Total Price: ฿{self.total_price:.2f}", font=("Arial Baltic", 14))
        total_label.grid(row=3, column=1,pady=10,padx = 30)
        total_label.configure(bg ='seashell1')
        
        self.cash_entry = tk.Entry(self.ui_frame, font=("Arial Baltic", 13))
        self.cash_entry.grid(row=4, column=1, pady=10,padx=40)

        confirm_button = tk.Button(self.ui_frame, text="Pay Cash", font=("Arial Baltic", 11, "bold"),
                                   command=self.confirm_payment, width=20, height=3, bg='#E3CF57')
        confirm_button.grid(row=5, column=1, pady=10,padx = 40)

        cancel_payment = tk.Button(self.ui_frame, text="Cancel Payment", font=("Arial Baltic", 11, "bold"),
                                   command=self.confirm_cancel_payment, width=20, height=3, bg='#EE3B3B')
        cancel_payment.grid(row=6, column=1, pady=10,padx = 40)

        self.date_time_label = tk.Label(self.ui_frame, text="", font=("Helvetica", 12))
        self.date_time_label.grid(row=7, column=0, columnspan=10, pady=90, sticky='e')
        self.date_time_label.configure(bg ='seashell1')

        self.update_date_time_label4()

        # Load the image using PIL
        img = Image.open('BTS3.png')
        img = img.resize((216, 77), Image.LANCZOS)

        # Convert the PIL Image to a Tkinter PhotoImage
        self.image = ImageTk.PhotoImage(img)

        # Create a label to display the image
        image_label = tk.Label(self.ui_frame, image=self.image)
        image_label.grid(row=8, column=1, columnspan=6, sticky='e', pady=25)
        image_label.configure(bg ='seashell1')
        
        self.payment_sound = pygame.mixer.Sound('cash.mp3')
        self.payment_sound.set_volume(0.2)

        
    def update_date_time_label4(self):
        if not self.isStopped:
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.date_time_label.config(text=current_datetime)

            self.after(1000, self.update_date_time_label4)

    def confirm_payment(self):
        cash_amount = self.cash_entry.get()
        if not cash_amount:
            tkinter.messagebox.showerror("Error", "Please enter a cash amount.")
        else:
            try:
                cash_amount = float(cash_amount)
                if cash_amount >= self.total_price:
                    self.isStopped = True
                    change = cash_amount - self.total_price
                    tkinter.messagebox.showinfo("Payment Successful", f"Payment successful! Your change: {change:.2f} THB")
                    # self.play_payment_sound()
                    self.parent.parent.restart_program()
                    self.after(1000, self.destroy)
                    # self.parent.parent.deiconify()
                    # self.destroy()
                    # self.go_back_to_main()
                    # self.go_back_to_main()
                else:
                    tkinter.messagebox.showerror("Insufficient Cash", "Insufficient cash amount. Please enter more.")
            except ValueError:
                tkinter.messagebox.showerror("Invalid Amount", "Please enter a valid cash amount.")

    def go_back_to_main(self):
        
        # self.metro_ticket = MetroTicketMachine()
        # self.metro_ticket.__init__()
        # self.metro_ticket.mainloop()
        self.destroy()


    def confirm_cancel_payment(self):
        response = tkinter.messagebox.askyesno("Cancel Payment", "Are you sure you want to cancel the payment?")
        if response:
            self.isStopped = True
            self.focus_set()
            self.destroy()
            self.parent.parent.deiconify()
            self.parent.parent.restart_program()
            # metro_ticket = MetroTicketMachine()
            # metro_ticket.__init__()
            # metro_ticket.mainloop()
            # self.parent.restart_program()
            
    def play_payment_sound(self):
        # Play the payment sound effect when the "Pay" button is clicked
        self.payment_sound.play()  # Use .play() to play the sound

class AutoScrollbar(ttk.Scrollbar):
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
            ttk.Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise tk.TclError('Cannot use pack with this widget')

    def place(self, **kw):
        raise tk.TclError('Cannot use place with this widget')

class Zoom_Advanced(ttk.Frame):
    def __init__(self, mainframe, path):
        
        ttk.Frame.__init__(self, master=mainframe)

        vbar = AutoScrollbar(self.master, orient='vertical')
        hbar = AutoScrollbar(self.master, orient='horizontal')
        vbar.grid(row=0, column=1, sticky='ns')
        hbar.grid(row=1, column=0, sticky='we')

        self.canvas = tk.Canvas(self.master, highlightthickness=0,
                                xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.canvas.grid(row=0, column=0, sticky='nswe')
        self.canvas.update()
        vbar.configure(command=self.scroll_y)
        hbar.configure(command=self.scroll_x)


        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.master.configure(bg='seashell1')

        self.canvas.bind('<Configure>', self.show_image)
        self.canvas.bind('<ButtonPress-1>', self.move_from)
        self.canvas.bind('<B1-Motion>', self.move_to)
        self.canvas.bind('<MouseWheel>', self.wheel)
        self.canvas.bind('<Button-5>', self.wheel)
        self.canvas.bind('<Button-4>', self.wheel)
        
        self.zoom_in_button = tk.Button(self.master, text="Zoom In", command=self.zoom_in, width = 9,bg = '#E3CF57')
        self.zoom_out_button = tk.Button(self.master, text="Zoom Out", command=self.zoom_out, width = 9,bg = '#E3CF57')
        
        self.reset_zoom_button = tk.Button(self.master, text="Reset Zoom", width=9, command=self.reset_zoom, bg = '#E3CF57')

        self.zoom_in_button.grid(row=2, column=0, sticky='e', pady= 5)
        self.zoom_out_button.grid(row=2, column=0, sticky='e',padx = 80, pady= 5)
        self.reset_zoom_button.grid(row=2, column=0, sticky = 'e', padx = 160, pady= 5)
        
        self.image = Image.open(path)
        self.width, self.height = self.image.size
        self.imscale = 1.0
        self.delta = 1.3
        self.max_imscale = 2.5
        self.min_imscale = 0.5
        self.container = self.canvas.create_rectangle(0, 0, self.width, self.height, width=0)

        self.show_image()

    def scroll_y(self, *args, **kwargs):
        self.canvas.yview(*args, **kwargs)
        self.show_image()

    def scroll_x(self, *args, **kwargs):
        self.canvas.xview(*args, **kwargs)
        self.show_image()

    def move_from(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def move_to(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self.show_image()

    def zoom_in(self):
        if self.imscale * self.delta <= self.max_imscale:
            self.imscale *= self.delta
            self.zoom(self.delta)

    def zoom_out(self):
        if self.imscale / self.delta >= self.min_imscale:
            self.imscale /= self.delta
            self.zoom(1.0 / self.delta)

    def zoom(self, scale):
        x = self.canvas.winfo_width() // 2
        y = self.canvas.winfo_height() // 2
        self.canvas.scale('all', x, y, scale, scale)
        self.show_image()
        
    def reset_zoom(self):
    # # Reset the zoom level to the initial value
    #     self.imscale = 1.0
    #     self.canvas.scale('all', 0, 0, 1.0 / self.imscale, 1.0 / self.imscale)
    #     self.show_image()
        self.width, self.height = self.image.size
        self.imscale = 1.0
        self.delta = 1.3
        self.container = self.canvas.create_rectangle(0, 0, self.width, self.height, width=0)
        self.show_image()

    def wheel(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        bbox = self.canvas.bbox(self.container)

        if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]:
            pass
        else:
            return

        scale = 1.0
        if event.num == 5 or event.delta == -120:  # Scroll down (zoom out)
                if self.imscale / self.delta >= self.min_imscale:
                    self.imscale /= self.delta
                    scale /= self.delta
        elif event.num == 4 or event.delta == 120:  # Scroll up (zoom in)
                if self.imscale * self.delta <= self.max_imscale:
                    self.imscale *= self.delta
                    scale *= self.delta

        self.canvas.scale('all', x, y, scale, scale)
        self.show_image()

    def show_image(self, event=None):
        bbox1 = self.canvas.bbox(self.container)
        bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)
        bbox2 = (self.canvas.canvasx(0),
                 self.canvas.canvasy(0),
                 self.canvas.canvasx(self.canvas.winfo_width()),
                 self.canvas.canvasy(self.canvas.winfo_height()))
        bbox = [min(bbox1[0], bbox2[0]), min(bbox1[1], bbox2[1]),
                max(bbox1[2], bbox2[2]), max(bbox1[3], bbox2[3])]

        if bbox[0] == bbox2[0] and bbox[2] == bbox2[2]:
            bbox[0] = bbox1[0]
            bbox[2] = bbox1[2]
        if bbox[1] == bbox2[1] and bbox[3] == bbox2[3]:
            bbox[1] = bbox1[1]
            bbox[3] = bbox1[3]

        self.canvas.configure(scrollregion=bbox)
        # self.canvas.delete("all")
        x1 = max(bbox2[0] - bbox1[0], 0)
        y1 = max(bbox2[1] - bbox1[1], 0)
        x2 = min(bbox2[2], bbox1[2]) - bbox1[0]
        y2 = min(bbox2[3], bbox1[3]) - bbox1[1]

        if int(x2 - x1) > 0 and int(y2 - y1) > 0:
            x = min(int(x2 / self.imscale), self.width)
            y = min(int(y2 / self.imscale), self.height)
            image = self.image.crop((int(x1 / self.imscale), int(y1 / self.imscale), x, y))
            imagetk = ImageTk.PhotoImage(image.resize((int(x2 - x1), int(y2 - y1))))
            imageid = self.canvas.create_image(max(bbox2[0], bbox1[0]), max(bbox2[1], bbox1[1]),
                                               anchor='nw', image=imagetk)
            self.canvas.lower(imageid)
            self.canvas.imagetk = imagetk

if __name__ == "__main__":
    app = MetroTicketMachine()
    app.mainloop()

