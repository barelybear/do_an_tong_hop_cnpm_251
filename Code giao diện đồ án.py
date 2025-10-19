import tkinter as tk

class StaticChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat App Prototype - Static Interface")
        self.root.geometry("1400x800")
        self.root.configure(bg="#f0f2f5")
        
        # Main container
        main_frame = tk.Frame(self.root, bg="#f0f2f5")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar
        sidebar = tk.Frame(main_frame, width=320, bg="white", relief="solid", borderwidth=1)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # Sidebar Header
        header_frame = tk.Frame(sidebar, bg="white")
        header_frame.pack(fill=tk.X, pady=20, padx=20)
        title_label = tk.Label(header_frame, text="Chats", font=("Segoe UI", 24), bg="white", fg="#333")
        title_label.pack(side=tk.LEFT)
        
        icons_frame = tk.Frame(header_frame, bg="white")
        icons_frame.pack(side=tk.RIGHT)
        plus_icon = tk.Label(icons_frame, text="➕", font=("Segoe UI", 20), bg="white", fg="#667eea")
        plus_icon.pack(side=tk.LEFT, padx=(0, 15))
        profile_icon = tk.Label(icons_frame, text="👤", font=("Segoe UI", 20), bg="white", fg="#667eea")
        profile_icon.pack(side=tk.LEFT)
        
        # Tabs
        tabs_frame = tk.Frame(sidebar, bg="white")
        tabs_frame.pack(fill=tk.X, padx=20, pady=(0, 5))
        tab1 = tk.Label(tabs_frame, text="Trò chuyện", font=("Segoe UI", 12, "bold"), bg="white", fg="#667eea")
        tab1.pack(side=tk.LEFT, padx=(0, 10))
        tab2 = tk.Label(tabs_frame, text="Bạn bè", font=("Segoe UI", 12), bg="white", fg="#8e8e93")
        tab2.pack(side=tk.LEFT, padx=10)
        tab3 = tk.Label(tabs_frame, text="Lời mời", font=("Segoe UI", 12), bg="white", fg="#8e8e93")
        tab3.pack(side=tk.LEFT, padx=10)
        
        # Underline for active tab
        active_underline = tk.Frame(tabs_frame, bg="#667eea", height=3)
        active_underline.place(x=10, y=30, width=70, height=3)
        
        # Search Box
        search_frame = tk.Frame(sidebar, bg="#f8f9fa")
        search_frame.pack(fill=tk.X, pady=(15, 0), padx=20)
        search_entry = tk.Entry(search_frame, font=("Segoe UI", 14), fg="#333", bg="#f8f9fa", relief="solid", borderwidth=0, insertwidth=0)
        search_entry.insert(0, "🔍 Tìm kiếm...")
        search_entry.config(fg="#8e8e93")
        search_entry.pack(fill=tk.X, pady=10)
        
        # Chat List - Static frames for each chat item
        chat_items_frame = tk.Frame(sidebar, bg="white")
        chat_items_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0), padx=20)
        
        # Active Chat Item 1: Nguyễn Hoàng (highlighted)
        item1_frame = tk.Frame(chat_items_frame, bg="#e7f3ff", relief="solid", borderwidth=0)
        item1_frame.pack(fill=tk.X, pady=(0, 5))
        # Avatar - circular
        avatar_canvas1 = tk.Canvas(item1_frame, width=50, height=50, bg="#e7f3ff", highlightthickness=0)
        avatar_canvas1.create_oval(2, 2, 48, 48, fill="#667eea", outline="")
        avatar_canvas1.create_text(25, 25, text="NH", fill="white", font=("Segoe UI", 18, "bold"))
        avatar_canvas1.pack(side=tk.LEFT, padx=(5, 12))
        # Info
        info1_frame = tk.Frame(item1_frame, bg="#e7f3ff")
        info1_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        name1 = tk.Label(info1_frame, text="Nguyễn Hoàng", font=("Segoe UI", 15, "bold"), bg="#e7f3ff", fg="#333")
        name1.pack(anchor=tk.W)
        preview1 = tk.Label(info1_frame, text="Dự án của bạn tiến triển...", font=("Segoe UI", 14), fg="#8e8e93", bg="#e7f3ff")
        preview1.pack(anchor=tk.W)
        # Time
        time1 = tk.Label(item1_frame, text="10:32 AM", font=("Segoe UI", 12), fg="#8e8e93", bg="#e7f3ff")
        time1.pack(side=tk.RIGHT, pady=(0, 5))
        
        # Chat Item 2: Phạm Thảo
        item2_frame = tk.Frame(chat_items_frame, bg="white", relief="solid", borderwidth=0)
        item2_frame.pack(fill=tk.X, pady=(0, 5))
        avatar_canvas2 = tk.Canvas(item2_frame, width=50, height=50, bg="white", highlightthickness=0)
        avatar_canvas2.create_oval(2, 2, 48, 48, fill="#667eea", outline="")
        avatar_canvas2.create_text(25, 25, text="PT", fill="white", font=("Segoe UI", 18, "bold"))
        avatar_canvas2.pack(side=tk.LEFT, padx=(5, 12))
        info2_frame = tk.Frame(item2_frame, bg="white")
        info2_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        name2 = tk.Label(info2_frame, text="Phạm Thảo", font=("Segoe UI", 15, "bold"), bg="white", fg="#333")
        name2.pack(anchor=tk.W)
        preview2 = tk.Label(info2_frame, text="Hẹn gặp lại nhé!", font=("Segoe UI", 14), fg="#8e8e93", bg="white")
        preview2.pack(anchor=tk.W)
        time2 = tk.Label(item2_frame, text="Hôm qua", font=("Segoe UI", 12), fg="#8e8e93", bg="white")
        time2.pack(side=tk.RIGHT, pady=(0, 5))
        
        # Chat Item 3: Nhóm Dự Án
        item3_frame = tk.Frame(chat_items_frame, bg="white", relief="solid", borderwidth=0)
        item3_frame.pack(fill=tk.X, pady=(0, 5))
        avatar_canvas3 = tk.Canvas(item3_frame, width=50, height=50, bg="white", highlightthickness=0)
        avatar_canvas3.create_oval(2, 2, 48, 48, fill="#667eea", outline="")
        avatar_canvas3.create_text(25, 25, text="👥", fill="white", font=("Segoe UI", 18, "bold"))
        avatar_canvas3.pack(side=tk.LEFT, padx=(5, 12))
        info3_frame = tk.Frame(item3_frame, bg="white")
        info3_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        name3 = tk.Label(info3_frame, text="Nhóm Dự Án", font=("Segoe UI", 15, "bold"), bg="white", fg="#333")
        name3.pack(anchor=tk.W)
        preview3 = tk.Label(info3_frame, text="Mai họp lúc 9h nhé", font=("Segoe UI", 14), fg="#8e8e93", bg="white")
        preview3.pack(anchor=tk.W)
        time3 = tk.Label(item3_frame, text="Hôm qua", font=("Segoe UI", 12), fg="#8e8e93", bg="white")
        time3.pack(side=tk.RIGHT, pady=(0, 5))
        
        # Chat Item 4: Lê Minh
        item4_frame = tk.Frame(chat_items_frame, bg="white", relief="solid", borderwidth=0)
        item4_frame.pack(fill=tk.X, pady=(0, 5))
        avatar_canvas4 = tk.Canvas(item4_frame, width=50, height=50, bg="white", highlightthickness=0)
        avatar_canvas4.create_oval(2, 2, 48, 48, fill="#667eea", outline="")
        avatar_canvas4.create_text(25, 25, text="LM", fill="white", font=("Segoe UI", 18, "bold"))
        avatar_canvas4.pack(side=tk.LEFT, padx=(5, 12))
        info4_frame = tk.Frame(item4_frame, bg="white")
        info4_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        name4 = tk.Label(info4_frame, text="Lê Minh", font=("Segoe UI", 15, "bold"), bg="white", fg="#333")
        name4.pack(anchor=tk.W)
        preview4 = tk.Label(info4_frame, text="OK bạn!", font=("Segoe UI", 14), fg="#8e8e93", bg="white")
        preview4.pack(anchor=tk.W)
        time4 = tk.Label(item4_frame, text="2 ngày trước", font=("Segoe UI", 12), fg="#8e8e93", bg="white")
        time4.pack(side=tk.RIGHT, pady=(0, 5))
        
        # Main Chat Area
        chat_main = tk.Frame(main_frame, bg="#f7f9fa")
        chat_main.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Chat Header
        chat_header = tk.Frame(chat_main, bg="white", relief="solid", borderwidth=1)
        chat_header.pack(fill=tk.X)
        left_frame = tk.Frame(chat_header, bg="white")
        left_frame.pack(side=tk.LEFT, padx=25, pady=15)
        # Header Avatar
        header_avatar_canvas = tk.Canvas(left_frame, width=50, height=50, bg="white", highlightthickness=0)
        header_avatar_canvas.create_oval(2, 2, 48, 48, fill="#667eea", outline="")
        header_avatar_canvas.create_text(25, 25, text="NH", fill="white", font=("Segoe UI", 18, "bold"))
        header_avatar_canvas.pack(side=tk.LEFT)
        name_frame = tk.Frame(left_frame, bg="white")
        name_frame.pack(side=tk.LEFT, padx=(15, 0))
        name_label = tk.Label(name_frame, text="Nguyễn Hoàng", font=("Segoe UI", 16, "bold"), bg="white", fg="#333")
        name_label.pack(anchor=tk.W)
        status_label = tk.Label(name_frame, text="● Online", font=("Segoe UI", 13), fg="#4cd964", bg="white")
        status_label.pack(anchor=tk.W)
        
        right_frame = tk.Frame(chat_header, bg="white")
        right_frame.pack(side=tk.RIGHT, padx=25, pady=15)
        call_icon = tk.Label(right_frame, text="📞", font=("Segoe UI", 16), bg="white")
        call_icon.pack(side=tk.LEFT, padx=(0, 15))
        video_icon = tk.Label(right_frame, text="📹", font=("Segoe UI", 16), bg="white")
        video_icon.pack(side=tk.LEFT, padx=15)
        more_icon = tk.Label(right_frame, text="⋮", font=("Segoe UI", 16), bg="white")
        more_icon.pack(side=tk.LEFT)
        
        # Messages Area - Static messages
        messages_frame = tk.Frame(chat_main, bg="#f7f9fa")
        messages_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)
        
        # Message 1: Received (left, with avatar)
        msg1_frame = tk.Frame(messages_frame, bg="#f7f9fa")
        msg1_frame.pack(anchor=tk.W, pady=(0, 15))
        # Avatar
        msg_avatar1 = tk.Canvas(msg1_frame, width=40, height=40, bg="#f7f9fa", highlightthickness=0)
        msg_avatar1.create_oval(0, 0, 40, 40, fill="#667eea", outline="")
        msg_avatar1.create_text(20, 20, text="NH", fill="white", font=("Segoe UI", 14, "bold"))
        msg_avatar1.pack(side=tk.LEFT, padx=(0, 10))
        # Bubble
        bubble1 = tk.Label(msg1_frame, text="Chào bạn! Bạn có khỏe không?", bg="white", fg="#333", 
                           relief="flat", borderwidth=0, padx=15, pady=12, font=("Segoe UI", 14), 
                           wraplength=300, justify=tk.LEFT)
        bubble1.pack(side=tk.LEFT, anchor=tk.NW)
        # Time below bubble
        time1 = tk.Label(msg1_frame, text="10:30 AM", font=("Segoe UI", 11), fg="#8e8e93", bg="#f7f9fa")
        time1.place(in_=msg1_frame, x=50, y=bubble1.winfo_reqheight() + 15)
        
        # Message 2: Sent (right, no avatar, blue bubble)
        msg2_frame = tk.Frame(messages_frame, bg="#f7f9fa")
        msg2_frame.pack(anchor=tk.E, pady=(0, 15))
        bubble2 = tk.Label(msg2_frame, text="Chào! Mình khỏe, cảm ơn bạn 😊", bg="#667eea", fg="white", 
                           relief="flat", borderwidth=0, padx=15, pady=12, font=("Segoe UI", 14), 
                           wraplength=300, justify=tk.LEFT)
        bubble2.pack(side=tk.RIGHT, anchor=tk.N)
        time2 = tk.Label(msg2_frame, text="10:31 AM", font=("Segoe UI", 11), fg="#e0e0e0", bg="#f7f9fa")
        time2.place(in_=msg2_frame, x=0, y=bubble2.winfo_reqheight() + 15)
        
        # Message 3: Received (left, with avatar)
        msg3_frame = tk.Frame(messages_frame, bg="#f7f9fa")
        msg3_frame.pack(anchor=tk.W, pady=(0, 15))
        # Avatar
        msg_avatar3 = tk.Canvas(msg3_frame, width=40, height=40, bg="#f7f9fa", highlightthickness=0)
        msg_avatar3.create_oval(0, 0, 40, 40, fill="#667eea", outline="")
        msg_avatar3.create_text(20, 20, text="NH", fill="white", font=("Segoe UI", 14, "bold"))
        msg_avatar3.pack(side=tk.LEFT, padx=(0, 10))
        # Bubble
        bubble3 = tk.Label(msg3_frame, text="Dự án của bạn tiến triển thế nào rồi?", bg="white", fg="#333", 
                           relief="flat", borderwidth=0, padx=15, pady=12, font=("Segoe UI", 14), 
                           wraplength=300, justify=tk.LEFT)
        bubble3.pack(side=tk.LEFT, anchor=tk.NW)
        # Time below bubble
        time3 = tk.Label(msg3_frame, text="10:32 AM", font=("Segoe UI", 11), fg="#8e8e93", bg="#f7f9fa")
        time3.place(in_=msg3_frame, x=50, y=bubble3.winfo_reqheight() + 15)
        
        # Input Area
        input_frame = tk.Frame(chat_main, bg="white", relief="solid", borderwidth=1)
        input_frame.pack(fill=tk.X, padx=25, pady=(0, 20))
        input_inner = tk.Frame(input_frame, bg="white")
        input_inner.pack(pady=20, padx=25, fill=tk.X)
        emoji_icon = tk.Label(input_inner, text="😊", font=("Segoe UI", 16), bg="white")
        emoji_icon.pack(side=tk.LEFT, padx=5)
        attach_icon = tk.Label(input_inner, text="📎", font=("Segoe UI", 16), bg="white")
        attach_icon.pack(side=tk.LEFT, padx=(0, 12))
        # Input placeholder
        input_entry = tk.Entry(input_inner, font=("Segoe UI", 14), fg="#333", bg="#f8f9fa", relief="solid", borderwidth=2, insertwidth=0)
        input_entry.insert(0, "Nhập tin nhắn...")
        input_entry.config(fg="#8e8e93")
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 12))
        # Send button - circular
        send_canvas = tk.Canvas(input_inner, width=44, height=44, bg="white", highlightthickness=0)
        send_canvas.create_oval(2, 2, 42, 42, fill="#667eea", outline="")
        send_canvas.create_text(22, 22, text="➤", fill="white", font=("Segoe UI", 16))
        send_canvas.pack(side=tk.RIGHT)

if __name__ == "__main__":
    root = tk.Tk()
    app = StaticChatApp(root)
    root.mainloop()