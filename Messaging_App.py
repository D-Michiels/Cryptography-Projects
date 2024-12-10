from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.anchorlayout import AnchorLayout
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivy.core.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from socket import *
from hashlib import sha256
import hashlib
import secrets
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from threading import Thread
from kivy.clock import Clock

class ChatScreen(BoxLayout):
    def __init__(self, client_socket, key, iv, **kwargs):
        super(ChatScreen, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.client_socket = client_socket
        self.Key = key
        self.iv = iv
        
        # Scrollable text window to display messages
        self.text_window = ScrollView(size_hint=(1, 0.9), do_scroll_y=False)
        self.text_layout = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        self.text_layout.bind(minimum_height=self.text_layout.setter('height'))  # This line is crucial
        self.text_window.add_widget(self.text_layout)
        
        # Text input to send messages
        self.text_input = TextInput(size_hint=(1, 0.1))

        # Tinted background color
        with self.canvas.before:
            Color(0.5, 0.5, 0.5, 0.5)  # Semi-transparent grey color
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)

        # Button to send messages
        send_button = Button(text='Send', size_hint=(1, None), height=30)
        send_button.bind(on_press=self.send_message)
        
        # Adding widgets to the chat screen
        self.add_widget(self.text_window)
        self.add_widget(self.text_input)
        self.add_widget(send_button)

        # Bind the size and position of the chat screen to update background
        self.bind(size=self.update_bg_position, pos=self.update_bg_position)

    def update_bg_position(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos
    
    def send_message(self, instance):
        message = self.text_input.text
        # Encrypt and send message
        encrypted_message = encrypt(message, self.Key, self.iv)
        self.client_socket.send((encrypted_message.hex()).encode())  # Send as binary
        self.text_input.text = ""  # Clear the text input after sending
        self.add_message(f" (You): {message}",'right', color=(0,0,1,1))  # Blue for sent messages
    
    def add_message(self, message, alignment='left', color=(0, 0, 0, 1), ):
        label = Label(text=message, size_hint_y=None, height=30, halign=alignment, valign='top', color=color)
        label.bind(size=lambda instance, _: instance.setter('text_size')(instance, (self.text_layout.width - 20, None)))
        label.bind(texture_size=lambda instance, _: setattr(instance, 'height', instance.texture_size[1]))
        self.text_layout.add_widget(label)
        self.text_window.scroll_to(label)
        
class LoginScreen(App):
    def build(self):
        root = FloatLayout(size=Window.size)
        self.bg_texture = Image('pic.png').texture
        with root.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(texture=self.bg_texture, size=Window.size, pos=(0, 0))

        Window.bind(on_resize=self.on_window_resize)
        anchor_layout = AnchorLayout(anchor_x='center', anchor_y='center')
        login_box = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint=(None, None), width=300, height=250)
        
        with login_box.canvas.before:
            Color(0.38, 0.553, 0.612, 0.5)
            self.input_box = Rectangle(size=(300, 250), pos=(Window.width / 2 - 150, Window.height / 2 - 125))

        def add_field(caption, password=False):
            layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
            label = Label(text=caption, color=(1, 1, 1, 1))
            input_field = TextInput(multiline=False, password=password, size_hint_x=None, width=175)
            layout.add_widget(label)
            layout.add_widget(input_field)
            login_box.add_widget(layout)
            return input_field

        self.username_input = add_field('Username:')
        self.password_input = add_field('Password:', password=True)
        self.server_ip_input = add_field('Server IP:')
        self.server_port_input = add_field('Server Port:')
        submit_button = Button(text='Login', size_hint_y=None, height=30)
        submit_button.bind(on_press=self.connect)
        login_box.add_widget(submit_button)
        anchor_layout.add_widget(login_box)
        root.add_widget(anchor_layout)
        return root

    def on_window_resize(self, instance, width, height):
        self.bg_rect.size = (width, height)
        self.input_box.pos = (Window.width / 2 - 150, Window.height / 2 - 125)

    def connect(self, instance):
        # Default values
        P = '00:c0:37:c3:75:88:b4:32:98:87:e6:1c:2d:a3:32:4b:1b:a4:b8:1a:63:f9:74:8f:ed:2d:8a:41:0c:2f:c2:1b:12:32:f0:d3:bf:a0:24:27:6c:fd:88:44:81:97:aa:e4:86:a6:3b:fc:a7:b8:bf:77:54:df:b3:27:c7:20:1f:6f:d1:7f:d7:fd:74:15:8b:d3:1c:e7:72:c9:f5:f8:ab:58:45:48:a9:9a:75:9b:5a:2c:05:32:16:2b:7b:62:18:e8:f1:42:bc:e2:c3:0d:77:84:68:9a:48:3e:09:5e:70:16:18:43:79:13:a8:c3:9c:3d:d0:d4:ca:3c:50:0b:88:5f:e3'
        g = 2
        P = int(P.replace(":", ""), 16)

        # Server IP and Port
        server_ip = self.server_ip_input.text
        server_port = int(self.server_port_input.text)

        # Generate the private key (Xb) and public key (Yb)
        rand_num = secrets.randbits(64)
        Xb = sha256(f"{self.username_input.text}:{self.password_input.text}:{rand_num}".encode('utf-8')).digest()
        Xb = int.from_bytes(Xb, 'big')
        Yb = hex(pow(g, Xb, P))[2:]

        # Create a socket and connect to the server
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((server_ip, server_port))

        # Send public key (Yb) to server
        client_socket.sendall(Yb.encode('utf-8'))

        # Receive public key (Ya) from server
        Ya = client_socket.recv(4096).decode('utf-8')
        Ya = int(Ya, 16)

        # Compute session key and IV
        K = str(pow(Ya, Xb, P))
        Key = sha256(K.encode('utf-8')).hexdigest()
        md5_IV = hashlib.md5(K.encode('utf-8')).hexdigest()

        # Send Session Key + IV
        client_socket.sendall(sha256((Key + md5_IV).encode('utf-8')).hexdigest().encode('utf-8'))

        # Wait for server response (Acknowledgement)
        server_response = client_socket.recv(4096).decode('utf-8')
        print(server_response)

        # Convert Key and IV for AES
        self.Key = bytes.fromhex(Key)
        self.iv = bytes.fromhex(md5_IV)

        # Switch to the chat screen
        chat_screen = ChatScreen(client_socket, self.Key, self.iv)
        self.root.clear_widgets()
        self.root.add_widget(chat_screen)

        # Start sending and receiving messages
        receive_thread = Thread(target=self.receive_messages, args=(client_socket,))
        send_thread = Thread(target=self.send_messages, args=(client_socket,))
        receive_thread.start()
        send_thread.start()

    def send_messages(self, client_socket):
        s = socket(AF_INET,SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = (s.getsockname()[0])
        s.close()
        while True:
            try:
                message = input("\nEnter message to send:")
                message = str(local_ip) +"|" + message
                encrypted_message = encrypt(message, self.Key, self.iv)
                client_socket.send(((encrypted_message.hex()[2:])).encode())  # Send as binary
            except Exception as e:
                print(f"Failed to send message: {e}")
                break

    def receive_messages(self, client_socket):
        chat_screen = self.root.children[0]  # Assuming chat screen is the first child of the root widget
        while True:
            data = client_socket.recv(4096).decode('utf-8')
            if not data:
                print("Server closed the connection.")
                break
            message = decrypt(data, self.Key, self.iv)
            # Schedule message addition in the main thread
            Clock.schedule_once(lambda dt: chat_screen.add_message(f"Server: {message}", color=(0, 1, 0, 1)))  # Received message in green

def encrypt(plainText, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    cipherText = cipher.encrypt(pad(plainText.encode(), AES.block_size))
    return cipherText

def decrypt(cipherText, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plainText = unpad(cipher.decrypt(bytes.fromhex(cipherText)), AES.block_size).decode()
    return plainText

if __name__ == '__main__':
    LoginScreen().run()
